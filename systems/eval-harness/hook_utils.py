#!/usr/bin/env python3
"""
Shared helpers for .claude/hooks/*.py eval-harness hooks.

Extracted so the turn-level lifecycle hooks (eval-turn-start.py, eval-turn-stop.py)
and the existing subagent-level hooks (eval-agent-start.py, eval-agent-stop.py,
post-tool-use.py, step-complete.py) don't each carry their own copy of the same
atomic-write / session-id / eval-record-lookup logic. Existing hooks keep their
own inlined copies (they predate this module and work) — new hooks import from
here.
"""

import json
import re
import sys
import secrets
import string
import fcntl
from pathlib import Path
from datetime import datetime, timezone

# systems/eval-harness/hook_utils.py -> parents[2] is IES root
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SESSION_INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
WORKFLOWS_DIR = IES_ROOT / "workflows"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

_WORKFLOW_PATH_RE = re.compile(r"workflows/([a-z0-9_-]+)/workflow\.md", re.IGNORECASE)


def extract_workflow_path_reference(text: str, must_exist: bool = True) -> str | None:
    """Find an explicit `workflows/{name}/workflow.md` reference in `text`
    and return `{name}`, or None. Shared by eval-turn-start.py's
    detect_workflow() (matching against `agent: master` workflows a
    controller prompt might invoke) and eval-agent-start.py (matching
    against ANY workflow a subagent's spawn prompt names, e.g. Master
    dispatching Knox with "run workflows/plaud-ingest/workflow.md in
    full" — plaud-ingest is Knox-owned, not master-owned, so this can't
    reuse detect_workflow()'s master-only filtering, just the underlying
    path-extraction it also needs). Deliberately just the path-reference
    check — the run-verb/trigger-phrase/first-clause heuristics in
    detect_workflow() are about inferring intent from a short controller
    message and don't apply to a spawn prompt, which either names an
    explicit workflow.md path or it doesn't.

    `must_exist=True` (default) validates the matched name against a real
    directory under workflows/ so a typo or a reference to some other
    repo's `workflows/x/workflow.md` in quoted text doesn't false-match.
    """
    if not text:
        return None
    m = _WORKFLOW_PATH_RE.search(text.lower())
    if not m:
        return None
    name = m.group(1)
    if must_exist and not (WORKFLOWS_DIR / name / "workflow.md").is_file():
        return None
    return name


def log_error(msg: str, tag: str = "HOOK"):
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{tag}] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str, tag: str = "HOOK"):
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{tag}] [INFO] {msg}\n")
    except Exception:
        pass


def atomic_write_json(path: Path, data: dict):
    """Write JSON atomically using a temp file + rename, with exclusive lock."""
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        tmp_path.replace(path)
    except Exception as e:
        log_error(f"atomic_write_json failed for {path}: {e}")
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def read_stdin() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}


def new_eval_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def _read_session_index() -> list:
    """Read memory/sessions/index.json with a short retry-on-parse-failure
    window. boot's own Session Index step (workflow.md's personal block —
    not something this module can change) appends a new record via a plain
    read-modify-write on the whole file, not the atomic temp+rename pattern
    this module uses for its own writes. A hook read landing mid-write can
    briefly see a truncated/partial file and raise JSONDecodeError even
    though the file is not really missing or corrupt — retrying a couple
    times a few dozen ms apart is enough to ride out that window rather
    than falling through to infer_session_id()'s exception-handler fallback,
    which mints a brand-new, disconnected session id (root cause of
    eval-20260827T161845-1TYTWV: an orphaned turn-level record whose
    session_id never matched the real session's because this exact race
    was hit once)."""
    import time
    last_err = None
    for attempt in range(3):
        try:
            if not SESSION_INDEX_PATH.exists():
                return []
            with open(SESSION_INDEX_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            last_err = e
            if attempt < 2:
                time.sleep(0.08)
    if last_err:
        raise last_err
    return []


def harness_session_id(payload: dict | None) -> str | None:
    """The real Claude Code session_id, straight from the hook's own stdin
    payload. Every hook event (UserPromptSubmit, PreToolUse, PostToolUse,
    SubagentStart, SubagentStop, SessionStart, SessionEnd, Stop) carries
    `session_id` as a documented, guaranteed-present, stable-for-the-
    session field — it's assigned once at session start and never
    regenerated; `transcript_path` on the same payload points at
    `<session_id>.jsonl`, confirming it's the same value all session long.
    This is the authoritative source — prefer it over anything inferred
    from memory/sessions/index.json, which is IES's own bookkeeping file,
    written asynchronously by boot's Session Index step mid-run, and is
    exactly the race that produced eval-20260828T135817-P00Y9T's stale
    session_id (opened before that step had appended today's entry) and
    the P00Y9T/WL89IY split (two hooks reading two different fields of
    that file — see below)."""
    if payload:
        sid = payload.get("session_id")
        if sid:
            return sid
    return None


def infer_session_id(payload: dict | None = None) -> str:
    """Return the current session's id. Pass the hook's own parsed stdin
    `payload` whenever the calling hook has one (every hook triggered by a
    Claude Code event does) — this returns the harness-native session_id
    directly, with no file I/O and no race.

    Falls back to memory/sessions/index.json only for callers with no
    payload at all (standalone CLI scripts invoked directly by a workflow
    step, e.g. close-eval-record.py — not a hook). That fallback prefers
    the `id` field (the same field post-tool-use.py's get_session_id() and
    close-eval-record.py's current_session_id() already read) over
    `started`. Historical note: an earlier version of this function
    claimed memory/sessions/index.json's entries "never" carry an `id`
    field — false as of this fix; recent entries (e.g.
    session-2026-08-28T085856) do have one. Reading `started` instead of
    `id` here, while post-tool-use.py read `id`, is exactly what made
    P00Y9T (this function's old behavior) and WL89IY (post-tool-use.py's
    create_eval_record_from_state path) disagree on session_id for the
    same real session and end up as two unlinked records instead of one."""
    sid = harness_session_id(payload)
    if sid:
        return sid

    try:
        index = _read_session_index()

        if index:
            last_entry = index[-1]
            last = last_entry.get("id") or last_entry.get("started", "")
            if last:
                return last

        now = datetime.now(timezone.utc)
        session_id = now.isoformat().replace("+00:00", "Z")
        new_session = {
            "started": session_id,
            "closed": None,
            "current_topic": None,
            "topics": []
        }
        index.append(new_session)
        SESSION_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(SESSION_INDEX_PATH, index)
        log_info(f"Created session {session_id} for eval tracking")
        return session_id
    except Exception as e:
        log_error(f"Failed to infer or create session ID: {e}")
        now = datetime.now(timezone.utc)
        return f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"


def find_records_for_session(session_id: str) -> list[Path]:
    """All eval-*.json files whose session_id matches, newest first."""
    if not session_id or not EVAL_RUNS_DIR.exists():
        return []
    records = []
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if data.get("session_id") == session_id:
                records.append((f, data.get("started", "")))
        except Exception:
            continue
    records.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in records]


def find_open_turn_records(session_id: str) -> list:
    """All in-progress, monitoring.active turn-level records for this
    session — identified by monitoring.active being true, not just by
    session_id + status (a subagent-level stub from eval-agent-start.py can
    also be in-progress under the same session_id)."""
    out = []
    for f in find_records_for_session(session_id):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if data.get("status") == "in-progress" and data.get("monitoring", {}).get("active"):
                out.append(f)
        except Exception:
            continue
    return out


def find_open_turn_record(session_id: str) -> Path | None:
    """Most-recent single open turn-level record for this session, or None.
    Used by eval-turn-stop.py, where checking every open record it can find
    (via the sweep in that hook) makes ambiguity harmless. NOT used for
    subagent linking — see find_unambiguous_open_turn_record for why."""
    records = find_open_turn_records(session_id)
    return records[0] if records else None


def find_unambiguous_open_turn_record(session_id: str) -> Path | None:
    """Like find_open_turn_record, but returns None if there is more than
    one candidate. Used specifically for linking a freshly-spawned subagent
    into an open turn-level record (eval-agent-start.py/eval-agent-stop.py).

    Root cause of a real incident: a Rigby capability-build subagent
    (unrelated to boot) got linked into a spurious, coincidentally-open
    'boot' turn-level record (itself caused by a detect_workflow
    false-positive, fixed separately in eval-turn-start.py) purely because
    find_open_turn_record returned *a* match for the session_id, without
    checking whether that match was the ONLY plausible workflow the
    subagent could belong to. There's no reliable way from a bare
    SubagentStart payload to know which specific workflow a spawn belongs
    to when more than one turn-level record is open in the same session —
    guessing (picking the most recent) is exactly what produced the
    misattribution. When ambiguous, skip linking rather than guess: the
    subagent's own standalone eval-agent record is unaffected either way,
    this only controls whether it ALSO gets rolled into a workflow's
    subagents[] array."""
    records = find_open_turn_records(session_id)
    return records[0] if len(records) == 1 else None

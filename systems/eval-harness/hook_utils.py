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


def infer_session_id() -> str:
    """Read current session ID from memory/sessions/index.json, creating a
    session record if none exists yet so no eval record is ever orphaned.
    Mirrors eval-agent-start.py's infer_session_id — kept in sync by hand
    since that hook predates this module."""
    try:
        index = _read_session_index()

        if index:
            # memory/sessions/index.json's real schema is
            # {started, closed, current_topic, topics} — there has never
            # been an "id" field (42 real records on disk, none have one).
            # "started" is already a unique-enough key per session record;
            # do not add an "id" field just to work around this.
            last = index[-1].get("started", "")
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

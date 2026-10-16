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
HARNESS_SESSION_PATH = SESSION_INDEX_PATH.parent / "harness-session.json"
WORKFLOWS_DIR = IES_ROOT / "workflows"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

# How long a noted harness session id stays authoritative for CLI scripts
# (close-eval-record.py) that have no hook payload of their own. Long enough
# to cover any realistic session, short enough that a stale note from a
# previous Claude Code session isn't picked up by a later Cowork session
# (where SessionStart never fires) running the next day.
HARNESS_SESSION_MAX_AGE_HOURS = 12

_WORKFLOW_PATH_RE = re.compile(r"workflows/([a-z0-9_-]+)/workflow\.md", re.IGNORECASE)

# --- Agent attribution (Stage 3 Phase 0) ---------------------------------
# Import the canonical roster/mapping from step_audit (single source of truth,
# no duplicated list). Guarded so a broken import degrades to "no mapping"
# rather than taking down every hook that imports this module.
try:
    from step_audit import (  # noqa: E402
        MANIFEST_AGENTS, AGENT_LABEL_ALIASES, normalize_agent_label,
        workflow_owner_agent,
    )
except Exception:  # pragma: no cover - defensive
    MANIFEST_AGENTS = ()
    AGENT_LABEL_ALIASES = {}
    normalize_agent_label = None
    workflow_owner_agent = None

# Every name that can appear in a spawn prompt: canonical manifest names plus
# their raw aliases ("jarvis" → master), de-duplicated, order preserved.
_AGENT_NAME_CANDIDATES = tuple(
    dict.fromkeys(list(MANIFEST_AGENTS) + list(AGENT_LABEL_ALIASES))
)

# Agent names that are ordinary English words ("master", "chief", "chase").
# A bare mention of these is not trustworthy — the name must appear in an
# explicit spawn context before it counts as an attribution signal.
_AMBIGUOUS_AGENT_WORDS = {"master", "chief", "chase"}

# Phrases that mark "the next agent name is who this subagent is": e.g.
# "spawn Ralph with ...", "You are Knox", "dispatch to Chief", "Agent: Shep".
_AGENT_SPAWN_CUE_RE = re.compile(
    r"(?:you are|you're|spawn(?:ing)?|dispatch(?:ing)?|route(?:d)? to|"
    r"hand(?:ing)? (?:this |it |off )?to|activate|agent\s*[:\-])\s*"
    r"(?:the\s+)?([a-z]+)\b",
    re.IGNORECASE,
)


def resolve_agent_from_text(text: str) -> str | None:
    """Best-effort IES agent named in a block of text (a subagent spawn prompt,
    a description, etc.).

    Unambiguous proper-noun agent names (knox, rigby, quinn, shep, sterling,
    galen, harper, ralph; plus the system-name alias jarvis) are matched on any whole-word occurrence and
    scored by count. Ambiguous names that double as English words (master,
    chief, chase) only count when they follow an explicit spawn cue
    ("spawn Chase", "You are Chief", "Agent: Master"), so prose like "chase
    down the invoice" or "the master file" never mis-attributes. Returns the
    canonical manifest name, or None."""
    if not text or normalize_agent_label is None:
        return None

    low = text.lower()
    scores: dict[str, int] = {}
    first_pos: dict[str, int] = {}

    for name in _AGENT_NAME_CANDIDATES:
        m = re.search(rf"\b{re.escape(name)}\b", low)
        if not m:
            continue
        if name in _AMBIGUOUS_AGENT_WORDS:
            # Count only cue-anchored occurrences.
            count = sum(
                1 for cue in _AGENT_SPAWN_CUE_RE.finditer(low)
                if cue.group(1).lower() == name
            )
            if count == 0:
                continue
            pos = m.start()
        else:
            count = len(re.findall(rf"\b{re.escape(name)}\b", low))
            pos = m.start()
        scores[name] = count
        first_pos[name] = pos

    if not scores:
        return None
    # Highest mention count wins; ties break on earliest appearance.
    best = max(scores, key=lambda n: (scores[n], -first_pos[n]))
    return normalize_agent_label(best)


# --- Spawn-text recovery (Stage 3 Phase 3 attribution fix) -----------------
# The SubagentStart hook payload carries NO prompt text. Verified 2026-10-16
# against a live capture: its keys are exactly
#   session_id, transcript_path, cwd, prompt_id, agent_id, agent_type,
#   hook_event_name
# The Phase 0 detector looped over payload.get("prompt"/"task"/"description"/
# "message"/"initial_prompt") — none of which exist — so every spawned
# specialist landed as `agent: general-purpose`, `workflow: null`,
# `owning_agent: null` (the six 2026-10-16 runs). Recover the spawn text from
# the places Claude Code DOES persist it instead.

# Root of Claude Code's per-project session/transcript storage.
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

# A spawn prompt almost always opens "You are <Agent> ...". That opener is a
# stronger signal than resolve_agent_from_text's mention-count, so it is
# checked first (a prompt that opens "You are Harper" but mentions "Knox"
# twice in its body should still resolve to Harper).
_SPAWN_OPENER_RE = re.compile(r"you\s+are\s+(?:the\s+)?([a-z]+)\b", re.IGNORECASE)


def resolve_spawn_agent_from_prompt(text: str) -> str | None:
    """Canonical IES agent for a spawn prompt: prefer a leading
    'You are <Agent>' opener, else fall back to resolve_agent_from_text's
    cue/count logic. Returns a canonical manifest name, or None."""
    if not text or normalize_agent_label is None:
        return None
    m = _SPAWN_OPENER_RE.search(text[:300])
    if m:
        cand = normalize_agent_label(m.group(1))
        if cand:
            return cand
    return resolve_agent_from_text(text)


def _read_first_user_message_text(transcript_path) -> str | None:
    """Text of the first user message in a Claude Code JSONL transcript, or
    None. For a subagent transcript that first message IS the spawn prompt
    ("You are Shep, ..."). Best-effort: any failure returns None."""
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return None
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") != "user":
                    continue
                content = (rec.get("message") or {}).get("content")
                if isinstance(content, str) and content.strip():
                    return content
                if isinstance(content, list):
                    parts = [b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text"]
                    text = "\n".join(p for p in parts if p).strip()
                    if text:
                        return text
    except Exception:
        return None
    return None


def agent_from_transcript(transcript_path) -> str | None:
    """Canonical IES agent named in a transcript's first user message (the
    spawn prompt). Best-effort: unresolvable/missing path -> None, no crash."""
    return resolve_spawn_agent_from_prompt(_read_first_user_message_text(transcript_path))


def _subagent_dir_from_payload(payload: dict):
    """Directory holding this subagent's own transcript + meta, derived from
    the parent transcript_path the SubagentStart hook is given:
    <proj>/<session_id>.jsonl  ->  <proj>/<session_id>/subagents/."""
    tp = (payload or {}).get("transcript_path")
    if not tp:
        return None
    p = Path(tp)
    return p.parent / p.stem / "subagents"


def read_subagent_meta(payload: dict) -> dict:
    """The subagent's .meta.json (Claude Code writes agentType, description,
    toolUseId, ...) for this agent_id, or {} when absent/unreadable."""
    try:
        d = _subagent_dir_from_payload(payload)
        aid = (payload or {}).get("agent_id")
        if d and aid:
            mp = d / f"agent-{aid}.meta.json"
            if mp.is_file():
                with open(mp) as f:
                    return json.load(f)
    except Exception:
        pass
    return {}


def _agent_tool_prompt_by_id(transcript_path, tool_use_id) -> str | None:
    """input.prompt of the Agent tool_use with this exact id, from a parent
    transcript. This is the exact-match path (the subagent's meta.json records
    the toolUseId of the Agent call that spawned it)."""
    if not transcript_path or not tool_use_id:
        return None
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return None
        with open(p, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                content = (rec.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for b in content:
                    if (isinstance(b, dict) and b.get("type") == "tool_use"
                            and b.get("id") == tool_use_id):
                        return (b.get("input") or {}).get("prompt")
    except Exception:
        return None
    return None


def _most_recent_agent_tool_prompt(transcript_path) -> str | None:
    """input.prompt of the LAST Agent tool_use in a transcript.

    NOT used for attribution. Verified unreliable on 2026-10-16: the
    SubagentStart payload's transcript_path is the MAIN session transcript, so
    for a nested spawn (a subagent spawning a sub-subagent) the spawn's own
    Agent tool_use isn't there at all, and for parallel top-level spawns the
    "last" Agent tool_use is whichever was written last, not necessarily this
    one. A live probe spawned with "You are Knox" was mis-resolved to the
    previous spawn's agent ("rigby") through exactly this path. Kept only as a
    documented dead end; write-side attribution now defers to
    eval-agent-stop.py, which reads the subagent's OWN transcript (exact)."""
    if not transcript_path:
        return None
    last = None
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return None
        with open(p, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                content = (rec.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for b in content:
                    if (isinstance(b, dict) and b.get("type") == "tool_use"
                            and b.get("name") == "Agent"):
                        pr = (b.get("input") or {}).get("prompt")
                        if pr:
                            last = pr
    except Exception:
        return None
    return last


def resolve_spawn_text(payload: dict) -> str | None:
    """Best available spawn text for a SubagentStart payload.

    Order: explicit payload text fields (forward-compat, in case Claude Code
    later adds one) -> the parent transcript's Agent tool_use prompt, matched
    EXACTLY by the meta.json toolUseId -> the subagent's own transcript first
    user message -> the .meta.json description. Returns None when nothing is
    recoverable.

    Deliberately does NOT fall back to "the most recent Agent tool_use" (see
    _most_recent_agent_tool_prompt): that heuristic mis-attributes parallel and
    nested spawns. At SubagentStart time the .meta.json is usually not yet
    written (verified 2026-10-16) and the subagent's own transcript does not
    exist yet, so this returns None for most current spawns — which is correct:
    the record is left as the raw subagent type and eval-agent-stop.py
    attributes it authoritatively from the subagent's own transcript at close."""
    if not isinstance(payload, dict):
        return None
    for key in ("prompt", "task", "description", "message", "initial_prompt"):
        t = payload.get(key)
        if isinstance(t, str) and t.strip():
            return t
    meta = read_subagent_meta(payload)
    tp = payload.get("transcript_path")
    if tp and meta.get("toolUseId"):
        prompt = _agent_tool_prompt_by_id(tp, meta["toolUseId"])
        if prompt:
            return prompt
    d = _subagent_dir_from_payload(payload)
    aid = payload.get("agent_id")
    if d and aid:
        own = _read_first_user_message_text(d / f"agent-{aid}.jsonl")
        if own:
            return own
    if meta.get("description"):
        return meta["description"]
    return None


def agent_from_meta(agent_id) -> str | None:
    """Canonical IES agent for a bare agent_id (no transcript path on hand):
    locate its transcript / .meta.json under ~/.claude/projects and mine them.
    Read-side fallback for records that stored agent_id but not
    agent_transcript_path. Best-effort: None on anything unresolvable."""
    if not agent_id:
        return None
    try:
        for tpath in CLAUDE_PROJECTS_DIR.glob(f"*/*/subagents/agent-{agent_id}.jsonl"):
            a = agent_from_transcript(tpath)
            if a:
                return a
        for mpath in CLAUDE_PROJECTS_DIR.glob(f"*/*/subagents/agent-{agent_id}.meta.json"):
            with open(mpath) as f:
                desc = json.load(f).get("description")
            a = resolve_spawn_agent_from_prompt(desc)
            if a:
                return a
    except Exception:
        return None
    return None


def transcript_indicates_completion(transcript_path) -> bool | None:
    """Best-effort completion evidence from a subagent transcript.

    True when the agent explicitly handed back (a SubagentHandback tool_use)
    or its final assistant turn carried text; None when there is no transcript
    to read. Used by eval-agent-stop.py when the SubagentStop payload has no
    last_assistant_message and no steps were recorded — the case that
    mislabeled six verifiably-complete 2026-10-16 runs as `aborted`."""
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return None
        last_assistant_text = False
        handed_back = False
        saw_assistant = False
        with open(p, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") != "assistant":
                    continue
                saw_assistant = True
                content = (rec.get("message") or {}).get("content")
                if isinstance(content, str):
                    last_assistant_text = bool(content.strip())
                elif isinstance(content, list):
                    last_assistant_text = any(
                        isinstance(b, dict) and b.get("type") == "text"
                        and (b.get("text") or "").strip()
                        for b in content
                    )
                    for b in content:
                        if (isinstance(b, dict) and b.get("type") == "tool_use"
                                and b.get("name") == "SubagentHandback"):
                            handed_back = True
        if not saw_assistant:
            return None
        return handed_back or last_assistant_text
    except Exception:
        return None


def detect_spawn_agent(payload: dict, workflow_name: str | None = None) -> str | None:
    """Resolve the IES agent behind a SubagentStart payload.

    Priority:
      1. the owner of the workflow the spawn prompt names (authoritative:
         workflows/<name>/workflow.md's `agent:` frontmatter — e.g.
         boot-verification -> ralph, plaud-ingest -> knox)
      2. an agent name named in the recovered spawn text (resolve_spawn_text)
    Returns a canonical manifest agent name, or None."""
    if normalize_agent_label is None:
        return None
    if workflow_name and workflow_owner_agent:
        owner = normalize_agent_label(workflow_owner_agent(workflow_name))
        if owner:
            return owner
    text = resolve_spawn_text(payload)
    if text:
        return resolve_spawn_agent_from_prompt(text)
    return None


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


def note_harness_session(payload: dict | None):
    """Record the harness-native session id for this session so that
    payload-less CLI scripts (close-eval-record.py, invoked by workflow
    final steps via Bash) can resolve the SAME session id the hooks are
    writing records under.

    Root cause this closes: memory/sessions/index.json entries carry an
    IES-generated id flavor (e.g. "session-2026-09-18-115915", written by
    boot's Session Index step mid-run and possibly hours stale), while
    hooks key records on the payload's harness id (e.g. a UUID). The same
    logical session ended up with eval records under both flavors, and
    session-scoped dedupe (post-tool-use.py GUARD 1) missed across flavors —
    that gap let the 2026-09-18 daily-review phantom slip past the guard
    while its authoritative sibling existed under the other flavor."""
    sid = harness_session_id(payload)
    if not sid:
        return
    try:
        HARNESS_SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(HARNESS_SESSION_PATH, {
            "session_id": sid,
            "noted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        })
    except Exception as e:
        log_error(f"note_harness_session failed: {e}")


def current_harness_session_id(max_age_hours: float = HARNESS_SESSION_MAX_AGE_HOURS) -> str | None:
    """The harness-native session id noted by the SessionStart hook, if the
    note is fresh (within max_age_hours). Returns None when absent, unreadable,
    or stale — callers fall back to the sessions-index id flavor in that case."""
    try:
        if not HARNESS_SESSION_PATH.exists():
            return None
        with open(HARNESS_SESSION_PATH, "r") as f:
            data = json.load(f)
        sid = data.get("session_id")
        noted_at = data.get("noted_at")
        if not sid or not noted_at:
            return None
        dt = datetime.fromisoformat(str(noted_at).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
        if age_hours > max_age_hours:
            return None
        return sid
    except Exception:
        return None


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

    # No payload (standalone CLI caller, e.g. close-eval-record.py). Prefer
    # the harness session id noted by the SessionStart hook so CLI-written
    # records land under the same session id flavor as hook-written ones;
    # the sessions-index `id` flavor is the fallback, not the source.
    noted = current_harness_session_id()
    if noted:
        return noted

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


def open_turn_level_record_exists(workflow_name: str) -> bool:
    """Is there already an open (in-progress, monitoring.active) turn-level
    'workflow' record for this workflow name, anywhere in the runs dir?

    Deliberately NOT scoped to session_id — see eval-turn-start.py's
    already_open_for_workflow (this function's original home) for the full
    rationale: session_id can legitimately take on two different, both-valid
    values within one logical run (boot's own Session Index step appends a
    new entry partway through step-01), so scoping to session_id can miss a
    real duplicate. workflow_name + monitoring.active is the reliable dedup
    key: workflows/{name}/state.yaml is a single file, so there is never a
    legitimate reason for two simultaneously in-progress turn-level records
    against the same workflow name.

    Shared by two call sites that both need this same check:
    - eval-turn-start.py, before opening a new turn-level record on
      UserPromptSubmit (the original use).
    - post-tool-use.py's create_eval_record_from_state(), before writing a
      completed "cowork path" record on a state.yaml PostToolUse write. Root
      cause of eval-20260828T160656-FE6XZW: that function's own guard
      (find_completed_eval_record) only checked for an already-*completed*
      duplicate, not a still-open real turn-level record for the same
      workflow — so when eval-turn-start.py's genuine in-progress record
      (eval-20260828T154249-UQX5N6) hadn't finalized yet (its Stop hook fired
      14 seconds *after* this Cowork path ran), the guard saw nothing to
      dedupe against and wrote a duplicate. Checking this function too closes
      that gap: if a real turn-level record for this workflow is still open,
      the Cowork path backs off and lets eval-turn-stop.py finalize it
      properly instead of racing it with a second, phantom "completed"
      record.
    """
    if not EVAL_RUNS_DIR.exists():
        return False
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if (
                data.get("type") == "workflow"
                and data.get("name") == workflow_name
                and data.get("status") == "in-progress"
                and data.get("monitoring", {}).get("active")
            ):
                return True
        except Exception:
            continue
    return False


def find_parent_record_with_subagent(session_id: str, agent_id: str) -> Path | None:
    """Find the turn-level record (open OR already closed) whose subagents[]
    array contains an entry for this agent_id, searched across every eval
    record for the session — not just the currently-open ones.

    Used by eval-agent-stop.py's rollup write, instead of re-deriving "the"
    open turn record at Stop time. eval-agent-start.py already decided which
    parent (if any) this specific agent_id belongs to, at link time, by
    writing a subagents[] entry keyed on agent_id into exactly one parent
    record. Re-deriving "the open turn record" at Stop time is a second,
    independent guess that can disagree with the first: if the parent's own
    Stop hook (eval-turn-stop.py) fires and closes the parent (flips
    monitoring.active to false / status away from in-progress) before this
    subagent's own SubagentStop hook runs — a real race, since hooks are
    separate async processes with no ordering guarantee across agents that
    finish close together — find_unambiguous_open_turn_record would find
    zero open records and silently drop the rollup, permanently losing that
    subagent's token/cost data (root cause of eval-20260828T154249-UQX5N6's
    a2d85012d16ba3d83 entry landing with tokens_input/output/cost_usd/model
    all null). Looking up the parent by "does its subagents[] already name
    this agent_id" instead of by "is a turn record open right now" removes
    that race entirely — the parent's open/closed status no longer matters."""
    if not agent_id:
        return None
    for f in find_records_for_session(session_id):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if any(s.get("agent_id") == agent_id for s in data.get("subagents", [])):
                return f
        except Exception:
            continue
    return None

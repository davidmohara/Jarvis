#!/usr/bin/env python3
"""
SubagentStart Hook: Eval Record Stub Creation
Triggered when any sub-agent spawns.
Creates an eval record stub with agent_id, agent_type, and started timestamp.
"""

import json
import sys
import secrets
import string
import fcntl
from pathlib import Path
from datetime import datetime, timezone

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
try:
    from hook_utils import (
        find_unambiguous_open_turn_record, _read_session_index,
        extract_workflow_path_reference, infer_session_id as _shared_infer_session_id,
    )
except Exception:
    find_unambiguous_open_turn_record = None
    _read_session_index = None
    extract_workflow_path_reference = None  # 36 chars, ~2.1B combos
    _shared_infer_session_id = None

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str):
    """Log informational message to /tmp/ies-hook-errors.log."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [INFO] {msg}\n")
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
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}

def new_eval_id() -> str:
    """Generate a unique eval ID in the format eval-YYYYMMDDTHHMMSS-XXXXXX."""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"

def infer_session_id(payload: dict | None = None) -> str:
    """Prefer the harness-native `session_id` straight off this hook's own
    stdin payload (SubagentStart carries it, per Claude Code's documented
    hook schema — guaranteed present, stable for the whole session, no
    file I/O, no race). Delegates to hook_utils.infer_session_id, which
    also holds the memory/sessions/index.json fallback for the case this
    module's import failed.

    This used to be a local, hand-maintained copy of the memory-index
    inference (kept "in sync by hand" with hook_utils.py's version per the
    old docstring) that read the `started` field. hook_utils.py's fallback
    reads `id` instead (to agree with post-tool-use.py's get_session_id())
    — the two disagreeing was the direct cause of eval-20260828T135817-
    P00Y9T and eval-20260828T140308-WL89IY (both "boot" workflow records
    for the same real session, opened by two different hooks that
    inferred two different session_id strings for it). Now there's one
    implementation, and — for any hook with a payload — no inference at
    all, just the value Claude Code already gave us."""
    if _shared_infer_session_id:
        try:
            return _shared_infer_session_id(payload)
        except Exception as e:
            log_error(f"shared infer_session_id failed, falling back: {e}")

    if payload:
        sid = payload.get("session_id")
        if sid:
            return sid

    try:
        index_path = IES_ROOT / "memory" / "sessions" / "index.json"
        if _read_session_index:
            index = _read_session_index()
        else:
            index = []
            if index_path.exists():
                with open(index_path, "r") as f:
                    index = json.load(f)

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

        index_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = index_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(index, f, indent=2)
        tmp_path.replace(index_path)

        log_info(f"Created session {session_id} for eval tracking")
        return session_id

    except Exception as e:
        log_error(f"Failed to infer or create session ID: {e}")
        now = datetime.now(timezone.utc)
        return f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"

def infer_workflow_or_skill_name(agent_type: str) -> tuple:
    """Infer whether this is a workflow or skill and the name from agent_type.
    Returns (type, name) — type and name are refined by post-tool-use.py
    when state.yaml is written (for workflows) or by eval-agent-stop.py.
    """
    return "agent", agent_type

def detect_spawn_workflow(payload: dict) -> str | None:
    """If this subagent was spawned with a raw Agent() call whose prompt
    names an explicit `workflows/{name}/workflow.md` path (e.g. Master
    dispatching Knox with "run workflows/plaud-ingest/workflow.md in
    full"), return that workflow's name. Reuses hook_utils.py's shared
    path-extraction — the same one eval-turn-start.py's detect_workflow()
    uses — rather than a second copy of the regex.

    Why this matters: plaud-ingest (and anything else dispatched this way,
    which per this session's audit is most workflows) currently produces
    real SubagentStart/SubagentStop eval records tagged only
    `type: "agent", name: "general-purpose"` — the Claude Code subagent
    type, not the workflow it's actually running. There is no query path
    from "show me plaud-ingest's evals" back to these real records. Fixed
    by writing a `workflow` field alongside the existing `name`/`type`
    (which keep their established agent-type meaning — "general-purpose" —
    unchanged; `workflow` is a new, additive field, not a replacement).

    Does not attempt to resolve intent from natural language the way
    detect_workflow() does for controller prompts (run-verbs, first-clause
    restriction, trigger phrases) — a spawn prompt either names an explicit
    workflow.md path or it doesn't; there is no ambiguity to disambiguate
    the way there is for a short conversational message, and guessing here
    would risk mistagging a genuinely ad-hoc/non-workflow subagent (e.g.
    Rigby's own capability-build dispatches, which describe work in prose
    with no workflow.md reference at all and must stay untagged)."""
    if not extract_workflow_path_reference:
        return None
    # Try the plausible field names for "the text this subagent was spawned
    # with" — Claude Code's SubagentStart payload shape for this isn't
    # documented in this repo, so check several rather than assume one.
    for key in ("prompt", "task", "description", "message", "initial_prompt"):
        text = payload.get(key)
        if isinstance(text, str) and text:
            found = extract_workflow_path_reference(text)
            if found:
                return found
    return None


def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract agent info from SubagentStart hook
    agent_id = payload.get("agent_id")
    agent_type = payload.get("agent_type")
    spawn_workflow = detect_spawn_workflow(payload)

    # Auto-generate if missing (fallback for workflows)
    if not agent_id:
        agent_id = f"agent-{secrets.token_hex(8)}"
    if not agent_type:
        agent_type = payload.get("workflow_name") or "unknown"

    # Ensure eval runs directory exists
    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate eval ID
    eval_id = new_eval_id()

    # Infer session ID
    session_id = infer_session_id(payload)

    # Infer type and name (will be refined by eval-agent-stop)
    eval_type, eval_name = infer_workflow_or_skill_name(agent_type)

    # Create eval record stub
    now = datetime.now(timezone.utc)
    stub = {
        "id": eval_id,
        "agent_id": agent_id,  # stored for reliable stop-to-start correlation
        "type": eval_type,
        "name": eval_name,
        "workflow": spawn_workflow,  # additive; None unless the spawn prompt named an
                                      # explicit workflows/{name}/workflow.md path. Does
                                      # not change the meaning of type/name above.
        "agent": agent_type,
        "session_id": session_id,
        "trigger": "workflow-dispatch" if spawn_workflow else "unknown",  # refined by post-tool-use.py when state.yaml written
        "started": now.isoformat().replace("+00:00", "Z"),
        "completed": None,
        "duration_seconds": None,
        "status": "in-progress",
        "steps": [],
        "assessment": {
            "mechanical": {
                "completed": None,
                "all_steps_finished": None,
                "tool_failures": 0,
                "error_ids": []
            },
            "structural": {
                "expected_outputs_written": None,
                "outputs_non_empty": None,
                "assertions_checked": 0,
                "assertions_passed": 0,
                "assertion_results": []
            },
            "grading": {
                "last_graded": None,
                "grade": None,
                "safety_grade": None,
                "grader_notes": None
            },
            "controller_feedback": {
                "rating": None,
                "comment": None,
                "timestamp": None
            },
            "bias_assessment": {
                "applicable": False,
                "protected_attributes": [],
                "fairness_metric": None,
                "demographic_coverage_verified": False,
                "adversarial_inputs_tested": False,
                "bias_detected": False,
                "bias_flags": [],
                "remediation_status": "none"
            }
        },
        "version_hash": None,
        "prior_baseline_id": None,
        "tags": []
    }

    # Write eval record stub
    eval_path = EVAL_RUNS_DIR / f"{eval_id}.json"
    atomic_write_json(eval_path, stub)
    if not eval_path.exists():
        log_error(f"Failed to write eval record stub for {agent_type} ({agent_id})")
    elif spawn_workflow:
        log_info(f"Tagged subagent {agent_id} ({agent_type}) with workflow={spawn_workflow!r} from spawn prompt")

    # If a turn-level workflow eval is open for this session (opened by
    # eval-turn-start.py on UserPromptSubmit), also record this subagent as
    # a child of it so eval-turn-stop.py can roll its tokens/cost/model into
    # the parent's totals. This subagent's own standalone record above is
    # unaffected — existing skill-eval consumers keep working unchanged.
    if find_unambiguous_open_turn_record:
        try:
            parent_path = find_unambiguous_open_turn_record(session_id)
            # Guard against merging a sibling fire-and-forget spawn into an
            # unrelated open workflow's subagents[] just because it's the
            # only turn record open right now. Root cause of
            # eval-20260827T162201-YWMW6Z and eval-20260828T154249-UQX5N6
            # both wrongly absorbing Knox's plaud-ingest agent into boot's
            # subagents[]: Master dispatches Knox's plaud-ingest retry (or
            # speaker-ID follow-up) as its own separate spawn *during*
            # boot's turn window, so boot's turn record is "the" (only)
            # open turn record at the moment Knox's subagent starts, even
            # though Knox's spawn has nothing to do with boot's own
            # execution. When the spawn prompt names an explicit
            # workflows/{name}/workflow.md path (detect_spawn_workflow
            # above) that differs from the open parent's own workflow name,
            # this is exactly that case — a named sibling workflow spawned
            # inside another workflow's turn, not a child of it — so skip
            # linking. A boot-internal dispatch (e.g. steps 2-8 run via a
            # plain Agent() call with no workflows/*/workflow.md reference
            # in its prompt) has spawn_workflow=None and still links
            # normally; this only excludes spawns that self-identify as a
            # *different* named workflow.
            if (
                parent_path
                and spawn_workflow
                and parent_path != eval_path
            ):
                try:
                    with open(parent_path, "r") as f:
                        parent_name = json.load(f).get("name")
                except Exception:
                    parent_name = None
                if parent_name and parent_name != spawn_workflow:
                    log_info(
                        f"Not linking subagent {agent_id} into parent "
                        f"{parent_path.name} (parent workflow={parent_name!r}, "
                        f"spawn workflow={spawn_workflow!r}) — sibling spawn, not a child"
                    )
                    parent_path = None
            if parent_path and parent_path != eval_path:
                with open(parent_path, "r") as f:
                    parent = json.load(f)
                parent.setdefault("subagents", []).append({
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "started": stub["started"],
                    "completed": None,
                    "model": None,
                    "tokens_input": None,
                    "tokens_output": None,
                    "cost_usd": None,
                })
                atomic_write_json(parent_path, parent)
        except Exception as e:
            log_error(f"Failed to link subagent {agent_id} to open turn record: {e}")

if __name__ == "__main__":
    main()

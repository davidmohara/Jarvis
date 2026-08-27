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
ALPHABET = string.ascii_uppercase + string.digits  # 36 chars, ~2.1B combos

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

def infer_session_id() -> str:
    """Attempt to read current session ID from memory/sessions/index.json.
    If no session exists, create one automatically so eval records are never orphaned."""
    try:
        index_path = IES_ROOT / "memory" / "sessions" / "index.json"
        index = []

        if index_path.exists():
            with open(index_path, "r") as f:
                index = json.load(f)

        # If we have sessions, return the last one
        if index:
            return index[-1].get("id", "")

        # If no sessions exist, create one now to ensure eval records have a session_id
        now = datetime.now(timezone.utc)
        session_id = f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"
        new_session = {
            "id": session_id,
            "started": now.isoformat().replace("+00:00", "Z"),
            "closed": None,
            "current_topic": None,
            "topics": []
        }
        index.append(new_session)

        # Write back atomically
        index_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = index_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(index, f, indent=2)
        tmp_path.replace(index_path)

        log_info(f"Created session {session_id} for eval tracking")
        return session_id

    except Exception as e:
        log_error(f"Failed to infer or create session ID: {e}")
        # Last resort: generate a session ID based on current time
        now = datetime.now(timezone.utc)
        return f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"

def infer_workflow_or_skill_name(agent_type: str) -> tuple:
    """Infer whether this is a workflow or skill and the name from agent_type.
    Returns (type, name) — type and name are refined by post-tool-use.py
    when state.yaml is written (for workflows) or by eval-agent-stop.py.
    """
    return "agent", agent_type

def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract agent info from SubagentStart hook
    agent_id = payload.get("agent_id")
    agent_type = payload.get("agent_type")

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
    session_id = infer_session_id()

    # Infer type and name (will be refined by eval-agent-stop)
    eval_type, eval_name = infer_workflow_or_skill_name(agent_type)

    # Create eval record stub
    now = datetime.now(timezone.utc)
    stub = {
        "id": eval_id,
        "agent_id": agent_id,  # stored for reliable stop-to-start correlation
        "type": eval_type,
        "name": eval_name,
        "agent": agent_type,
        "session_id": session_id,
        "trigger": "unknown",  # refined by post-tool-use.py when state.yaml written
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

if __name__ == "__main__":
    main()

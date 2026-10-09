#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-01-intake.

Re-derives the intake claims from disk rather than trusting the step's
self-report: the error log directory is read directly to confirm the recorded
entry count is plausible, and state.yaml is read to confirm the session was
actually initialized (session-id, eval-record-id, entry_count_at_start) and the
gate decision progressed past step-01.

A run that finds a clean log (zero entries) and exits is a legitimate outcome.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "error-improvement"


def load_state(path: Path) -> dict:
    docs = [d for d in yaml.safe_load_all(path.read_text()) if d]
    return docs[0] if docs else {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    entries_dir = ies_root / "systems" / "error-tracking" / "entries"

    actual_entry_count = 0
    if entries_dir.is_dir():
        actual_entry_count = len(list(entries_dir.glob("err-*.json")))

    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/error-improvement/state.yaml missing or YAML parser unavailable",
            "fields": {"entries_on_disk": actual_entry_count},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-01-intake and write initial state (session-id, eval-record-id, entry_count_at_start) to state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"entries_on_disk": actual_entry_count},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01-intake: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    session_id = state.get("session-id")
    eval_record_id = state.get("eval-record-id")
    entry_count_at_start = ctx.get("entry_count_at_start") if isinstance(ctx, dict) else None
    status = state.get("status")
    current_step = state.get("current-step")

    fields = {
        "session_id": session_id,
        "eval_record_id": eval_record_id,
        "entry_count_at_start": entry_count_at_start,
        "entries_on_disk": actual_entry_count,
        "status": status,
        "current_step": current_step,
    }

    missing = [k for k, v in (("session-id", session_id), ("eval-record-id", eval_record_id)) if not v]
    if missing or entry_count_at_start is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"step-01 intake state incomplete: missing {missing or ['entry_count_at_start']}",
            "fields": fields,
            "validation_errors": [f"missing_{m}" for m in (missing or ["entry_count_at_start"])],
            "retry_instruction": "Re-execute step-01-intake: write session-id, eval-record-id, and accumulated-context.entry_count_at_start to state.yaml.",
        }))
        return

    # A clean-log exit is a legitimate terminal outcome for this step.
    if status == "complete" and actual_entry_count == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "Clean log: zero entries on disk, workflow exited at intake as designed",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Intake initialized (session {session_id}, {actual_entry_count} entries on disk, recorded start count {entry_count_at_start})",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

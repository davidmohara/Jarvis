#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-03-triage.

step-03 is the approval gate: the workflow must not advance to step-04 without a
recorded controller approval. This verifier re-derives that from state.yaml:
either an approval is recorded (`approval_received: true` plus an
`approved_fixes` list), or the workflow legitimately skipped triage (no proposed
fixes, or the controller deferred everything, and the state has moved past this
step). A state left at `awaiting-approval` with no approval is the one outcome
this verifier refuses to pass.
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
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/error-improvement/state.yaml missing or YAML parser unavailable",
            "fields": {"approval_received": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03-triage and record the approval in state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"approval_received": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-03-triage: state.yaml is corrupted.",
        }))
        return

    approval_received = state.get("approval_received")
    approved_fixes = state.get("approved_fixes")
    status = state.get("status")
    current_step = state.get("current-step")

    fields = {
        "approval_received": approval_received,
        "approved_fixes_count": len(approved_fixes) if isinstance(approved_fixes, list) else None,
        "status": status,
        "current_step": current_step,
    }

    # Hard fail: the workflow is parked at the approval gate with no approval.
    if status == "awaiting-approval" and approval_received is not True:
        print(json.dumps({
            "result": "retry",
            "reason": "Workflow is at awaiting-approval with no recorded controller approval, the triage gate is not satisfied",
            "fields": fields,
            "validation_errors": ["approval_gate_unsatisfied"],
            "retry_instruction": "Surface the Apply Now list to the controller and record the approval (approval_received: true, approved_fixes: [...]) before advancing to step-04.",
        }))
        return

    if approval_received is True and isinstance(approved_fixes, list):
        print(json.dumps({
            "result": "pass",
            "reason": f"Controller approval recorded with {len(approved_fixes)} approved fix(es)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    # Legitimate skip paths: no proposed fixes, everything deferred, or a
    # compaction-only run, the state has moved past triage with an empty list.
    moved_past = current_step not in (None, "step-03-triage") or status == "complete"
    if isinstance(approved_fixes, list) and moved_past:
        print(json.dumps({
            "result": "pass",
            "reason": f"Triage skipped with an empty approved_fixes list (status {status}, current-step {current_step}), legitimate no-apply path",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": "No approval recorded and no legitimate skip path found in state.yaml",
        "fields": fields,
        "validation_errors": ["no_approval_no_skip"],
        "retry_instruction": "Re-execute step-03-triage: record approval_received and approved_fixes, or record the legitimate skip path (empty approved_fixes with the state advanced).",
    }))


if __name__ == "__main__":
    main()

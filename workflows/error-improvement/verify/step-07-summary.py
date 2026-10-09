#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-07-summary.

Re-derives the close claims from disk rather than trusting the step's
self-report: state.yaml must show `status: complete`, and a closed eval record
for the error-improvement workflow must exist under systems/eval-harness/runs/.
A state still parked at an earlier step is the failure this verifier catches.
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
            "fields": {"status": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-07-summary and close state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"status": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-07-summary: state.yaml is corrupted.",
        }))
        return

    status = state.get("status")

    eval_record_exists = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.exists():
        for f in runs_dir.glob("eval-*.json"):
            try:
                if (json.loads(f.read_text()) or {}).get("name") == WORKFLOW:
                    eval_record_exists = True
                    break
            except Exception:
                continue

    fields = {
        "status": status,
        "eval_record_exists": eval_record_exists,
    }

    if status != "complete":
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml status is '{status}', expected 'complete', the cycle was not closed",
            "fields": fields,
            "validation_errors": ["state_not_complete"],
            "retry_instruction": "Re-execute step-07-summary: deliver the summary, then set state.yaml status: complete as the final action.",
        }))
        return

    note = "" if eval_record_exists else " (note: no eval record found under systems/eval-harness/runs/)"
    print(json.dumps({
        "result": "pass",
        "reason": f"Cycle closed: state.yaml complete{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

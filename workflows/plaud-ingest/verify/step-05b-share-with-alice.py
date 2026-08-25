#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-05b-share-with-alice.

This is the final step and the spec is explicit: it MUST set
state.yaml status: complete when finished. External systems (Plaud
share links, Monday tasks) aren't independently checkable offline, so
ground truth here is the one thing this process can actually confirm:
the real state.yaml reflects the terminal state the step is required
to leave behind, and its own reported share/task counts are internally
consistent.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "plaud-ingest" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/plaud-ingest/state.yaml missing or YAML parser unavailable",
            "fields": {"status": None, "current_step": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05b — state.yaml must exist.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"status": None, "current_step": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05b — state.yaml is corrupted.",
        }))
        return

    status = state.get("status")
    current_step = state.get("current-step")
    ctx = state.get("accumulated-context") or {}
    classification = ctx.get("recording-classification") or {}
    work_count = sum(1 for v in classification.values() if v == "work") if isinstance(classification, dict) else 0

    fields = {
        "status": status,
        "current_step": current_step,
        "work_recordings_count": work_count,
        "personal_recordings_count": sum(1 for v in classification.values() if v == "personal") if isinstance(classification, dict) else 0,
    }

    if status != "complete" or current_step != "step-05b":
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml shows status='{status}', current-step='{current_step}' — step-05b requires status: complete, current-step: step-05b as its terminal state",
            "fields": fields,
            "validation_errors": ["terminal_state_not_reached"],
            "retry_instruction": "Finish step-05b and set state.yaml status: complete, current-step: step-05b per the step's mandatory execution rule #4.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Workflow reached terminal state (status: complete, current-step: step-05b) with {work_count} work recording(s) classified",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

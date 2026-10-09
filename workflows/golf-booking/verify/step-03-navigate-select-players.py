#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-03-navigate-select-players.

The step's whole point is to click the exact date Gate 1 validated, never a
nearby substitute. This verifier re-derives the target date from
preview-output.json (honoring override_instructions) and compares it to the date
recorded in state.yaml's accumulated-context, a mismatch means a date
substitution leaked in between the gate and the click.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-booking"


def preview_target_date(preview_path: Path):
    try:
        data = json.loads(preview_path.read_text())
    except Exception:
        return None, "preview_unreadable"
    override = data.get("override_instructions")
    if isinstance(override, dict) and override.get("date"):
        return override["date"], "override_instructions"
    top = data.get("top_options") or []
    if top and isinstance(top[0], dict):
        return top[0].get("date"), "top_options[0]"
    return None, "no_target"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    preview_path = ies_root / "workflows" / WORKFLOW / "preview-output.json"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"target_date": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03 and record target_date in state.yaml.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"target_date": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-03: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    recorded_date = ctx.get("target_date") if isinstance(ctx, dict) else None
    status = state.get("status")

    expected_date, source = preview_target_date(preview_path)

    fields = {
        "recorded_target_date": recorded_date,
        "preview_target_date": expected_date,
        "preview_source": source,
        "status": status,
    }

    if status in ("aborted", "awaiting-window", "verification-failed"):
        print(json.dumps({
            "result": "pass",
            "reason": f"No booking progressed (status {status}), no date selection to verify",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if not recorded_date:
        print(json.dumps({
            "result": "retry",
            "reason": "No target_date recorded in state.yaml, the selection step did not record which date it clicked",
            "fields": fields,
            "validation_errors": ["target_date_not_recorded"],
            "retry_instruction": "Re-execute step-03: record accumulated-context.target_date.",
        }))
        return

    if expected_date and recorded_date != expected_date:
        print(json.dumps({
            "result": "retry",
            "reason": f"Date substitution detected: clicked/recorded {recorded_date} but preview-output.json ({source}) specifies {expected_date}",
            "fields": fields,
            "validation_errors": ["date_substitution"],
            "retry_instruction": "Stop. Do not book a substituted date. Re-execute step-03 clicking exactly the Gate 1-validated date, or abort with status: aborted and a resolution-note.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Date selection matches the validated target {recorded_date} ({source}), no substitution",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

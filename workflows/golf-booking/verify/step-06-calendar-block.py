#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-06-calendar-block (Gate 5, soft).

Gate 5 is soft: the booking is already confirmed, so a calendar failure does not
undo it, but it must never be swallowed. This verifier accepts either a verified
calendar event (confirmation created-and-verified) or a recorded fallback
(`calendar_event_failed: true` in state.yaml, meaning the manual-add notice was
sent). A run with neither is the silent gap this catches.
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


def parse_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm = []
    inside = False
    for line in lines:
        if line.strip() == "---":
            inside = not inside
            if not inside:
                break
            continue
        if inside:
            fm.append(line)
    try:
        return yaml.safe_load("\n".join(fm)) or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    step_path = ies_root / "workflows" / WORKFLOW / "steps" / "step-06-calendar-block.md"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"calendar_outcome": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-06 and record the calendar outcome.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"calendar_outcome": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-06: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    outputs = (parse_frontmatter(step_path.read_text()).get("outputs") or {}) if step_path.is_file() else {}

    confirmation = None
    gate_5 = None
    if isinstance(outputs, dict):
        confirmation = outputs.get("confirmation")
        gate_5 = outputs.get("gate_5_result")
    if confirmation is None and isinstance(ctx, dict):
        confirmation = ctx.get("confirmation")
    if gate_5 is None and isinstance(ctx, dict):
        gate_5 = ctx.get("gate_5_result")

    calendar_event_failed = ctx.get("calendar_event_failed") if isinstance(ctx, dict) else None

    fields = {
        "confirmation": confirmation,
        "gate_5_result": gate_5,
        "calendar_event_failed": calendar_event_failed,
    }

    confirmation_str = str(confirmation).lower() if confirmation is not None else ""
    gate_5_str = str(gate_5).lower() if gate_5 is not None else ""

    status = state.get("status")
    resolution_note = (state.get("resolution-note") or "").strip()
    if status in ("aborted", "awaiting-window", "verification-failed") and len(resolution_note) >= 20:
        print(json.dumps({
            "result": "pass",
            "reason": f"Run did not reach the calendar step (status {status}) with a documented reason",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if "created-and-verified" in confirmation_str or "pass" in gate_5_str:
        print(json.dumps({
            "result": "pass",
            "reason": f"Gate 5: calendar event created and verified ({confirmation or gate_5})",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if calendar_event_failed is True:
        print(json.dumps({
            "result": "pass",
            "reason": "Gate 5: calendar event failed but the fallback notice was taken (calendar_event_failed: true), not a silent gap",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": "No verified calendar event and no recorded fallback, the calendar outcome is a silent gap",
        "fields": fields,
        "validation_errors": ["calendar_outcome_unrecorded"],
        "retry_instruction": "Re-execute step-06: record confirmation 'created-and-verified' from calendar-handler, or send the manual-add fallback notice and set accumulated-context.calendar_event_failed: true.",
    }))


if __name__ == "__main__":
    main()

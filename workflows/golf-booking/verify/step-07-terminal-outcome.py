#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking (Gate 7 — Terminal Outcome Honesty).

Run after step-07 claims the workflow complete. This workflow can
legitimately fail (no Chrome access, no viable windows, ChronoGolf down,
session expired, Gate 1/4 blocking) — that is a valid terminal state per
the workflow's Failure Modes table, not something to punish. The bar
this verifier enforces is honest reporting: either a real booking was
made (booking-id/date/time populated) or the failure is documented with
a specific reason. A status that looks like a failure with no explanation
recorded at all is the actual problem — a silent failure.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

MIN_DOCUMENTED_FAILURE_LENGTH = 40  # chars — enough to be a real explanation, not a stub


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "golf-booking" / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml not found or YAML parser unavailable",
            "fields": {"booking_outcome": "undocumented-failure"},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Confirm workflows/golf-booking/state.yaml exists after running skills/golf-booking/SKILL.md.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"booking_outcome": "undocumented-failure"},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute phase-2 — state.yaml is corrupted or malformed.",
        }))
        return

    booking_id = state.get("booking-id")
    booking_date = state.get("booking-date")
    booking_time = state.get("booking-time")
    resolution_note = (state.get("resolution-note") or "").strip()
    accumulated_context = state.get("accumulated-context")
    status = state.get("status")

    booked = bool(booking_id) and bool(booking_date) and bool(booking_time)

    has_documented_reason = len(resolution_note) >= MIN_DOCUMENTED_FAILURE_LENGTH
    if not has_documented_reason and accumulated_context:
        context_str = json.dumps(accumulated_context)
        has_documented_reason = len(context_str) >= MIN_DOCUMENTED_FAILURE_LENGTH

    fields = {
        "booking_id": booking_id,
        "booking_date": booking_date,
        "booking_time": booking_time,
        "status": status,
        "resolution_note_length": len(resolution_note),
    }

    if booked:
        fields["booking_outcome"] = "booked"
        print(json.dumps({
            "result": "pass",
            "reason": f"Booking confirmed: {booking_date} {booking_time} (id={booking_id})",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if has_documented_reason:
        fields["booking_outcome"] = "documented-failure"
        print(json.dumps({
            "result": "pass",
            "reason": "No booking made, but failure is documented with a specific reason (resolution-note/accumulated-context)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    fields["booking_outcome"] = "undocumented-failure"
    print(json.dumps({
        "result": "retry",
        "reason": "No booking recorded and no documented failure reason — silent failure",
        "fields": fields,
        "validation_errors": ["no_booking_no_documentation"],
        "retry_instruction": "Either complete the booking (populate booking-id/booking-date/booking-time) or document the specific failure reason in resolution-note per the Failure Modes table in workflow.md.",
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-00-cancel-prior-booking (Gate 0).

The single worst failure in this workflow is cancelling the wrong reservation.
This verifier re-derives the Gate 0 outcome from state.yaml rather than trusting
a self-reported "cancellation complete": a cancellation is only accepted when it
is recorded as verified and the prior booking id has been cleared; a
not-required no-op and a deferred cancellation (new target outside the booking
window, prior booking deliberately retained) are both legitimate outcomes.
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


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"gate_0_outcome": "unknown"},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-00 and record the Gate 0 outcome in state.yaml.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"gate_0_outcome": "unknown"},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-00: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    booking_id = state.get("booking-id")
    cancellation = ctx.get("cancellation") if isinstance(ctx, dict) else None
    cancelled_id = ctx.get("cancelled-booking-id") if isinstance(ctx, dict) else None
    cancellation_verified = ctx.get("cancellation-verified") if isinstance(ctx, dict) else None
    pending_cancellation = ctx.get("pending-cancellation") if isinstance(ctx, dict) else None

    fields = {
        "booking_id": booking_id,
        "cancellation": cancellation,
        "cancelled_booking_id": cancelled_id,
        "cancellation_verified": cancellation_verified,
        "pending_cancellation": pending_cancellation,
    }

    if cancellation == "not-required":
        fields["gate_0_outcome"] = "not-required"
        print(json.dumps({
            "result": "pass",
            "reason": "Gate 0: no prior booking to cancel (idempotent no-op)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if cancellation_verified is True and not booking_id:
        fields["gate_0_outcome"] = "cancelled-verified"
        print(json.dumps({
            "result": "pass",
            "reason": f"Gate 0: prior booking {cancelled_id} cancelled and verified absent; state cleared",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if pending_cancellation is True and booking_id:
        fields["gate_0_outcome"] = "deferred"
        print(json.dumps({
            "result": "pass",
            "reason": "Gate 0: re-book target outside the booking window, cancellation deferred, prior booking retained",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    fields["gate_0_outcome"] = "unresolved"
    print(json.dumps({
        "result": "retry",
        "reason": "Gate 0 outcome is unresolved: no not-required no-op, no verified cancellation, and no deferred-cancellation record found",
        "fields": fields,
        "validation_errors": ["gate_0_unresolved"],
        "retry_instruction": "Re-execute step-00: record one of cancellation: not-required, cancellation-verified: true (with booking-id cleared), or pending-cancellation: true (with the prior booking retained).",
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-02-login-recovery (Gate 2).

Gate 2 requires an explicit login confirmation, never an assumption. This
verifier re-derives the outcome from state.yaml: a recorded `login_method` of
`already-authenticated` or `1password-recovery` means Gate 2 passed. A run that
aborted on a failed login (status aborted with a documented reason) is a
legitimate terminal state; a run with neither a login_method nor a documented
abort is the silent failure this catches.
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
VALID_LOGIN_METHODS = {"already-authenticated", "1password-recovery"}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"login_method": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02 and record login_method in state.yaml.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"login_method": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    login_method = ctx.get("login_method") if isinstance(ctx, dict) else None
    status = state.get("status")
    resolution_note = (state.get("resolution-note") or "").strip()

    fields = {
        "login_method": login_method,
        "status": status,
        "resolution_note_length": len(resolution_note),
    }

    if login_method in VALID_LOGIN_METHODS:
        print(json.dumps({
            "result": "pass",
            "reason": f"Gate 2 passed with login_method '{login_method}'",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if status in ("aborted", "verification-failed", "awaiting-window") and len(resolution_note) >= 20:
        print(json.dumps({
            "result": "pass",
            "reason": f"Login did not run or succeed (status {status}), but the run is a documented terminal state",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": "No recorded login_method and no documented abort, Gate 2 was neither passed nor honestly failed",
        "fields": fields,
        "validation_errors": ["login_outcome_unrecorded"],
        "retry_instruction": "Re-execute step-02: record accumulated-context.login_method ('already-authenticated' or '1password-recovery'), or set status: aborted with a resolution-note on a failed login.",
    }))


if __name__ == "__main__":
    main()

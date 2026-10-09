#!/usr/bin/env python3
"""Ground-truth verifier for golf-preview/step-02-calendar-conflict-check (Gate 2).

Re-derives the per-day calendar status from the recorded data rather than
trusting the step's self-report: all three target days must carry a status of
`available`, `unavailable`, or `conditional`, and any `unavailable` day must
carry a reason. The CT-conversion flag is reported but does not block (it is a
soft gate by design).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-preview"
DAYS = ("friday", "saturday", "sunday")
VALID_STATUSES = {"available", "unavailable", "conditional"}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    preview_path = ies_root / "workflows" / "golf-booking" / "preview-output.json"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-preview/state.yaml missing or YAML parser unavailable",
            "fields": {},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02 and record per-day calendar status.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    day_status = ctx.get("day_status") if isinstance(ctx, dict) else None
    if not isinstance(day_status, dict) and preview_path.is_file():
        try:
            day_status = (json.loads(preview_path.read_text()) or {}).get("day_status")
        except Exception:
            day_status = None

    ct_flag = ctx.get("ct_conversion_flag") if isinstance(ctx, dict) else None

    fields = {
        "day_status": day_status if isinstance(day_status, dict) else None,
        "ct_conversion_flag": ct_flag,
    }

    if not isinstance(day_status, dict):
        print(json.dumps({
            "result": "retry",
            "reason": "day_status is missing or not a mapping, the calendar check was not recorded",
            "fields": fields,
            "validation_errors": ["day_status_not_recorded"],
            "retry_instruction": "Re-execute step-02: record accumulated-context.day_status with an entry for friday, saturday, and sunday.",
        }))
        return

    problems = []
    for day in DAYS:
        entry = day_status.get(day)
        if not isinstance(entry, dict):
            problems.append(f"{day}: no status recorded")
            continue
        status = entry.get("status")
        if status not in VALID_STATUSES:
            problems.append(f"{day}: invalid status '{status}'")
        elif status == "unavailable" and not (entry.get("reason") or "").strip():
            problems.append(f"{day}: unavailable with no reason")

    if problems:
        print(json.dumps({
            "result": "retry",
            "reason": f"Per-day calendar status is incomplete or invalid: {problems}",
            "fields": fields,
            "validation_errors": problems,
            "retry_instruction": "Re-execute step-02: every day needs status available|unavailable|conditional, and unavailable days need a reason.",
        }))
        return

    note = " (CT conversion flagged, soft, surfaced to David)" if ct_flag else ""
    print(json.dumps({
        "result": "pass",
        "reason": f"Per-day calendar status recorded for all three days{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

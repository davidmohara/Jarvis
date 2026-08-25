#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/phase-1-preview.

Confirms preview-output.json exists, is valid JSON, and has substantive
content: a non-empty top_options list, a target_weekend with real dates,
and day_status for all three target days. Derives candidate_windows_found
and go_no_go_summary from the actual file rather than trusting self-report.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

STALE_DAYS = 10  # weekly cadence — flag if generated_at is way older than one cycle


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    preview_path = ies_root / "workflows" / "golf-booking" / "preview-output.json"

    if not preview_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/preview-output.json does not exist",
            "fields": {"candidate_windows_found": 0, "go_no_go_summary": None},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Re-execute skills/golf-preview/SKILL.md and write preview-output.json with top_options, target_weekend, and day_status.",
        }))
        return

    try:
        data = json.loads(preview_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"preview-output.json is not valid JSON: {e}",
            "fields": {"candidate_windows_found": 0, "go_no_go_summary": None},
            "validation_errors": ["invalid_json"],
            "retry_instruction": "Re-execute the preview phase — preview-output.json is corrupted or malformed.",
        }))
        return

    validation_errors = []

    top_options = data.get("top_options") or []
    if not isinstance(top_options, list) or len(top_options) == 0:
        validation_errors.append("empty_top_options")

    target_weekend = data.get("target_weekend") or {}
    expected_days = ["friday", "saturday", "sunday"]
    missing_dates = [d for d in expected_days if not target_weekend.get(d)]
    if missing_dates:
        validation_errors.append(f"target_weekend_missing_dates: {missing_dates}")

    day_status = data.get("day_status") or {}
    missing_status = [d for d in expected_days if d not in day_status]
    if missing_status:
        validation_errors.append(f"day_status_missing_days: {missing_status}")

    available_days = [d for d in expected_days if day_status.get(d, {}).get("status") == "available"]
    unavailable_days = [d for d in expected_days if day_status.get(d, {}).get("status") == "unavailable"]
    go_no_go_summary = {
        "available": len(available_days),
        "unavailable": len(unavailable_days),
        "available_days": available_days,
        "unavailable_days": unavailable_days,
    }

    generated_at = data.get("generated_at")
    freshness_note = None
    if generated_at:
        try:
            gen_time = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
            ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
            age_days = (ref_time - gen_time).total_seconds() / 86400
            if age_days > STALE_DAYS:
                validation_errors.append(f"generated_at_stale: {round(age_days, 1)} days old")
                freshness_note = f"stale ({round(age_days, 1)}d old, expected weekly cadence)"
            else:
                freshness_note = f"fresh ({round(age_days, 1)}d old)"
        except Exception:
            validation_errors.append("generated_at_unparseable")
            freshness_note = "unparseable"
    else:
        validation_errors.append("generated_at_missing")

    fields = {
        "candidate_windows_found": len(top_options),
        "go_no_go_summary": go_no_go_summary,
        "target_weekend": target_weekend,
        "generated_at": generated_at,
        "freshness": freshness_note,
    }

    blocking_errors = [e for e in validation_errors if e in ("empty_top_options",) or e.startswith("target_weekend_missing_dates") or e.startswith("day_status_missing_days")]

    if blocking_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"preview-output.json missing required content: {blocking_errors}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run skills/golf-preview/SKILL.md to fully populate top_options, target_weekend, and day_status for all three days.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"preview-output.json valid with {len(top_options)} candidate window(s), {go_no_go_summary['available']} available / {go_no_go_summary['unavailable']} unavailable day(s)",
        "fields": fields,
        "validation_errors": validation_errors,
    }))


if __name__ == "__main__":
    main()

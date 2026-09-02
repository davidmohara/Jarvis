#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-01 (Gate 1 — Booking Window Pre-Check).

Independently re-derives the target booking date from preview-output.json
(honoring override_instructions if present) and confirms it is within the
8-day ChronoGolf booking window as of `today`. This exists because the
single worst failure mode in this whole pipeline is silently substituting
a different date than the one specified (see
systems/error-tracking/entries/err-20260813T122205-D64IQ7.json) — a script
cross-check catches a miscalculation the agent's own inline arithmetic
might not.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

BOOKING_WINDOW_DAYS = 8


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    today_str = payload.get("today")

    if not today_str:
        print(json.dumps({
            "result": "retry",
            "reason": "No 'today' date provided to the verifier",
            "fields": {},
            "validation_errors": ["missing_today"],
            "retry_instruction": "Re-invoke this verifier with today's date in YYYY-MM-DD format.",
        }))
        return

    try:
        today = datetime.strptime(today_str, "%Y-%m-%d").date()
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"'today' is not a parseable date: {e}",
            "fields": {"today": today_str},
            "validation_errors": ["today_unparseable"],
            "retry_instruction": "Re-invoke with today in YYYY-MM-DD format.",
        }))
        return

    preview_path = ies_root / "workflows" / "golf-booking" / "preview-output.json"
    if not preview_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "preview-output.json not found",
            "fields": {},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Confirm workflows/golf-preview has run and produced preview-output.json.",
        }))
        return

    try:
        data = json.loads(preview_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"preview-output.json invalid JSON: {e}",
            "fields": {},
            "validation_errors": ["invalid_json"],
            "retry_instruction": "Re-run golf-preview to regenerate a valid preview-output.json.",
        }))
        return

    override = data.get("override_instructions")
    target_date_str = None
    source = None

    if override and isinstance(override, dict) and override.get("date"):
        target_date_str = override["date"]
        source = "override_instructions"
    else:
        top_options = data.get("top_options") or []
        if top_options:
            target_date_str = top_options[0].get("date")
            source = "top_options[0]"

    if not target_date_str:
        print(json.dumps({
            "result": "retry",
            "reason": "Could not determine a target date from override_instructions or top_options",
            "fields": {"override": override, "top_options_present": bool(data.get("top_options"))},
            "validation_errors": ["no_target_date"],
            "retry_instruction": "Ensure preview-output.json has either override_instructions.date or a populated top_options[0].date.",
        }))
        return

    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"Target date '{target_date_str}' from {source} is not parseable: {e}",
            "fields": {"target_date_str": target_date_str, "source": source},
            "validation_errors": ["target_date_unparseable"],
            "retry_instruction": "Fix the date format in preview-output.json (expected YYYY-MM-DD).",
        }))
        return

    days_out = (target_date - today).days
    within_window = 0 <= days_out <= BOOKING_WINDOW_DAYS

    fields = {
        "target_date": target_date_str,
        "source": source,
        "today": today_str,
        "days_out": days_out,
        "booking_window_days": BOOKING_WINDOW_DAYS,
    }

    if within_window:
        print(json.dumps({
            "result": "pass",
            "reason": f"Target date {target_date_str} ({source}) is {days_out} day(s) out — within the {BOOKING_WINDOW_DAYS}-day window",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": f"Target date {target_date_str} ({source}) is {days_out} day(s) out — outside the {BOOKING_WINDOW_DAYS}-day window. Do NOT substitute a different date.",
        "fields": fields,
        "validation_errors": ["outside_booking_window"],
        "retry_instruction": "Set status: awaiting-window and abort this run. Do not open the date calendar or select a substitute date. Retry on the next scheduled run once the window opens for this exact date.",
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-01-gather-calendar.

Checks data/calendar-unified.json actually exists, is valid JSON, and
contains events for today rather than trusting a self-reported meeting
count. A zero-event day is a legitimate pass (clear calendar), not a
failure — only a missing/stale/unparseable file is a problem.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

STALE_HOURS = 30


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)
    today = ref_time.date().isoformat()

    cal_path = ies_root / "data" / "calendar-unified.json"
    if not cal_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "data/calendar-unified.json does not exist",
            "fields": {"events_today": 0, "total_events": 0},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Re-run boot step-01.5 unified calendar pull before proceeding with step-01.",
        }))
        return

    try:
        data = json.loads(cal_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"data/calendar-unified.json is not valid JSON: {e}",
            "fields": {"events_today": 0, "total_events": 0},
            "validation_errors": ["invalid_json"],
            "retry_instruction": "Re-run the unified calendar pull — the cached file is corrupted.",
        }))
        return

    events = data.get("events") or []
    total_events = len(events)
    events_today = 0
    for e in events:
        start = e.get("start") or ""
        if start[:10] == today:
            events_today += 1

    mtime = datetime.fromtimestamp(cal_path.stat().st_mtime, tz=timezone.utc)
    age_hours = (ref_time - mtime).total_seconds() / 3600

    validation_errors = []
    if age_hours > STALE_HOURS:
        validation_errors.append(f"calendar_file_stale: {round(age_hours, 1)}h old")

    fields = {
        "events_today": events_today,
        "total_events": total_events,
        "date_range": data.get("date_range"),
        "file_age_hours": round(age_hours, 1),
    }

    if total_events == 0 and age_hours > STALE_HOURS:
        print(json.dumps({
            "result": "retry",
            "reason": f"Calendar file is empty and stale ({round(age_hours, 1)}h old)",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run boot step-01.5 to refresh the unified calendar pull.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Calendar data present: {events_today} event(s) today, {total_events} total in range"
        + (f" (file {round(age_hours, 1)}h old — flagged stale)" if validation_errors else ""),
        "fields": fields,
        "validation_errors": validation_errors,
    }))


if __name__ == "__main__":
    main()

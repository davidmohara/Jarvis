#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-01.5-unified-calendar-pull.

Confirms data/calendar-unified.json exists, is valid JSON, and has an
events list (0 events is a valid but noteworthy outcome).
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    calendar_path = ies_root / "data" / "calendar-unified.json"

    if not calendar_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "data/calendar-unified.json does not exist",
            "fields": {"calendar_file": None, "event_count": 0},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Re-execute step-01.5 to pull the 4-day calendar window and write data/calendar-unified.json.",
        }))
        return

    try:
        data = json.loads(calendar_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"data/calendar-unified.json is not valid JSON: {e}",
            "fields": {"calendar_file": str(calendar_path), "event_count": 0},
            "validation_errors": ["invalid_json"],
            "retry_instruction": "Re-execute step-01.5 — the calendar file is corrupted or malformed.",
        }))
        return

    events = data.get("events", [])
    fields = {
        "calendar_file": str(calendar_path),
        "event_count": len(events),
        "date_range": data.get("date_range"),
        "pulled_at": data.get("pulled_at"),
    }

    if len(events) == 0:
        verdict = {
            "result": "pass",
            "reason": "calendar-unified.json exists with 0 events — valid but unusual for a 4-day window",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"calendar-unified.json exists with {len(events)} events",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

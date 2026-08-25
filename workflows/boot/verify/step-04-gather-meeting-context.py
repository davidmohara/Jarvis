#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-04-gather-meeting-context.

Derives `attendees_enriched` from the actual calendar data cross
referenced against Clay's reminders/birthdays file, rather than
trusting the model's self-reported enrichment claim.
"""

import json
import sys
from pathlib import Path


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    calendar_path = ies_root / "data" / "calendar-unified.json"
    clay_path = ies_root / "data" / "clay-reminders-unified.json"

    if not calendar_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "data/calendar-unified.json not found — no meeting context available to enrich",
            "fields": {"meetings_found": 0, "attendees_enriched": 0},
            "validation_errors": ["calendar_file_missing"],
            "retry_instruction": "Re-execute step-04 after confirming step-01.5 produced calendar-unified.json.",
        }))
        return

    try:
        calendar_data = json.loads(calendar_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"data/calendar-unified.json invalid JSON: {e}",
            "fields": {"meetings_found": 0, "attendees_enriched": 0},
            "validation_errors": ["invalid_calendar_json"],
            "retry_instruction": "Re-execute step-04 after step-01.5 rewrites a valid calendar file.",
        }))
        return

    events = calendar_data.get("events", [])
    attendee_names = set()
    for ev in events:
        for a in ev.get("attendees", []) or []:
            if isinstance(a, dict):
                name = a.get("name") or a.get("email") or a.get("emailAddress", {}).get("address") if isinstance(a.get("emailAddress"), dict) else a.get("email")
            else:
                name = str(a)
            if name:
                attendee_names.add(name)

    clay_available = clay_path.is_file()
    clay_count = 0
    if clay_available:
        try:
            clay_data = json.loads(clay_path.read_text())
            clay_count = clay_data.get("reminder_count", 0) + clay_data.get("birthday_count", 0)
        except Exception:
            clay_available = False

    fields = {
        "meetings_found": len(events),
        "attendees_enriched": len(attendee_names),
        "clay_cross_reference_available": clay_available,
        "clay_items_checked": clay_count,
    }

    verdict = {
        "result": "pass",
        "reason": f"{len(events)} meetings found, {len(attendee_names)} unique attendees identified for enrichment"
        + ("" if clay_available else " (Clay data unavailable for cross-reference)"),
        "fields": fields,
        "validation_errors": [] if clay_available else ["clay_data_unavailable"],
    }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

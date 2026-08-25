#!/usr/bin/env python3
"""Ground-truth verifier for one-on-one-prep/step-02-gather-communications.

Checks accumulated-context.communication_data for the required structural
keys (email_threads, teams_messages, shared_calendar_events, previous_brief).
Empty lists are a legitimate result ("no communications found" is a data
point per the step's failure modes, not an error) — the check is for
structural presence, not non-emptiness.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_KEYS = ["email_threads", "teams_messages", "shared_calendar_events"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "one-on-one-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/one-on-one-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"keys_present": []},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02 and ensure state.yaml is written.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"keys_present": []},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    comm = context.get("communication_data") or {}

    keys_present = [k for k in REQUIRED_KEYS if k in comm]
    missing = [k for k in REQUIRED_KEYS if k not in comm]

    email_count = len(comm.get("email_threads") or [])
    teams_count = len(comm.get("teams_messages") or [])
    calendar = comm.get("shared_calendar_events") or {}
    past_count = len((calendar or {}).get("past") or [])
    upcoming_count = len((calendar or {}).get("upcoming") or [])
    has_previous_brief = "previous_brief" in comm

    fields = {
        "keys_present": keys_present,
        "email_thread_count": email_count,
        "teams_message_count": teams_count,
        "calendar_past_count": past_count,
        "calendar_upcoming_count": upcoming_count,
        "previous_brief_section_present": has_previous_brief,
        "total_activity_items": email_count + teams_count + past_count + upcoming_count,
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"communication_data missing required structural key(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_key: {k}" for k in missing],
            "retry_instruction": f"Re-execute step-02 — populate the missing key(s) in communication_data: {', '.join(missing)}. Empty lists are fine if no activity was found, but the key must be present.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"communication_data structurally complete ({fields['total_activity_items']} total activity items across email/Teams/calendar)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

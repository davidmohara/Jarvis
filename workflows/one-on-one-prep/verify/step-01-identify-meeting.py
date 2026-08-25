#!/usr/bin/env python3
"""Ground-truth verifier for one-on-one-prep/step-01-identify-meeting.

Reads workflows/one-on-one-prep/state.yaml accumulated-context and checks
that meeting_details was actually populated with a person name (mandatory
per the step's execution rules) and either a confirmed date or an explicit
no-meeting-found note, rather than trusting a self-reported completion.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "one-on-one-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/one-on-one-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"person_confirmed": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-01 and ensure state.yaml is written.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"person_confirmed": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    meeting_details = context.get("meeting_details") or {}

    person = meeting_details.get("person")
    date = meeting_details.get("date")
    known_cadence = meeting_details.get("known_cadence")

    fields = {
        "person_confirmed": bool(person),
        "meeting_date": date,
        "location": meeting_details.get("location"),
        "known_cadence": known_cadence,
    }

    if not person:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.meeting_details is missing a confirmed person name",
            "fields": fields,
            "validation_errors": ["missing_person"],
            "retry_instruction": "Re-execute step-01 — confirm the person's full name and store it in meeting_details.person before proceeding.",
        }))
        return

    if not date:
        print(json.dumps({
            "result": "pass",
            "reason": f"Person confirmed ({person}) but no meeting date found — valid per workflow (build brief anyway, use next known cadence)",
            "fields": fields,
            "validation_errors": ["no_date_found"],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Meeting identified: {person} on {date}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

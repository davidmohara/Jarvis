#!/usr/bin/env python3
"""Ground-truth verifier for partner-meeting-prep/step-01-identify-partner.

Checks accumulated-context.partner_details for the mandatory fields the
step must confirm before proceeding: partner company name and meeting
format/date context. A missing meeting on the calendar is a valid state
per the workflow (build the prep doc anyway) — only a missing company
name is a hard failure.
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

    state_path = ies_root / "workflows" / "partner-meeting-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/partner-meeting-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"company_confirmed": False},
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
            "fields": {"company_confirmed": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    partner_details = context.get("partner_details") or {}

    company = partner_details.get("company")
    meeting_date = partner_details.get("meeting_date")
    partner_attendees = partner_details.get("partner_attendees") or []

    fields = {
        "company_confirmed": bool(company),
        "meeting_date": meeting_date,
        "partner_attendee_count": len(partner_attendees),
        "previous_prep_exists": bool((partner_details.get("previous_prep") or {}).get("exists")),
    }

    if not company:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.partner_details is missing a confirmed company name",
            "fields": fields,
            "validation_errors": ["missing_company"],
            "retry_instruction": "Re-execute step-01 — confirm the partner company name and store it in partner_details.company.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Partner identified: {company}"
        + (f", meeting {meeting_date}" if meeting_date else " (no calendar meeting found — proceeding per workflow)"),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

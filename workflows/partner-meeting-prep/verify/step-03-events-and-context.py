#!/usr/bin/env python3
"""Ground-truth verifier for partner-meeting-prep/step-03-events-and-context.

Checks accumulated-context.events_and_context for the required structural
keys. Blanks (no events found, no news found) are explicitly valid per the
step's failure modes — the check is for structural presence, not for
every section being non-empty.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_KEYS = ["controller_events", "partner_events", "industry_events", "partner_news", "office_offerings"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "partner-meeting-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/partner-meeting-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"keys_present": []},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03 and ensure state.yaml is written.",
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
            "retry_instruction": "Re-execute step-03 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    events = context.get("events_and_context") or {}

    keys_present = [k for k in REQUIRED_KEYS if k in events]
    missing = [k for k in REQUIRED_KEYS if k not in events]

    fields = {
        "keys_present": keys_present,
        "controller_events_count": len(events.get("controller_events") or []),
        "partner_events_count": len(events.get("partner_events") or []),
        "industry_events_count": len(events.get("industry_events") or []),
        "partner_news_count": len(events.get("partner_news") or []),
        "office_offerings_count": len(events.get("office_offerings") or []),
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"events_and_context missing required structural key(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_key: {k}" for k in missing],
            "retry_instruction": f"Re-execute step-03 to populate {', '.join(missing)} — empty lists are fine if genuinely nothing was found.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"events_and_context structurally complete ({fields['controller_events_count']} controller event(s), {fields['office_offerings_count']} office offering(s))",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

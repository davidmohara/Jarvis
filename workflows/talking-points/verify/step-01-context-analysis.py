#!/usr/bin/env python3
"""Ground-truth verifier for talking-points/step-01-context-analysis.

Re-derives the context analysis from accumulated-context rather than trusting
a completion flag: it requires a recorded event_type (a valid enum value,
either flat in accumulated-context or nested under event_context) and an
event identity (event_name or audience). The event type is the single
decision that gates the output format, so it is the one field that must not
be missing.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

VALID_EVENT_TYPES = ("meeting", "panel", "media", "podcast", "internal-comms", "internal_comms")


def load_state(path: Path) -> dict:
    if yaml is None or not path.is_file():
        return {}
    try:
        merged = {}
        for doc in yaml.safe_load_all(path.read_text()):
            if isinstance(doc, dict):
                for k, v in doc.items():
                    if k not in merged or v:
                        merged[k] = v
        return merged
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "talking-points" / "state.yaml")
    ctx = state.get("accumulated-context") or {}
    nested = ctx.get("event_context") or {}

    event_type = ctx.get("event_type") or (nested.get("event_type") if isinstance(nested, dict) else None)
    event_name = ctx.get("event_name") or (nested.get("event_name") if isinstance(nested, dict) else None)
    audience = nested.get("audience") if isinstance(nested, dict) else None
    key_topics = nested.get("key_topics") if isinstance(nested, dict) else None

    valid = bool(event_type) and str(event_type).strip().lower() in VALID_EVENT_TYPES

    fields = {
        "event_type": event_type,
        "event_type_is_valid": valid,
        "event_name": event_name,
        "audience": audience,
        "key_topics_count": len(key_topics) if isinstance(key_topics, list) else None,
    }

    if not event_type:
        print(json.dumps({
            "result": "retry",
            "reason": "No event_type recorded in accumulated-context, step-01 must classify the event before points can be generated",
            "fields": fields,
            "validation_errors": ["missing_event_type"],
            "retry_instruction": "Re-execute step-01 and record accumulated-context.event_type as one of "
                                 "meeting | panel | media | podcast | internal-comms.",
        }))
        return

    if not valid:
        print(json.dumps({
            "result": "retry",
            "reason": f"event_type '{event_type}' is not a recognized value (meeting|panel|media|podcast|internal-comms)",
            "fields": fields,
            "validation_errors": ["invalid_event_type"],
            "retry_instruction": "Re-execute step-01 and set event_type to a valid value.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Event context recorded: type '{event_type}'"
        + (f", '{event_name}'" if event_name else "")
        + (f" ({fields['key_topics_count']} key topic(s))" if fields["key_topics_count"] else ""),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

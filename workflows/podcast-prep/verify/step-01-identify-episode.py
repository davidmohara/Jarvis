#!/usr/bin/env python3
"""Ground-truth verifier for podcast-prep/step-01-identify-episode.

Checks accumulated-context.episode for the fields the step is required to
confirm before proceeding: episode number, title, primary guest name, and
filming date. Does not trust a self-reported "confirmed" claim — it reads
the actual stored structure.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_FIELDS = ["number", "title"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "podcast-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/podcast-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"episode_confirmed": False},
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
            "fields": {"episode_confirmed": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    episode = context.get("episode") or {}
    primary_guest = episode.get("primary_guest") or {}
    filming = episode.get("filming") or {}

    missing = [f for f in REQUIRED_FIELDS if not episode.get(f)]
    guest_name = primary_guest.get("name")

    fields = {
        "episode_number": episode.get("number"),
        "episode_title": episode.get("title"),
        "guest_name": guest_name,
        "filming_date": filming.get("date"),
    }

    if missing or not guest_name:
        missing_all = missing + ([] if guest_name else ["primary_guest.name"])
        print(json.dumps({
            "result": "retry",
            "reason": f"episode context missing required field(s): {', '.join(missing_all)}",
            "fields": fields,
            "validation_errors": [f"missing_field: {m}" for m in missing_all],
            "retry_instruction": f"Re-execute step-01 to confirm and store {', '.join(missing_all)} in accumulated-context.episode.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Episode confirmed: {episode.get('number')} — {episode.get('title')} with guest {guest_name}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for podcast-prep/step-02-gather-data.

Checks accumulated-context.gathered_data for the structural keys the step
is required to populate. This step is explicitly data-gathering only (no
document built yet), so the bar is structural completeness with honest
found:false flags where a source genuinely had nothing — not non-emptiness.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_KEYS = ["sharepoint_questions", "podcast_guide", "guest_clay", "email_context"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "podcast-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/podcast-prep/state.yaml not found or YAML parser unavailable",
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
    gathered = context.get("gathered_data") or {}

    keys_present = [k for k in REQUIRED_KEYS if k in gathered]
    missing = [k for k in REQUIRED_KEYS if k not in gathered]

    sharepoint_found = bool((gathered.get("sharepoint_questions") or {}).get("found"))
    clay_found = bool((gathered.get("guest_clay") or {}).get("found"))
    flags = gathered.get("flags") or []

    fields = {
        "keys_present": keys_present,
        "sharepoint_questions_found": sharepoint_found,
        "guest_clay_found": clay_found,
        "flags_count": len(flags),
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"gathered_data missing required structural key(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_key: {k}" for k in missing],
            "retry_instruction": f"Re-execute step-02 to populate {', '.join(missing)} (with found:false and a flag if genuinely unavailable).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"gathered_data structurally complete ({len(flags)} flag(s) noted, SharePoint questions {'found' if sharepoint_found else 'not found'})",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

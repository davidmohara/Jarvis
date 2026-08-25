#!/usr/bin/env python3
"""Ground-truth verifier for one-on-one-prep/step-04-assemble-brief.

This step does not save a standalone artifact — it assembles the brief in
working memory for step-05 to save. Ground truth here is that all upstream
data this step depends on (steps 01-03) is still present and intact in
accumulated-context by the time this step reports complete. If any upstream
key vanished, the assembly step could not have had real data to work from.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

UPSTREAM_KEYS = ["meeting_details", "communication_data", "task_data"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "one-on-one-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/one-on-one-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"upstream_keys_present": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04 after confirming steps 01-03 wrote to state.yaml.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"upstream_keys_present": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    present = [k for k in UPSTREAM_KEYS if context.get(k)]
    missing = [k for k in UPSTREAM_KEYS if not context.get(k)]

    fields = {
        "upstream_keys_present": len(present),
        "upstream_keys_expected": len(UPSTREAM_KEYS),
        "missing_upstream_keys": missing,
        "person": (context.get("meeting_details") or {}).get("person"),
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"Cannot assemble a data-backed brief — upstream data missing: {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_upstream: {k}" for k in missing],
            "retry_instruction": f"Re-execute steps that populate {', '.join(missing)} before assembling the brief in step-04.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"All {len(UPSTREAM_KEYS)} upstream data sections present in accumulated-context — brief has real data to draw from",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

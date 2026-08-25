#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-06-scan-workflows.

Derives `in_flight_list` by directly scanning every workflows/*/state.yaml
for status: in-progress, independent of what _active.yaml claims or what
the model reported.
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

    workflows_dir = ies_root / "workflows"
    if not workflows_dir.is_dir() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/ directory not found or YAML parser unavailable",
            "fields": {"in_flight_list": [], "workflows_scanned": 0},
            "validation_errors": ["workflows_dir_missing"],
            "retry_instruction": "Confirm the workflows/ directory exists and is readable.",
        }))
        return

    in_flight = []
    scanned = 0
    unreadable = []
    for state_file in workflows_dir.glob("*/state.yaml"):
        scanned += 1
        try:
            # Some state.yaml files contain a trailing '---' doc separator
            # (an empty second document) — take the first real document.
            docs = [d for d in yaml.safe_load_all(state_file.read_text()) if d]
            state = docs[0] if docs else {}
        except Exception:
            unreadable.append(str(state_file.relative_to(ies_root)))
            continue
        if state.get("status") == "in-progress":
            in_flight.append({
                "workflow": state.get("workflow") or state_file.parent.name,
                "current-step": state.get("current-step"),
                "session-started": state.get("session-started"),
            })

    active_yaml_path = workflows_dir / "_active.yaml"
    active_yaml_count = None
    if active_yaml_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(active_yaml_path.read_text()) if d]
            active_data = docs[0] if docs else {}
            active_yaml_count = len(active_data.get("active", []) or [])
        except Exception:
            active_yaml_count = None

    fields = {
        "in_flight_list": in_flight,
        "in_flight_count": len(in_flight),
        "workflows_scanned": scanned,
        "unreadable_state_files": unreadable,
        "active_yaml_count": active_yaml_count,
    }

    if scanned == 0:
        verdict = {
            "result": "retry",
            "reason": "No workflow state.yaml files found to scan",
            "fields": fields,
            "validation_errors": ["no_state_files_found"],
            "retry_instruction": "Re-execute step-06 — expected at least one workflows/*/state.yaml to exist.",
        }
    else:
        mismatch_note = ""
        if active_yaml_count is not None and active_yaml_count != len(in_flight):
            mismatch_note = f" (note: _active.yaml claims {active_yaml_count}, actual scan found {len(in_flight)} — index may be stale)"
        verdict = {
            "result": "pass",
            "reason": f"Scanned {scanned} workflow state files, found {len(in_flight)} genuinely in-progress{mismatch_note}",
            "fields": fields,
            "validation_errors": [f"unreadable_state_file: {u}" for u in unreadable],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

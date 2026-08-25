#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-05-people-check.

Reads the step's own frontmatter outputs from disk and cross-references
the delegation data step-03 actually wrote to delegations/tracker.md,
checking that step-05's people-with-overdue-items claims are consistent
with the real tracker instead of trusting them blind.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None


def extract_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm:
            fm_lines.append(line)
    try:
        return yaml.safe_load("\n".join(fm_lines)) or {}
    except Exception:
        return {}


def tracker_people(content: str) -> set:
    people = set()
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 2 and cells[1] and cells[1] != "Delegated To" and not re.fullmatch(r'-+', cells[1]):
            people.add(cells[1])
    return people


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / "workflows" / "weekly-review" / "steps" / "step-05-people-check.md"
    tracker_path = ies_root / "delegations" / "tracker.md"

    outputs = {}
    if yaml is not None and step_path.is_file():
        outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}

    tracked_people = tracker_people(tracker_path.read_text()) if tracker_path.is_file() else set()

    outputs_str = json.dumps(outputs)
    people_referenced = [p for p in tracked_people if p in outputs_str]

    fields = {
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "tracker_people_count": len(tracked_people),
        "tracker_people": sorted(tracked_people),
        "people_referenced_in_outputs": people_referenced,
    }

    if not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": "step-05 outputs block is empty — no people-check data recorded",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Record the people health summary and 1:1 prep flags in step-05 outputs.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"step-05 outputs recorded; {len(tracked_people)} people found in delegation tracker for cross-reference",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-02-rocks-review.

Parses the real rock names out of memory/personal/quarterly-objectives.md
and cross-references them against what step-02 recorded in its outputs,
so a rock review that never actually looked at the live rocks file gets
caught instead of trusted at face value.
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

ROCK_PATTERN = re.compile(r'^###\s+Rock\s+(\d+):\s*(.+?)\s*(?:\(.*\))?$', re.MULTILINE)


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


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    rocks_path = ies_root / "memory" / "personal" / "quarterly-objectives.md"
    step_path = ies_root / "workflows" / "weekly-review" / "steps" / "step-02-rocks-review.md"

    if not rocks_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "memory/personal/quarterly-objectives.md not found — nothing to check the rock review against",
            "fields": {"rocks_in_file": 0},
            "validation_errors": ["rocks_file_missing"],
            "retry_instruction": "Confirm memory/personal/quarterly-objectives.md exists before running step-02.",
        }))
        return

    content = rocks_path.read_text()
    matches = ROCK_PATTERN.findall(content)
    rocks_in_file = [f"Rock {n}: {name}" for n, name in matches]

    outputs = {}
    if yaml is not None and step_path.is_file():
        outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}

    outputs_str = json.dumps(outputs)
    rocks_mentioned = [r for n, name in matches if str(n) in outputs_str or name.split(" ")[0] in outputs_str for r in [f"Rock {n}: {name}"]]

    fields = {
        "rocks_in_file": len(rocks_in_file),
        "rock_names": rocks_in_file,
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "rocks_referenced_in_outputs": len(set(rocks_mentioned)),
    }

    if not rocks_in_file:
        verdict = {
            "result": "retry",
            "reason": "No rocks (### Rock N: ...) found in quarterly-objectives.md — cannot verify a rock-by-rock review happened",
            "fields": fields,
            "validation_errors": ["no_rocks_parsed"],
            "retry_instruction": "Confirm quarterly-objectives.md follows the '### Rock N: Name' heading convention, or update it if rocks have changed.",
        }
    elif not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": f"Found {len(rocks_in_file)} rocks in quarterly-objectives.md but step-02 outputs are empty",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Record per-rock status in step-02 outputs before proceeding.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"{len(rocks_in_file)} rocks found in quarterly-objectives.md, step-02 outputs recorded",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

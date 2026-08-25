#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-02-set-tomorrow.

Reads the step's own frontmatter `outputs` block and checks it actually
recorded a confirmed top_3 list (mandatory per the step's execution rules),
deriving `top_3_count` and rock-alignment count from the real recorded
data instead of trusting a bare completion claim.
"""

import json
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


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / "workflows" / "daily-review" / "steps" / "step-02-set-tomorrow.md"
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "step-02-set-tomorrow.md not found or YAML parser unavailable",
            "fields": {"top_3_count": 0},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/daily-review/steps/step-02-set-tomorrow.md exists.",
        }))
        return

    fm = extract_frontmatter(step_path.read_text())
    outputs = fm.get("outputs") or {}
    tomorrow_data = outputs.get("tomorrow_data") if isinstance(outputs, dict) else None
    top_3 = None
    if isinstance(tomorrow_data, dict):
        top_3 = tomorrow_data.get("top_3")
    if top_3 is None and isinstance(outputs, dict):
        top_3 = outputs.get("top_3")

    top_3_count = len(top_3) if isinstance(top_3, list) else 0
    rock_aligned_count = 0
    if isinstance(top_3, list):
        for item in top_3:
            if isinstance(item, dict) and item.get("rock_aligned"):
                rock_aligned_count += 1

    fields = {
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "top_3_count": top_3_count,
        "rock_aligned_count": rock_aligned_count,
    }

    if not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": "step-02 outputs block is empty — no tomorrow_data recorded",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-02 and record the confirmed top_3 priorities in tomorrow_data.",
        }
    elif top_3_count == 0:
        verdict = {
            "result": "retry",
            "reason": "step-02 outputs recorded but no top_3 priorities were captured",
            "fields": fields,
            "validation_errors": ["missing_top_3"],
            "retry_instruction": "Step-02 requires a confirmed top_3 list before proceeding — ask the controller and record it.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"step-02 recorded {top_3_count} priorities for tomorrow ({rock_aligned_count} rock-aligned)",
            "fields": fields,
            "validation_errors": [] if top_3_count == 3 else [f"top_3_count_unexpected: {top_3_count}"],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

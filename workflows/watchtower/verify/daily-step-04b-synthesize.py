#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-04b-synthesize.

Synthesis check. The step claims it produced a `through_line` and (when 2+
items exist) a `consulting_read`. This verifier re-derives the claim from the
step's own edge-case rules rather than trusting the frontmatter self-report:

  * `through_line` must be a non-empty string;
  * when items_synthesized >= 2, `consulting_read` must be a non-empty string
    (the step requires a consulting read whenever 2+ items exist);
  * when items_synthesized <= 1, `consulting_read` may legitimately be null.

Verdict: retry if through_line is empty or a required consulting_read is
missing; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-04b-synthesize.md"


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

    step_path = ies_root / STEP_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-04b-synthesize.md not found or YAML parser unavailable",
            "fields": {"synthesis_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-04b-synthesize.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-04b outputs block is empty - no synthesis recorded",
            "fields": {"synthesis_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-04b and record through_line/consulting_read/items_synthesized in the step frontmatter outputs.",
        }))
        return

    through_line = outputs.get("through_line")
    consulting_read = outputs.get("consulting_read")
    items_synthesized = outputs.get("items_synthesized")

    fields = {
        "through_line_present": isinstance(through_line, str) and bool(through_line.strip()),
        "consulting_read_present": isinstance(consulting_read, str) and bool(consulting_read.strip()),
        "items_synthesized": items_synthesized,
    }

    if not (isinstance(through_line, str) and through_line.strip()):
        print(json.dumps({
            "result": "retry",
            "reason": "through_line is missing or empty",
            "fields": fields,
            "validation_errors": ["through_line_missing"],
            "retry_instruction": "Generate and record a non-empty through_line in step-04b outputs.",
        }))
        return

    if isinstance(items_synthesized, int) and items_synthesized >= 2:
        if not (isinstance(consulting_read, str) and consulting_read.strip()):
            print(json.dumps({
                "result": "retry",
                "reason": f"items_synthesized={items_synthesized} (>=2) but consulting_read is missing - the step requires a consulting read for 2+ items",
                "fields": fields,
                "validation_errors": ["consulting_read_missing"],
                "retry_instruction": "Generate and record the consulting_read for this 2+ item day.",
            }))
            return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-04b synthesis verified: through_line present, consulting_read {'present' if fields['consulting_read_present'] else 'null (permitted)'} for {items_synthesized} item(s)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

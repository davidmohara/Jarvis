#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-01-capture.

Reads the step's own frontmatter `outputs` block from disk (not a
self-reported status flag) and checks it actually contains capture data —
completed/not-completed/blocker items or an inbox count — rather than an
empty or placeholder dict.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

EXPECTED_KEYS = ("completed", "not_completed", "blockers", "inbox_count", "morning_priorities_hit", "eval_health")


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

    step_path = ies_root / "workflows" / "daily-review" / "steps" / "step-01-capture.md"
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "step-01-capture.md not found or YAML parser unavailable",
            "fields": {"items_captured": 0},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/daily-review/steps/step-01-capture.md exists.",
        }))
        return

    fm = extract_frontmatter(step_path.read_text())
    outputs = fm.get("outputs") or {}

    matched_keys = [k for k in EXPECTED_KEYS if k in outputs]
    items_captured = 0
    for key in ("completed", "not_completed", "blockers"):
        value = outputs.get(key)
        if isinstance(value, list):
            items_captured += len(value)

    fields = {
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "matched_expected_keys": matched_keys,
        "items_captured": items_captured,
        "inbox_count": outputs.get("inbox_count"),
    }

    if not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": "step-01 outputs block is empty — no capture data recorded",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-01 and record capture_data (completed/not_completed/blockers/inbox_count) in the step frontmatter outputs.",
        }
    elif not matched_keys:
        verdict = {
            "result": "retry",
            "reason": "step-01 outputs present but none of the expected capture fields were recorded",
            "fields": fields,
            "validation_errors": ["no_expected_fields"],
            "retry_instruction": "Record at least one of completed/not_completed/blockers/inbox_count in step-01 outputs.",
        }
    elif items_captured == 0 and outputs.get("inbox_count") is None:
        verdict = {
            "result": "pass",
            "reason": "step-01 outputs recorded but no items or inbox count captured — likely a genuinely light day",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"step-01 captured {items_captured} item(s) across completed/not_completed/blockers",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

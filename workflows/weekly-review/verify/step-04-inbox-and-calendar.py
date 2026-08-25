#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-04-inbox-and-calendar.

Reads the step's own frontmatter outputs from disk and requires an actual
inbox count field to be present (the step's mandatory rule #1: report the
exact inbox count, no estimates) rather than trusting a bare completion
claim.
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


def find_numeric(value, keys):
    if not isinstance(value, dict):
        return None
    for k in keys:
        if k in value and isinstance(value[k], (int, float)):
            return value[k]
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / "workflows" / "weekly-review" / "steps" / "step-04-inbox-and-calendar.md"
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "step-04-inbox-and-calendar.md not found or YAML parser unavailable",
            "fields": {"inbox_count_recorded": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/weekly-review/steps/step-04-inbox-and-calendar.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    inbox_count = find_numeric(outputs, ["inbox_count", "inbox_items", "inbox"])
    calendar_items = None
    if isinstance(outputs, dict):
        for key in ("next_week_meetings", "calendar_next_week", "meetings"):
            v = outputs.get(key)
            if isinstance(v, list):
                calendar_items = len(v)
                break

    fields = {
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "inbox_count_recorded": inbox_count is not None,
        "inbox_count": inbox_count,
        "calendar_items_recorded": calendar_items,
    }

    if not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": "step-04 outputs block is empty — no inbox/calendar data recorded",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Record the exact inbox count and next week's calendar audit in step-04 outputs.",
        }
    elif inbox_count is None:
        verdict = {
            "result": "retry",
            "reason": "step-04 outputs present but no numeric inbox count recorded — the step mandates an exact count",
            "fields": fields,
            "validation_errors": ["inbox_count_missing"],
            "retry_instruction": "Pull the exact inbox count from the task management API and record it in outputs.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Inbox count recorded ({inbox_count}) and step-04 outputs present",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

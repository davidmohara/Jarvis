#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-04-summarize.

Summarize check. The step claims it summarized `items_summarized` items at an
average length of `avg_word_count`. This verifier re-derives the claim from
the upstream step and the step's own length rule rather than trusting the
frontmatter self-report:

  * items_summarized must equal step-03's `awareness_items` (one summary per
    surviving item);
  * when items_summarized > 0, avg_word_count must be a positive number within
    the step's 60-120 word bound (with headroom for a light day).

Verdict: retry on a mismatch or an out-of-bound average; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-04-summarize.md"
UPSTREAM_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-03-score.md"


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
    upstream_path = ies_root / UPSTREAM_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-04-summarize.md not found or YAML parser unavailable",
            "fields": {"summarize_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-04-summarize.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-04 outputs block is empty - no summarize counts recorded",
            "fields": {"summarize_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-04 and record items_summarized/avg_word_count in the step frontmatter outputs.",
        }))
        return

    items_summarized = outputs.get("items_summarized")
    avg_word_count = outputs.get("avg_word_count")

    upstream_awareness = None
    if upstream_path.is_file():
        up_outputs = extract_frontmatter(upstream_path.read_text()).get("outputs") or {}
        if isinstance(up_outputs, dict):
            upstream_awareness = up_outputs.get("awareness_items")

    fields = {
        "items_summarized_reported": items_summarized,
        "avg_word_count_reported": avg_word_count,
        "upstream_awareness_items": upstream_awareness,
    }

    if not isinstance(items_summarized, int):
        print(json.dumps({
            "result": "retry",
            "reason": "items_summarized is missing or not an integer",
            "fields": fields,
            "validation_errors": ["invalid_items_summarized"],
            "retry_instruction": "Record an integer items_summarized in step-04 outputs.",
        }))
        return

    if isinstance(upstream_awareness, int) and items_summarized != upstream_awareness:
        print(json.dumps({
            "result": "retry",
            "reason": f"items_summarized ({items_summarized}) != step-03 awareness_items ({upstream_awareness}) - summaries do not cover every surviving item",
            "fields": fields,
            "validation_errors": ["summaries_mismatch"],
            "retry_instruction": "Write one summary per step-03 awareness item and reconcile items_summarized.",
        }))
        return

    if items_summarized > 0:
        if not isinstance(avg_word_count, (int, float)) or avg_word_count <= 0 or avg_word_count > 120:
            print(json.dumps({
                "result": "retry",
                "reason": f"avg_word_count ({avg_word_count}) is missing or outside the 0-120 word bound",
                "fields": fields,
                "validation_errors": ["avg_word_count_out_of_bounds"],
                "retry_instruction": "Trim summaries to the 60-120 word bound and record avg_word_count.",
            }))
            return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-04 summarize reconciled: {items_summarized} item(s) summarized, avg {avg_word_count} words",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

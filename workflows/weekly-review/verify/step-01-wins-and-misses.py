#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-01-wins-and-misses.

Cross-checks the step's recorded outputs against the actual daily review
files on disk for the review week, deriving `daily_reviews_found` from the
real filesystem rather than trusting a self-reported "reviews gathered"
claim.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

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


def week_dates(payload: dict) -> list:
    raw = payload.get("step_completed") or payload.get("step_started")
    try:
        anchor = datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except Exception:
        return []
    monday = anchor - timedelta(days=anchor.weekday())
    return [(monday + timedelta(days=i)).isoformat() for i in range(7) if monday + timedelta(days=i) <= anchor]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / "workflows" / "weekly-review" / "steps" / "step-01-wins-and-misses.md"
    daily_dir = ies_root / "reviews" / "daily"

    dates = week_dates(payload)
    reviews_found = []
    if daily_dir.is_dir():
        for date in dates:
            if (daily_dir / f"{date}.md").is_file() or (daily_dir / f"auto-{date}.md").is_file():
                reviews_found.append(date)

    outputs = {}
    if yaml is not None and step_path.is_file():
        outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}

    fields = {
        "week_dates_checked": dates,
        "daily_reviews_found": reviews_found,
        "daily_reviews_found_count": len(reviews_found),
        "daily_reviews_expected_count": len(dates),
        "outputs_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
    }

    if not dates:
        verdict = {
            "result": "retry",
            "reason": "Could not determine the review week from step timestamps",
            "fields": fields,
            "validation_errors": ["week_undetermined"],
            "retry_instruction": "Ensure step-01 records started-at/completed-at timestamps so the review week can be verified.",
        }
    elif not isinstance(outputs, dict) or not outputs:
        verdict = {
            "result": "retry",
            "reason": "step-01 outputs block is empty — no wins/misses/themes recorded",
            "fields": fields,
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Record wins, misses, and themes in step-01 outputs before proceeding.",
        }
    elif len(reviews_found) == 0:
        verdict = {
            "result": "pass",
            "reason": "No daily review files exist for this week (a real gap, not a verifier failure) — outputs were still recorded",
            "fields": fields,
            "validation_errors": ["no_daily_reviews_this_week"],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Found {len(reviews_found)}/{len(dates)} daily review files for the week, outputs recorded",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

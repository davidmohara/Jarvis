#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-07-social-tracker.

Checks the actual weekly review file (or its documented working-memory
fallback) for a social-tracker section/table, and tolerates a documented
site-unavailable failure per the step's own Failure Modes table — the bar
is honest reporting of one of the two outcomes, not a specific table.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

SOCIAL_SECTION = re.compile(r'social\s*(tracker|calendar)', re.IGNORECASE)
UNAVAILABLE_NOTE = re.compile(r'social tracker unavailable', re.IGNORECASE)


def iso_week_candidates(payload: dict) -> list:
    candidates = []
    for key in ("step_completed", "step_started"):
        raw = payload.get(key)
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            year, week, _ = dt.isocalendar()
            candidates.append(f"{year}-W{week:02d}")
        except Exception:
            continue
    return sorted(set(candidates))


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    weekly_dir = ies_root / "reviews" / "weekly"
    working_dir = ies_root / "memory" / "working"
    candidates = iso_week_candidates(payload)

    review_content = ""
    review_path = None
    for wk in candidates:
        p = weekly_dir / f"{wk}.md"
        if p.is_file():
            review_content = p.read_text()
            review_path = p
            break

    working_content = ""
    working_hits = []
    if working_dir.is_dir():
        for f in working_dir.glob("*social-tracker*.md"):
            working_hits.append(f.name)
            working_content += f.read_text()

    combined = review_content + working_content
    has_social_section = bool(SOCIAL_SECTION.search(combined))
    has_unavailable_note = bool(UNAVAILABLE_NOTE.search(combined))

    fields = {
        "review_path": str(review_path.relative_to(ies_root)) if review_path else None,
        "working_memory_fallback_files": working_hits,
        "social_section_found": has_social_section,
        "unavailable_note_found": has_unavailable_note,
    }

    if has_social_section or has_unavailable_note:
        verdict = {
            "result": "pass",
            "reason": "Social tracker section found" if has_social_section else "Documented site-unavailable outcome found, per Failure Modes table",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "retry",
            "reason": "No social tracker section, unavailable-note, or working-memory fallback found for this week",
            "fields": fields,
            "validation_errors": ["social_tracker_output_missing"],
            "retry_instruction": "Run skills/sterling-social-tracker/SKILL.md and append the result (table or documented unavailability) to the weekly review file.",
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-06-set-priorities.

Checks the real filesystem for the weekly review file this step is
mandated to write (reviews/weekly/YYYY-Wxx.md), confirms it is
substantive, and derives `priorities_found` by counting numbered list
items under a priorities-style heading instead of trusting a self-reported
"priorities set" claim.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

MIN_CONTENT_LENGTH = 300
PRIORITY_HEADING = re.compile(r'^##\s+.*Priorit', re.MULTILINE | re.IGNORECASE)
NUMBERED_ITEM = re.compile(r'^\s*\d+\.\s+\S')


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


def count_priorities(content: str) -> int:
    match = PRIORITY_HEADING.search(content)
    if not match:
        return 0
    section = content[match.end():]
    next_heading = re.search(r'^##\s+', section, re.MULTILINE)
    if next_heading:
        section = section[:next_heading.start()]
    return sum(1 for line in section.split("\n") if NUMBERED_ITEM.match(line))


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    weekly_dir = ies_root / "reviews" / "weekly"
    candidates = iso_week_candidates(payload)

    found_path = None
    for wk in candidates:
        candidate = weekly_dir / f"{wk}.md"
        if candidate.is_file():
            found_path = candidate
            break

    if found_path is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"No reviews/weekly/{{week}}.md found for candidate week(s) {candidates or ['unknown']}",
            "fields": {"review_written": False, "candidate_weeks": candidates},
            "validation_errors": ["review_file_missing"],
            "retry_instruction": "Re-execute step-06 — the weekly review file must be written to reviews/weekly/YYYY-Wxx.md before closing.",
        }))
        return

    content = found_path.read_text()
    priorities_found = count_priorities(content)

    fields = {
        "review_path": str(found_path.relative_to(ies_root)),
        "review_written": True,
        "content_length": len(content),
        "priorities_found": priorities_found,
    }

    if len(content) < MIN_CONTENT_LENGTH:
        verdict = {
            "result": "retry",
            "reason": f"Weekly review file is too short ({len(content)} chars, need >= {MIN_CONTENT_LENGTH})",
            "fields": fields,
            "validation_errors": ["review_too_short"],
            "retry_instruction": "Re-execute step-06 — the weekly review file exists but lacks substantive content.",
        }
    elif priorities_found == 0:
        verdict = {
            "result": "retry",
            "reason": "Weekly review file written but no numbered priorities found under a priorities heading",
            "fields": fields,
            "validation_errors": ["no_priorities_found"],
            "retry_instruction": "Write next week's 3-5 priorities as a numbered list under a heading containing 'Priorities'.",
        }
    elif priorities_found > 5:
        verdict = {
            "result": "pass",
            "reason": f"Weekly review written with {priorities_found} priorities (mandate is 3-5 — review may need trimming, not blocking)",
            "fields": fields,
            "validation_errors": ["priorities_count_out_of_range"],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Weekly review written to {fields['review_path']} with {priorities_found} priorities ({len(content)} chars)",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

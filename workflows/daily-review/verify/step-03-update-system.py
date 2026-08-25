#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-03-update-system.

Checks the real filesystem for the daily review file this step is
mandated to write (reviews/daily/YYYY-MM-DD.md), confirms it is
substantive, and derives `sections_found` by scanning for the required
headings instead of trusting a self-reported "review written" claim.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

MIN_CONTENT_LENGTH = 300
# Tolerant of real-world heading variation (e.g. "Done Today" vs "What Got Done") —
# the mandate is that these three kinds of content exist, not exact template wording.
REQUIRED_HEADING_PATTERNS = [
    re.compile(r'^##\s+.*(What Got Done|Done Today|Completed|Wins)', re.MULTILINE | re.IGNORECASE),
    re.compile(r"^##\s+.*Tomorrow", re.MULTILINE | re.IGNORECASE),
    re.compile(r'^##\s+.*(System State|Inbox|Handoffs)', re.MULTILINE | re.IGNORECASE),
]


def candidate_dates(payload: dict) -> list:
    dates = []
    for key in ("step_started", "step_completed"):
        raw = payload.get(key)
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            dates.append(dt.strftime("%Y-%m-%d"))
        except Exception:
            continue
    return sorted(set(dates))


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    daily_dir = ies_root / "reviews" / "daily"
    dates = candidate_dates(payload)

    found_path = None
    for date in dates:
        candidate = daily_dir / f"{date}.md"
        if candidate.is_file():
            found_path = candidate
            break

    if found_path is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"No reviews/daily/{{date}}.md found for candidate date(s) {dates or ['unknown']}",
            "fields": {"review_written": False, "candidate_dates": dates},
            "validation_errors": ["review_file_missing"],
            "retry_instruction": "Re-execute step-03 — the daily review file must be written to reviews/daily/YYYY-MM-DD.md before proceeding.",
        }))
        return

    content = found_path.read_text()
    sections_found = [p.pattern for p in REQUIRED_HEADING_PATTERNS if p.search(content)]

    fields = {
        "review_path": str(found_path.relative_to(ies_root)),
        "review_written": True,
        "content_length": len(content),
        "sections_found_count": len(sections_found),
        "sections_expected": len(REQUIRED_HEADING_PATTERNS),
    }

    if len(content) < MIN_CONTENT_LENGTH:
        verdict = {
            "result": "retry",
            "reason": f"Daily review file is too short ({len(content)} chars, need >= {MIN_CONTENT_LENGTH})",
            "fields": fields,
            "validation_errors": ["review_too_short"],
            "retry_instruction": "Re-execute step-03 — the daily review file exists but lacks substantive content.",
        }
    elif len(sections_found) < 2:
        verdict = {
            "result": "retry",
            "reason": f"Daily review file exists but only {len(sections_found)}/{len(REQUIRED_HEADING_PATTERNS)} required sections found",
            "fields": fields,
            "validation_errors": ["missing_required_sections"],
            "retry_instruction": "Ensure the daily review file includes 'What Got Done', 'Tomorrow's Top 3', and 'System State' sections.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Daily review written to {fields['review_path']} ({len(content)} chars, {len(sections_found)}/{len(REQUIRED_HEADING_PATTERNS)} sections)",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

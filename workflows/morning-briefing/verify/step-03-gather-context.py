#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-03-gather-context.

Checks the identity files this step must read actually exist, and
derives yesterday's daily-review status by looking for the real file
on disk (accepting both the documented YYYY-MM-DD.md name and the
auto-*.md convention actually in use) instead of trusting the step's
self-reported "yesterday_review" claim.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REQUIRED_IDENTITY_FILES = [
    "identity/MEMORY.md",
    "identity/RESPONSIBILITIES.md",
    "identity/MISSION_CONTROL.md",
]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)
    yesterday = (ref_time - timedelta(days=1)).date().isoformat()

    missing = []
    for rel in REQUIRED_IDENTITY_FILES:
        p = ies_root / rel
        if not p.is_file() or p.stat().st_size == 0:
            missing.append(rel)

    reviews_dir = ies_root / "reviews" / "daily"
    review_found = False
    review_file = None
    if reviews_dir.is_dir():
        candidates = [reviews_dir / f"{yesterday}.md", reviews_dir / f"auto-{yesterday}.md"]
        for c in candidates:
            if c.is_file():
                review_found = True
                review_file = c.name
                break

    fields = {
        "identity_files_present": len(REQUIRED_IDENTITY_FILES) - len(missing),
        "missing_identity_files": missing,
        "yesterday_review_status": "completed" if review_found else "missing",
        "yesterday_review_file": review_file,
        "yesterday_date_checked": yesterday,
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"Required identity file(s) missing or empty: {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_or_empty: {m}" for m in missing],
            "retry_instruction": f"Re-execute step-03 and load: {', '.join(missing)}.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Identity context loaded; yesterday's review is {'present' if review_found else 'missing'}",
        "fields": fields,
        "validation_errors": [] if review_found else ["yesterday_review_missing"],
    }))


if __name__ == "__main__":
    main()

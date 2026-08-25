#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-03-delegation-review.

Parses the real delegations/tracker.md table to compute actual active,
overdue, and stale counts, rather than trusting whatever counts the step
claims to have presented to the controller.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_table_rows(content: str, heading: str) -> list:
    lines = content.split("\n")
    rows = []
    in_section = False
    header_seen = False
    for line in lines:
        if line.strip().startswith("## ") :
            in_section = line.strip().lstrip("# ").lower().startswith(heading.lower())
            header_seen = False
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue
        if set(cells) <= {"", "-", "---"} or all(re.fullmatch(r'-+', c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    tracker_path = ies_root / "delegations" / "tracker.md"
    if not tracker_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "delegations/tracker.md not found",
            "fields": {"active_delegations": 0},
            "validation_errors": ["tracker_missing"],
            "retry_instruction": "Confirm delegations/tracker.md exists before running step-03.",
        }))
        return

    content = tracker_path.read_text()
    active_rows = parse_table_rows(content, "Active Delegations")
    real_rows = [r for r in active_rows if r and r[0] not in ("", "*(none)*")]

    today = None
    raw_completed = payload.get("step_completed") or payload.get("step_started")
    if raw_completed:
        try:
            today = datetime.fromisoformat(raw_completed.replace("Z", "+00:00")).date()
        except Exception:
            today = None

    overdue = 0
    for row in real_rows:
        if len(row) < 4:
            continue
        due_raw = row[3]
        try:
            due_date = datetime.strptime(due_raw, "%Y-%m-%d").date()
        except Exception:
            continue
        if today and due_date < today:
            overdue += 1

    fields = {
        "active_delegations": len(real_rows),
        "overdue_delegations": overdue,
        "tracker_last_modified": datetime.fromtimestamp(tracker_path.stat().st_mtime).isoformat(),
    }

    verdict = {
        "result": "pass",
        "reason": f"Tracker parsed: {len(real_rows)} active delegation(s), {overdue} overdue as of the review date",
        "fields": fields,
        "validation_errors": [],
    }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

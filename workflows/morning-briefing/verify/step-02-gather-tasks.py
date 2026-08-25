#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-02-gather-tasks.

Checks the three real data sources this step is required to read —
data/omnifocus-unified.json, delegations/tracker.md, and
memory/personal/quarterly-objectives.md — actually exist and derives
real counts (inbox uncompleted, active delegation rows) instead of
trusting the step's self-reported numbers.
"""

import json
import re
import sys
from pathlib import Path


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    validation_errors = []

    omnifocus_path = ies_root / "data" / "omnifocus-unified.json"
    inbox_uncompleted = None
    if not omnifocus_path.is_file():
        validation_errors.append("omnifocus_unified_missing")
    else:
        try:
            of_data = json.loads(omnifocus_path.read_text())
            inbox_uncompleted = of_data.get("inbox", {}).get("uncompleted")
            if inbox_uncompleted is None:
                validation_errors.append("omnifocus_inbox_uncompleted_missing")
        except Exception:
            validation_errors.append("omnifocus_unified_invalid_json")

    tracker_path = ies_root / "delegations" / "tracker.md"
    active_delegation_rows = 0
    if not tracker_path.is_file():
        validation_errors.append("delegation_tracker_missing")
    else:
        text = tracker_path.read_text()
        active_section = text.split("## Active Delegations", 1)
        if len(active_section) == 2:
            section = active_section[1].split("## Completed", 1)[0]
            rows = [
                line for line in section.splitlines()
                if line.strip().startswith("|") and not line.strip().startswith("|---")
                and "Task" not in line and "*(none)*" not in line
            ]
            active_delegation_rows = len(rows)

    objectives_path = ies_root / "memory" / "personal" / "quarterly-objectives.md"
    if not objectives_path.is_file() or objectives_path.stat().st_size == 0:
        validation_errors.append("quarterly_objectives_missing_or_empty")

    fields = {
        "inbox_uncompleted": inbox_uncompleted,
        "active_delegation_rows": active_delegation_rows,
        "omnifocus_source_present": omnifocus_path.is_file(),
        "tracker_present": tracker_path.is_file(),
        "objectives_present": objectives_path.is_file(),
    }

    critical = [e for e in validation_errors if e in ("omnifocus_unified_missing", "omnifocus_unified_invalid_json")]
    if critical:
        print(json.dumps({
            "result": "retry",
            "reason": f"Required task data source unavailable: {critical}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run boot step-01.2 unified data pull, then re-execute step-02-gather-tasks.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Task/delegation sources present: {inbox_uncompleted} inbox item(s) uncompleted, {active_delegation_rows} active delegation row(s)",
        "fields": fields,
        "validation_errors": validation_errors,
    }))


if __name__ == "__main__":
    main()

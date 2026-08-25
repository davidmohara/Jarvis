#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-02-gather-data.

Derives `completed_tasks` from the actual data files each Phase 2 task
depends on, instead of trusting the model's self-reported status lines.
"""

import json
import sys
from pathlib import Path

# task-name -> backing data file. reminders (task J) is allowed to be
# legitimately empty ("nothing-to-surface"), so its presence check only
# requires the file to exist and be valid JSON, not non-empty content.
TASK_FILES = {
    "task-g-72hr-lookahead": "data/calendar-unified.json",
    "task-h-email-triage": "data/email-unified.json",
    "task-i-jarvis-inbox": "data/jarvis-inbox-unified.json",
    "task-j-reminders": "data/reminders.json",
}

CRITICAL_TASKS = {"task-g-72hr-lookahead", "task-h-email-triage"}


def file_ready(p: Path) -> bool:
    if not p.is_file():
        return False
    try:
        json.loads(p.read_text())
    except Exception:
        return False
    return True


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    completed_tasks = []
    missing_tasks = []
    for task, rel in TASK_FILES.items():
        if file_ready(ies_root / rel):
            completed_tasks.append(task)
        else:
            missing_tasks.append(task)

    fields = {
        "completed_tasks": completed_tasks,
        "completed_count": len(completed_tasks),
        "missing_tasks": missing_tasks,
        "phase2_status": "complete" if not missing_tasks else f"degraded — missing {len(missing_tasks)} task backing file(s)",
    }

    critical_missing = [t for t in missing_tasks if t in CRITICAL_TASKS]

    if critical_missing:
        verdict = {
            "result": "retry",
            "reason": f"Critical Phase 2 task data missing: {', '.join(critical_missing)}",
            "fields": fields,
            "validation_errors": [f"missing_backing_file: {t}" for t in critical_missing],
            "retry_instruction": f"Re-execute step-02 (or the upstream pull steps) to produce data for: {', '.join(critical_missing)}.",
        }
    elif not completed_tasks:
        verdict = {
            "result": "retry",
            "reason": "No Phase 2 task backing data found on disk",
            "fields": fields,
            "validation_errors": ["no_tasks_completed"],
            "retry_instruction": "Re-execute step-02 — none of the expected data files were found.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"{len(completed_tasks)}/{len(TASK_FILES)} Phase 2 tasks have real backing data on disk",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

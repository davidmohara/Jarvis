#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-02-gather-tasks.

Checks the three real data sources this step is required to read —
data/omnifocus-unified.json, delegations/tracker.md, and
memory/personal/quarterly-objectives.md — actually exist, and derives real
counts (inbox, due today, overdue, flagged, active delegation rows) instead of
trusting the step's self-reported numbers.

WHY THIS FILE WAS REWRITTEN (2026-09-16)
----------------------------------------
It used to read `of_data["inbox"]["uncompleted"]`. That key has never existed:
`skills/omnifocus-data/scripts/omnifocus_data.py` has written
`{pulled_at, status, task_count, tasks[]}` since the file was created. So the
read returned None on every run, `omnifocus_inbox_uncompleted_missing` was
raised on every run, and the verdict was still `pass` because that error was
not in the verifier's own `critical` list. A check that could not fail, and
did not.

The assertions below are derived from the shape the producer actually writes.
Two are worth calling out:

  * `task_count` must equal `len(tasks)`. That is the cheapest way to catch a
    truncated or half-written file, which otherwise looks like a quiet day.
  * No task may carry `completed: true`. This is the invariant the whole
    omnifocus-data skill exists to enforce (the inbox permanently holds ~247
    completed tasks that "Clean Up" does not remove), so it is checked here
    rather than assumed.

A `status: failed` pull is NOT a retry: the file is present and coherent, the
source is simply degraded, and re-reading it cannot help. The step's own
failure mode says to report it and carry on with delegations and rocks, so this
passes with the degradation recorded loudly in `reason` and `validation_errors`.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

STALE_HOURS = 24

# AppleScript renders due dates with `as string`, which is locale-dependent.
# en_US produces "Saturday, September 19, 2026 at 5:00:00 PM". The alternatives
# cover the plausible near neighbours; anything unparseable is counted and
# reported rather than crashing the verifier or being silently treated as "no
# due date".
APPLE_DATE_FORMATS = (
    "%A, %B %d, %Y at %I:%M:%S %p",
    "%A, %B %d, %Y at %H:%M:%S",
    "%B %d, %Y at %I:%M:%S %p",
    "%m/%d/%Y at %I:%M:%S %p",
)

def parse_apple_date(value):
    """Return a datetime, or None when the locale format is unrecognised."""
    if not value:
        return None
    for fmt in APPLE_DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def read_omnifocus(omnifocus_path, ref_time):
    """Returns (fields, validation_errors). Never raises."""
    fields = {
        "omnifocus_status": None,
        "task_count": None,
        "inbox_count": None,
        "due_today": None,
        "overdue": None,
        "flagged": None,
        "unparsed_due_dates": None,
        "file_age_hours": None,
    }
    errors = []

    if not omnifocus_path.is_file():
        return fields, ["omnifocus_unified_missing"]

    age_hours = (
        ref_time - datetime.fromtimestamp(omnifocus_path.stat().st_mtime, tz=timezone.utc)
    ).total_seconds() / 3600
    fields["file_age_hours"] = round(age_hours, 1)

    try:
        data = json.loads(omnifocus_path.read_text())
    except Exception:
        return fields, ["omnifocus_unified_invalid_json"]

    if not isinstance(data, dict):
        return fields, ["omnifocus_unified_invalid_json"]

    status = data.get("status")
    fields["omnifocus_status"] = status
    if status == "failed":
        # Present and parseable, but empty by construction. Surface the
        # underlying reason so the briefing says "degraded", not "nothing due".
        errors.append(f"omnifocus_pull_failed: {data.get('error') or 'no reason recorded'}")

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return fields, errors + ["omnifocus_tasks_not_a_list"]

    declared = data.get("task_count")
    fields["task_count"] = declared
    if not isinstance(declared, int) or declared != len(tasks):
        errors.append("omnifocus_task_count_mismatch")

    leaked = sum(1 for t in tasks if isinstance(t, dict) and t.get("completed") is not False)
    if leaked:
        errors.append("omnifocus_completed_tasks_leaked")

    inbox = due_today = overdue = flagged = unparsed = 0
    today = ref_time.date()
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("project") is None:
            inbox += 1
        if task.get("is_flagged"):
            flagged += 1

        raw_due = task.get("due_date")
        if not raw_due:
            continue
        due = parse_apple_date(raw_due)
        if due is None:
            unparsed += 1
        elif due.date() < today:
            overdue += 1
        elif due.date() == today:
            due_today += 1

    fields.update({
        "inbox_count": inbox,
        "due_today": due_today,
        "overdue": overdue,
        "flagged": flagged,
        "unparsed_due_dates": unparsed,
    })

    if unparsed:
        errors.append(f"omnifocus_unparsed_due_dates: {unparsed}")
    if age_hours > STALE_HOURS:
        errors.append(f"omnifocus_file_stale: {fields['file_age_hours']}h old")

    return fields, errors


def count_active_delegations(tracker_path, errors):
    if not tracker_path.is_file():
        errors.append("delegation_tracker_missing")
        return 0

    text = tracker_path.read_text()
    active_section = text.split("## Active Delegations", 1)
    if len(active_section) != 2:
        return 0
    section = active_section[1].split("## Completed", 1)[0]
    return len([
        line for line in section.splitlines()
        if line.strip().startswith("|") and not line.strip().startswith("|---")
        and "Task" not in line and "*(none)*" not in line
    ])


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = (
            datetime.fromisoformat(step_completed.replace("Z", "+00:00"))
            if step_completed else datetime.now(timezone.utc)
        )
    except Exception:
        ref_time = datetime.now(timezone.utc)

    errors = []
    fields, of_errors = read_omnifocus(
        ies_root / "data" / "omnifocus-unified.json", ref_time)
    errors.extend(of_errors)

    active_delegation_rows = count_active_delegations(
        ies_root / "delegations" / "tracker.md", errors)

    objectives_path = ies_root / "memory" / "personal" / "quarterly-objectives.md"
    objectives_ok = objectives_path.is_file() and objectives_path.stat().st_size > 0
    if not objectives_ok:
        errors.append("quarterly_objectives_missing_or_empty")

    fields.update({
        "active_delegation_rows": active_delegation_rows,
        "omnifocus_source_present": (ies_root / "data" / "omnifocus-unified.json").is_file(),
        "objectives_present": objectives_ok,
    })

    if "omnifocus_unified_missing" in errors:
        verdict = {
            "result": "retry",
            "reason": "data/omnifocus-unified.json does not exist — no task data for the briefing",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Run the omnifocus-data skill's pull (boot step-01.2 Pull B) to write data/omnifocus-unified.json, then re-execute step-02.",
        }
    elif "omnifocus_unified_invalid_json" in errors or "omnifocus_tasks_not_a_list" in errors:
        verdict = {
            "result": "retry",
            "reason": "data/omnifocus-unified.json is corrupt or has no task list",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Re-run the omnifocus-data pull (boot step-01.2 Pull B) — the cached file is unusable.",
        }
    elif "omnifocus_task_count_mismatch" in errors or "omnifocus_completed_tasks_leaked" in errors:
        detail = ("task_count disagrees with the task list"
                  if "omnifocus_task_count_mismatch" in errors
                  else "completed tasks leaked into the pull")
        verdict = {
            "result": "retry",
            "reason": f"data/omnifocus-unified.json failed its integrity check: {detail}",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Re-run the omnifocus-data pull (boot step-01.2 Pull B) and confirm status:available with no completed tasks in the file.",
        }
    elif fields["omnifocus_status"] == "failed":
        verdict = {
            "result": "pass",
            "reason": ("OmniFocus source is DEGRADED — the pull recorded status:failed, so the "
                       "briefing has no task data. Report it as unavailable, not as a clear day. "
                       "Proceed with delegations and rocks. "
                       f"({active_delegation_rows} active delegation row(s))"),
            "fields": fields,
            "validation_errors": errors,
        }
    else:
        verdict = {
            "result": "pass",
            "reason": (f"Task sources present: {fields['inbox_count']} inbox, "
                       f"{fields['due_today']} due today, {fields['overdue']} overdue, "
                       f"{fields['flagged']} flagged; {active_delegation_rows} active delegation row(s)"),
            "fields": fields,
            "validation_errors": errors,
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

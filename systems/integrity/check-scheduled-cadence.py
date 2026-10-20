#!/usr/bin/env python3
"""Check that every workflow documenting a recurring cadence has a matching
entry in config/scheduled-tasks.json.

Root cause this guards against: a workflow documents a monthly/weekly cadence
but was never registered as a scheduled task, so it silently never runs
(card-review / card-walkthrough, found 2026-10-16).

Implements Rule 11 of the rigby-integrity skill. Read-only. Exits 0 when
every documented cadence is covered, 1 when a gap exists.

Usage:
    python3 systems/integrity/check-scheduled-cadence.py [IES_ROOT]

If IES_ROOT is omitted, it is derived from this file's location.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RECURRING = re.compile(
    r"daily|weekly|monthly|quarterly|nightly|every day|every monday|"
    r"every week|every month|1st of|first of|last day of|auto-trigger",
    re.IGNORECASE,
)

# Cadence sources, in priority order.
SCHEDULE_FM = re.compile(r"^schedule:\s*\|?\s*\n((?:[ \t]+.+\n)+)", re.MULTILINE)
SCHEDULE_FM_INLINE = re.compile(r"^schedule:\s*(?!\|)(.+)$", re.MULTILINE)
CADENCE_LINE = re.compile(r"^\*\*Cadence:\*\*\s*(.+)$", re.MULTILINE)
TRIGGER_LINE = re.compile(r"^\*\*Trigger:\*\*\s*(.+)$", re.MULTILINE)
SCHEDULED_BULLET = re.compile(r"^\s*[-*]\s*Scheduled:\s*(.+)$", re.MULTILINE)


def resolve_root(root_arg):
    if root_arg:
        return Path(root_arg).resolve()
    return Path(__file__).resolve().parents[2]


def documented_cadence(text):
    """Return the documented cadence string, or None if the workflow is
    on-demand only."""
    m = SCHEDULE_FM.search(text)
    if m:
        return " ".join(m.group(1).split())

    m = SCHEDULE_FM_INLINE.search(text)
    if m:
        return m.group(1).strip()

    m = CADENCE_LINE.search(text)
    if m and RECURRING.search(m.group(1)):
        return m.group(1).strip()

    m = TRIGGER_LINE.search(text)
    if m and "scheduled" in m.group(1).lower() and RECURRING.search(m.group(1)):
        return m.group(1).strip()

    m = SCHEDULED_BULLET.search(text)
    if m and RECURRING.search(m.group(1)):
        return m.group(1).strip()

    return None


def skill_workflow(root, skill):
    """Resolve a task's skill to the workflow it executes, if any."""
    skill_md = root / ".claude" / "skills" / skill / "SKILL.md"
    if not skill_md.exists():
        return None
    m = re.search(r"workflows/([a-z0-9-]+)/workflow\.md", skill_md.read_text())
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(
        description="Check that every workflow documenting a recurring cadence has a "
                    "matching entry in config/scheduled-tasks.json. Read-only; exits 1 "
                    "when a gap exists.",
        epilog="Example:\n  python3 systems/integrity/check-scheduled-cadence.py",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ies_root", nargs="?", default=None,
                    help="IES root (default: derived from this file's location)")
    args = ap.parse_args()
    root = resolve_root(args.ies_root)
    config_path = root / "config" / "scheduled-tasks.json"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        return 1

    config = json.loads(config_path.read_text())
    covered = set()
    for task in config.get("tasks", []):
        if task.get("workflow"):
            covered.add(task["workflow"])
        elif task.get("skill"):
            wf = skill_workflow(root, task["skill"])
            if wf:
                covered.add(wf)

    gaps = []
    for wf_md in sorted((root / "workflows").glob("*/workflow.md")):
        name = wf_md.parent.name
        cadence = documented_cadence(wf_md.read_text())
        if cadence and name not in covered:
            gaps.append((name, cadence))

    if not gaps:
        print("Scheduled cadence coverage: OK "
              f"({len(covered)} workflows covered by scheduled tasks).")
        return 0

    print(f"Scheduled cadence gaps: {len(gaps)} workflow(s) document a "
          "recurring cadence but have no entry in config/scheduled-tasks.json\n")
    for name, cadence in gaps:
        print(f"  - {name}: {cadence}")
    print("\nAction: add a scheduled task (Cowork setup by David) or remove "
          "the cadence claim from the workflow.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

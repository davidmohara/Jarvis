#!/usr/bin/env python3
"""
Validate that no SKILL.md file carries a stamped eval-harness completion section.

History: this script originally stamped "SKILL COMPLETE" + "GRADE THIS RUN"
sections into every SKILL.md. That rollout is finished and the policy has
reversed (2026-10-10): instructional files carry no eval-harness machinery;
outcome capture is hook-based. This script is now a read-only guard: it FAILS
(exit 1) if any skill file contains a stamped section, so a regression (a
re-run of the old stamping behavior, or a new skill copied from a stamped
template) is caught immediately. It never writes to skills/ or workflows/.
"""

import re
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIRS = [IES_ROOT / ".claude" / "skills", IES_ROOT / "skills"]

STAMP_PATTERNS = [
    (re.compile(r"^## SKILL COMPLETE\b", re.MULTILINE), "stamped SKILL COMPLETE section"),
    (re.compile(r"^## GRADE THIS RUN\b", re.MULTILINE), "stamped GRADE THIS RUN section"),
]


def violations(skill_file: Path):
    """Return (pattern_description) tuples for every stamped section found."""
    try:
        content = skill_file.read_text(encoding="utf-8")
    except Exception as exc:
        return [(f"unreadable: {exc}",)]
    return [(desc,) for pattern, desc in STAMP_PATTERNS if pattern.search(content)]


def main() -> int:
    found = []
    checked = 0
    for skills_dir in SKILLS_DIRS:
        if not skills_dir.is_dir():
            continue
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            checked += 1
            for desc in violations(skill_file):
                found.append((skill_file, desc))
    if found:
        print(f"FAIL: {len(found)} stamped eval-harness section(s) found in {checked} skill files:")
        for skill_file, (desc,) in found:
            print(f"  {skill_file.relative_to(IES_ROOT)}: {desc}")
        print("Instructional files must not carry eval-harness completion sections.")
        print("Outcome capture is hook-based (.claude/hooks/ + systems/eval-harness/skill-capture).")
        return 1
    print(f"OK: no stamped eval-harness sections in {checked} skill files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

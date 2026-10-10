#!/usr/bin/env python3
"""
Validate that no workflow step file carries a stamped step-tracking call block.

History: this script originally stamped "STEP COMPLETION TRACKING"
record-step.py invocation blocks into every workflow step file. That rollout
is finished and the policy has reversed (2026-10-10): step files carry no
tracking machinery; step completion is captured by the hook chain
(eval-agent-stop.py dispatches step-complete.py on SubagentStop). This
script is now a read-only guard: it FAILS (exit 1) if any step file contains
a stamped record-step.py invocation block, so a regression is caught
immediately. It never writes to skills/ or workflows/.
"""

import re
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = IES_ROOT / "workflows"

STAMP_PATTERN = re.compile(
    r"^## STEP COMPLETION TRACKING\b.*?record-step\.py",
    re.MULTILINE | re.DOTALL,
)


def violations(step_file: Path):
    """Return a description for every stamped tracking block found."""
    try:
        content = step_file.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"unreadable: {exc}"]
    return ["stamped STEP COMPLETION TRACKING block"] if STAMP_PATTERN.search(content) else []


def main() -> int:
    found = []
    checked = 0
    if WORKFLOWS_DIR.is_dir():
        for step_file in sorted(WORKFLOWS_DIR.glob("*/steps/*.md")):
            checked += 1
            for desc in violations(step_file):
                found.append((step_file, desc))
    if found:
        print(f"FAIL: {len(found)} stamped step-tracking block(s) found in {checked} step files:")
        for step_file, desc in found:
            print(f"  {step_file.relative_to(IES_ROOT)}: {desc}")
        print("Step completion is captured by the hook chain (.claude/hooks/eval-agent-stop.py")
        print("dispatches step-complete.py on SubagentStop), never by in-file blocks.")
        return 1
    print(f"OK: no stamped step-tracking blocks in {checked} step files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

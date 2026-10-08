#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-03-gitignore-check.

Re-reads the actual .gitignore and re-derives the pattern-coverage claim,
instead of trusting the step's no_changes_needed self-report.
"""

import json
import sys
from pathlib import Path

STEP = Path(__file__).resolve().parents[1] / "steps" / "step-03-gitignore-check.md"
GITIGNORE = Path(__file__).resolve().parents[3] / ".gitignore"

EXPECTED_COVERAGE = {
    ".DS_Store": ".DS_Store",
    "meetings/**/*.html": "meetings/**/*.html",
    ".fuse_hidden": ".fuse_hidden",
    "__pycache__/": "__pycache__/",
    "*.pyc": "*.pyc",
    "*.tmp": "*.tmp",
}


def main():
    validation_errors = []
    fields = {}

    lines = GITIGNORE.read_text().splitlines() if GITIGNORE.exists() else []
    text = "\n".join(lines)
    missing = [label for needle, label in EXPECTED_COVERAGE.items() if needle not in text]
    fields["expected_patterns"] = len(EXPECTED_COVERAGE)
    fields["missing_patterns"] = missing

    if missing:
        validation_errors.append("gitignore_coverage_gap")

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f".gitignore is missing {len(missing)} expected temp-artifact pattern(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Add the missing pattern(s) to .gitignore as part of step-03, then re-verify.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"All {len(EXPECTED_COVERAGE)} expected temp-artifact patterns covered by .gitignore",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

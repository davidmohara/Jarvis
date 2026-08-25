#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-03-gitignore-check.

Reads the actual .gitignore file and confirms the core temp-artifact
patterns from step-01's table are covered, instead of trusting the
model's gitignore_results self-report.
"""

import json
import sys
from pathlib import Path

REQUIRED_PATTERNS = {
    ".DS_Store": [".DS_Store"],
    ".fuse_hidden*": [".fuse_hidden"],
    "__pycache__/": ["__pycache__"],
    "*.tmp": ["*.tmp"],
    "meetings/**/*.html": ["meetings/**/*.html", "meetings/**/*html"],
    "*.pyc": ["*.pyc"],
}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    gitignore_path = ies_root / ".gitignore"

    if not gitignore_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": ".gitignore does not exist at repo root",
            "fields": {"patterns_present": 0, "patterns_missing": list(REQUIRED_PATTERNS.keys())},
            "validation_errors": ["gitignore_missing"],
            "retry_instruction": "Create .gitignore with the standard temp-artifact patterns.",
        }))
        return

    content = gitignore_path.read_text()
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]

    missing = []
    for label, candidates in REQUIRED_PATTERNS.items():
        if not any(any(c in line for c in candidates) for line in lines):
            missing.append(label)

    fields = {
        "patterns_present": len(REQUIRED_PATTERNS) - len(missing),
        "patterns_missing": missing,
        "total_gitignore_lines": len(lines),
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f".gitignore is missing {len(missing)} required pattern(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_pattern: {m}" for m in missing],
            "retry_instruction": f"Add the missing gitignore patterns: {', '.join(missing)}. Do not remove or reorder existing entries.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"All {len(REQUIRED_PATTERNS)} required temp-artifact patterns are present in .gitignore",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

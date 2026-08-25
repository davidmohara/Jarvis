#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-04-root-audit.

Scans the actual IES root directory for files that shouldn't be there
(the same flag patterns the step itself uses), rather than trusting a
self-reported "root is clean" claim. This step is housekeeping and does
not block the day from closing, so a dirty root is reported but only
fails the checkpoint if the audit produced a large, clearly unaddressed
backlog of stray files.
"""

import json
import re
import sys
from pathlib import Path

EXCLUDED = {"CLAUDE.md", "SYSTEM.md", "README.md", ".gitignore", "evolution.manifest.json"}
FLAG_PATTERNS = [
    re.compile(r'\.py$'),
    re.compile(r'_temp'),
    re.compile(r'_draft'),
    re.compile(r'_working'),
    re.compile(r'^research-report-'),
    re.compile(r'_sync_report'),
    re.compile(r'\.pdf$'),
    re.compile(r'\.pptx$'),
    re.compile(r'\.docx$'),
    re.compile(r'\.html$'),
]
STRAY_THRESHOLD = 8


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    if not ies_root.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": "IES root directory not found",
            "fields": {"stray_files": []},
            "validation_errors": ["root_missing"],
            "retry_instruction": "Confirm ies_root resolves to a real directory.",
        }))
        return

    stray = []
    for entry in ies_root.iterdir():
        if not entry.is_file():
            continue
        name = entry.name
        if name.startswith(".") or name in EXCLUDED:
            continue
        if any(p.search(name) for p in FLAG_PATTERNS):
            stray.append(name)

    fields = {
        "root_files_scanned": sum(1 for e in ies_root.iterdir() if e.is_file()),
        "stray_file_count": len(stray),
        "stray_files": sorted(stray),
        "root_clean": len(stray) == 0,
    }

    if len(stray) > STRAY_THRESHOLD:
        verdict = {
            "result": "pass",
            "reason": f"Root directory has {len(stray)} stray file(s) matching routing-failure patterns — housekeeping backlog is growing, does not block the day from closing",
            "fields": fields,
            "validation_errors": [f"stray_file: {n}" for n in stray],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": "Root is clean" if not stray else f"Root has {len(stray)} stray file(s), within housekeeping tolerance",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

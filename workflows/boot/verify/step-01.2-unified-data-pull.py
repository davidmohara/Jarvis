#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-01.2-unified-data-pull.

Checks that each data/*.json file the step is responsible for actually
exists, is non-empty, and was written recently (near the step's own
time window) rather than being a stale leftover.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

FILES = [
    "data/email-unified.json",
    "data/omnifocus-unified.json",
    "data/clay-reminders-unified.json",
    "data/jarvis-inbox-unified.json",
]

FRESH_WINDOW_HOURS = 24


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)

    file_status = {}
    missing = []
    stale = []
    for rel in FILES:
        p = ies_root / rel
        if not p.is_file() or p.stat().st_size == 0:
            missing.append(rel)
            file_status[rel] = "missing_or_empty"
            continue
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        age_hours = (ref_time - mtime).total_seconds() / 3600
        if age_hours > FRESH_WINDOW_HOURS:
            stale.append(rel)
            file_status[rel] = f"stale ({age_hours:.1f}h old)"
        else:
            file_status[rel] = f"fresh ({age_hours:.1f}h old)"

    fields = {
        "files_created": [f for f in FILES if f not in missing],
        "files_missing": missing,
        "files_stale": stale,
        "file_status": file_status,
    }

    validation_errors = [f"missing: {m}" for m in missing]

    if missing:
        verdict = {
            "result": "retry",
            "reason": f"{len(missing)} unified data file(s) missing or empty: {', '.join(missing)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": f"Re-execute step-01.2 to pull and write: {', '.join(missing)}.",
        }
    elif stale:
        verdict = {
            "result": "pass",
            "reason": f"All files present; {len(stale)} older than {FRESH_WINDOW_HOURS}h and likely reused from a prior run: {', '.join(stale)}",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": "All 4 unified data files present and fresh",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

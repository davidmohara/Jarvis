#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-01-load-context.

Checks that the identity/context files the step is supposed to load
actually exist and are readable on disk, and looks for evidence that
Knox was spawned (an eval record for the plaud-ingest workflow).
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

REQUIRED_FILES = [
    "agents/master.md",
    "SYSTEM.md",
    "identity/MEMORY.md",
    "identity/VOICE.md",
    "identity/GOALS_AND_DREAMS.md",
    "identity/RESPONSIBILITIES.md",
    "identity/AUTOMATION.md",
    "identity/MISSION_CONTROL.md",
    "agents/routing.md",
]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_started = payload.get("step_started")

    missing = []
    for rel in REQUIRED_FILES:
        p = ies_root / rel
        if not p.is_file() or p.stat().st_size == 0:
            missing.append(rel)

    knox_evidence = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.exists():
        window_start = None
        try:
            window_start = datetime.fromisoformat(step_started.replace("Z", "+00:00")) if step_started else None
        except Exception:
            window_start = None
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            name = str(data.get("name", ""))
            if "plaud" not in name.lower() and "knox" not in name.lower():
                continue
            if not window_start:
                knox_evidence = True
                break
            try:
                started = datetime.fromisoformat(str(data.get("started", "")).replace("Z", "+00:00"))
            except Exception:
                continue
            if started >= window_start - timedelta(minutes=5):
                knox_evidence = True
                break

    fields = {
        "files_loaded": len(REQUIRED_FILES) - len(missing),
        "missing_files": missing,
        "knox_spawn_evidence": knox_evidence,
    }

    if missing:
        verdict = {
            "result": "retry",
            "reason": f"{len(missing)} required context file(s) missing or empty: {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_or_empty: {m}" for m in missing],
            "retry_instruction": f"Re-execute step-01 to load these files: {', '.join(missing)}.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"All {len(REQUIRED_FILES)} context files present"
            + (" (no Knox spawn evidence found yet — informational only)" if not knox_evidence else ", Knox spawn evidence found"),
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-08-knox-completion-check.

Looks for the actual plaud-ingest/Knox eval record and reports its
real status. This step is documented as non-blocking (Knox is
fire-and-forget), so the verifier only ever passes — it exists to make
the reported knox_status/knox_eval_id trustworthy, not to gate boot.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_started = payload.get("step_started")

    runs_dir = ies_root / "systems" / "eval-harness" / "runs"

    try:
        window_start = datetime.fromisoformat(step_started.replace("Z", "+00:00")) - timedelta(hours=6) if step_started else None
    except Exception:
        window_start = None

    candidates = []
    if runs_dir.exists():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            name = str(data.get("name", "")).lower()
            if "plaud" not in name and "knox" not in name:
                continue
            if window_start:
                try:
                    started = datetime.fromisoformat(str(data.get("started", "")).replace("Z", "+00:00"))
                except Exception:
                    continue
                if started < window_start:
                    continue
            candidates.append((f, data))

    if not candidates:
        verdict = {
            "result": "pass",
            "reason": "No Knox/plaud-ingest eval record found in the relevant window — valid documented outcome (background job may not have started or finished yet)",
            "fields": {"knox_status": "no_record", "knox_eval_id": None},
            "validation_errors": [],
        }
        print(json.dumps(verdict))
        return

    candidates.sort(key=lambda x: x[1].get("started", ""), reverse=True)
    record_path, record = candidates[0]

    raw_status = record.get("status")
    completed = record.get("completed")
    if raw_status in ("success", "complete") and completed:
        knox_status = "success"
    elif raw_status in ("failure", "partial") :
        knox_status = "failure"
    elif not completed:
        knox_status = "still_running"
    else:
        knox_status = raw_status or "unknown"

    fields = {
        "knox_status": knox_status,
        "knox_eval_id": record.get("id"),
        "knox_raw_status": raw_status,
        "knox_duration_seconds": record.get("duration_seconds"),
    }

    verdict = {
        "result": "pass",
        "reason": f"Knox eval record found ({record.get('id')}): status={knox_status}",
        "fields": fields,
        "validation_errors": [],
    }
    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

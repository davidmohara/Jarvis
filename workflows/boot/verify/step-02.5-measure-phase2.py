#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-02.5-measure-phase2.

This step is explicitly non-blocking in its own spec (measurement is
optional instrumentation). The verifier checks for an actual
measurement snapshot file near the step's time window and never
escalates — only pass or retry (retry is soft, since boot proceeds
regardless).
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

WINDOW_HOURS = 6


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    measurements_dir = ies_root / "systems" / "boot-instrumentation" / "measurements"

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)

    if not measurements_dir.exists():
        print(json.dumps({
            "result": "retry",
            "reason": "systems/boot-instrumentation/measurements/ directory does not exist",
            "fields": {"phase2_measurement_file": None, "total_kb": None},
            "validation_errors": ["measurements_dir_missing"],
            "retry_instruction": "Run measure.py to produce a measurement snapshot, or confirm the directory path.",
        }))
        return

    candidates = sorted(measurements_dir.glob("measurement-state-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print(json.dumps({
            "result": "retry",
            "reason": "No measurement-state-*.json snapshots found",
            "fields": {"phase2_measurement_file": None, "total_kb": None},
            "validation_errors": ["no_measurement_files"],
            "retry_instruction": "Run systems/boot-instrumentation/measure.py to produce a snapshot.",
        }))
        return

    latest = candidates[0]
    mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    age_hours = (ref_time - mtime).total_seconds() / 3600

    total_kb = round(latest.stat().st_size / 1024, 2)
    fields = {
        "phase2_measurement_file": str(latest.relative_to(ies_root)),
        "total_kb": total_kb,
        "snapshot_age_hours": round(age_hours, 2),
    }

    if age_hours > WINDOW_HOURS:
        verdict = {
            "result": "pass",
            "reason": f"Most recent measurement snapshot is {age_hours:.1f}h old (older than expected {WINDOW_HOURS}h window) — non-blocking, boot proceeds regardless",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Measurement snapshot found: {latest.name} ({total_kb} KB, {age_hours:.1f}h old)",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

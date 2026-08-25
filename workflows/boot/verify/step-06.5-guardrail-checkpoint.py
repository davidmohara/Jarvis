#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-06.5-guardrail-checkpoint.

Derives `stale_sources` by checking actual mtimes on data/*.json
against a staleness threshold, instead of trusting a self-reported
freshness claim.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

STALE_THRESHOLD_HOURS = 24


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)

    data_dir = ies_root / "data"
    if not data_dir.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": "data/ directory not found — cannot assess source freshness",
            "fields": {"stale_sources": [], "data_freshness_report": "unavailable"},
            "validation_errors": ["data_dir_missing"],
            "retry_instruction": "Confirm the data/ directory exists before running this checkpoint.",
        }))
        return

    stale_sources = []
    fresh_sources = []
    for f in sorted(data_dir.glob("*.json")):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        age_hours = (ref_time - mtime).total_seconds() / 3600
        entry = {"file": f.name, "age_hours": round(age_hours, 1)}
        if age_hours > STALE_THRESHOLD_HOURS:
            stale_sources.append(entry)
        else:
            fresh_sources.append(entry)

    fields = {
        "stale_sources": stale_sources,
        "fresh_sources": fresh_sources,
        "stale_threshold_hours": STALE_THRESHOLD_HOURS,
        "data_freshness_report": "pass" if not stale_sources else f"{len(stale_sources)} stale source(s) found",
    }

    # Reporting staleness truthfully is the point of this checkpoint — it is
    # informational, not something retrying step-06.5 itself can fix (the
    # underlying pull steps would need to re-run instead). Always pass.
    verdict = {
        "result": "pass",
        "reason": "All data sources fresh" if not stale_sources
        else f"{len(stale_sources)} stale source(s): {', '.join(s['file'] for s in stale_sources)}",
        "fields": fields,
        "validation_errors": [],
    }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

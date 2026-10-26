#!/usr/bin/env python3
"""Backfill correlation IDs onto existing eval run records.

Additive only: a record without a correlation_id gets one (minted fresh) and
every step entry gets it attached; records that already have one are left
untouched, as are steps that already carry it. No other field is read or
written. Used once to extend end-to-end tracing to historical records; new
records get IDs automatically at first recorded step (record-step.py).

Usage:
  python3 systems/eval-harness/backfill-correlation-ids.py [--runs-dir PATH] [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from correlation import mint, attach_to_step  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=str(IES_ROOT / "systems" / "eval-harness" / "runs"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    runs_dir = Path(args.runs_dir)

    minted = skipped = steps_tagged = 0
    for path in sorted(runs_dir.glob("eval-*.json")):
        try:
            record = json.loads(path.read_text())
        except Exception:
            print(f"skip (unreadable): {path.name}")
            continue
        if not isinstance(record, dict) or record.get("correlation_id"):
            skipped += 1
            continue
        record["correlation_id"] = mint()
        for raw in record.get("steps") or []:
            if isinstance(raw, dict):
                attach_to_step(record, raw)
                steps_tagged += 1
        minted += 1
        if not args.dry_run:
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(record, indent=2))
            tmp.replace(path)

    verb = "would mint" if args.dry_run else "minted"
    print(f"{verb} {minted} correlation IDs; tagged {steps_tagged} step entries; "
          f"{skipped} records already had one")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Success-rate recompute for the candidate workflows.

Metric definition (unchanged from the 2026-10-08 baseline):
  strict     = record status in (success, complete)
  mech       = strict + partial (ran to completion with degraded output)
  session-exit aborts (abort_reason == 'session-exit-normal') are excluded
  from the mech denominator and counted separately
  instrumented = record has at least one step with token attribution

Usage:
  python3 systems/eval-harness/success-rate.py [--runs-dir PATH] [--csv PATH]
"""

import argparse
import csv
import glob
import json
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ["boot", "morning-briefing", "daily-review", "plaud-ingest"]


def instrumented(record: dict) -> bool:
    for raw in record.get("steps") or []:
        if isinstance(raw, dict) and raw.get("tokens_input"):
            return True
    return False


def tier(record: dict) -> str:
    status = record.get("status")
    mech = (record.get("assessment") or {}).get("mechanical") or {}
    if status in ("success", "complete"):
        return "strict"
    if status == "partial" and mech.get("completed") and mech.get("all_steps_finished"):
        return "degraded"  # mech tier: finished every step, degraded output
    abort = mech.get("abort_reason")
    if status in ("aborted", "incomplete") and abort == "session-exit-normal":
        return "session-exit"
    return "other"  # failure, incomplete w/o session-exit reason, in-progress


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", default=str(IES_ROOT / "systems" / "eval-harness" / "runs"))
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    rows = []
    for path in sorted(glob.glob(str(Path(args.runs_dir) / "eval-*.json"))):
        try:
            record = json.loads(Path(path).read_text())
        except Exception:
            continue
        if record.get("name") not in CANDIDATES:
            continue
        rows.append({
            "workflow": record["name"],
            "run_id": record.get("id", Path(path).stem),
            "correlation_id": record.get("correlation_id"),
            "status": record.get("status"),
            "tier": tier(record),
            "instrumented": instrumented(record),
        })

    print(f"{'workflow':<17} {'scope':<13} {'recs':>5} {'strict':>7} {'degraded':>9} "
          f"{'sessexit':>9} {'other':>6} {'mech%':>7} {'strict%':>8}")
    csv_rows = []
    for wf in CANDIDATES:
        wf_rows = [r for r in rows if r["workflow"] == wf]
        for scope, subset in (("all-records", wf_rows),
                              ("instrumented", [r for r in wf_rows if r["instrumented"]])):
            if not subset:
                print(f"{wf:<17} {scope:<13} {0:>5}  (no instrumented records)")
                continue
            n = len(subset)
            strict = sum(r["tier"] == "strict" for r in subset)
            degraded = sum(r["tier"] == "degraded" for r in subset)
            sess = sum(r["tier"] == "session-exit" for r in subset)
            other = sum(r["tier"] == "other" for r in subset)
            mech_denom = n - sess
            mech = (strict + degraded) / mech_denom * 100 if mech_denom else 0.0
            strict_pct = strict / n * 100
            print(f"{wf:<17} {scope:<13} {n:>5} {strict:>7} {degraded:>9} "
                  f"{sess:>9} {other:>6} {mech:>6.1f}% {strict_pct:>7.1f}%")
            csv_rows.append({
                "workflow": wf, "scope": scope, "records": n, "strict": strict,
                "degraded_completion": degraded, "session_exit_aborts": sess,
                "other": other, "mech_rate_pct": round(mech, 1),
                "strict_rate_pct": round(strict_pct, 1),
            })

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\nwrote {args.csv}")


if __name__ == "__main__":
    main()

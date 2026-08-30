#!/usr/bin/env python3
"""
Close any open eval records at session exit.

Marks open evals with status: "incomplete" and abort_reason: "session-exit-normal"
so they're not counted as system failures in the success-rate metric.

A record with zero steps and zero subagents never represents a workflow
that actually ran this session — most commonly a "boot-first-prompt-of-
session" record eval-turn-start.py opened speculatively for a session that
never invoked boot. Marking that "incomplete" still leaves a record for
something that never happened. Those get deleted instead of closed — see
err-20260829T161711-3IPMKR for the incident that surfaced this.

Usage:
  python3 close-open-evals.py /path/to/eval-harness/runs/
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def close_open_evals(eval_dir):
    """Find and close any open eval records."""
    eval_path = Path(eval_dir)
    if not eval_path.exists():
        print(f"Eval directory not found: {eval_path}")
        return 0

    closed = 0
    deleted = 0
    now = datetime.now(tz=timezone.utc).isoformat()

    for f in eval_path.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            # Only close if still in-progress
            if data.get("status") == "in-progress":
                if not data.get("steps") and not data.get("subagents"):
                    # Never accrued a single step or subagent — nothing
                    # actually ran under this record. Delete it rather than
                    # leaving a false trace of a workflow that never
                    # happened, closed or otherwise.
                    f.unlink()
                    deleted += 1
                    continue

                data["status"] = "incomplete"
                data["completed"] = now
                data["assessment"]["mechanical"]["abort_reason"] = "session-exit-normal"
                data["assessment"]["mechanical"]["completed"] = False

                with open(f, "w") as file:
                    json.dump(data, file, indent=2)
                closed += 1
        except Exception as e:
            print(f"Error processing {f.name}: {e}")

    if deleted:
        print(f"Deleted {deleted} phantom eval record(s) with no real activity")
    return closed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Close open eval records at session exit")
    parser.add_argument("eval_dir", help="Path to eval-harness/runs directory")
    args = parser.parse_args()

    closed = close_open_evals(args.eval_dir)
    if closed > 0:
        print(f"Closed {closed} open eval record(s)")

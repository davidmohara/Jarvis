#!/usr/bin/env python3
"""
Close any open eval records at session exit.

Marks open evals with status: "incomplete" and abort_reason: "session-exit-normal"
so they're not counted as system failures in the success-rate metric.

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
    now = datetime.now(tz=timezone.utc).isoformat()

    for f in eval_path.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            # Only close if still in-progress
            if data.get("status") == "in-progress":
                data["status"] = "incomplete"
                data["completed"] = now
                data["assessment"]["mechanical"]["abort_reason"] = "session-exit-normal"
                data["assessment"]["mechanical"]["completed"] = False

                with open(f, "w") as file:
                    json.dump(data, file, indent=2)
                closed += 1
        except Exception as e:
            print(f"Error processing {f.name}: {e}")

    return closed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Close open eval records at session exit")
    parser.add_argument("eval_dir", help="Path to eval-harness/runs directory")
    args = parser.parse_args()

    closed = close_open_evals(args.eval_dir)
    if closed > 0:
        print(f"Closed {closed} open eval record(s)")

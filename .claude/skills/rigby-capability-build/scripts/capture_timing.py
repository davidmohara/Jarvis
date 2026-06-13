#!/usr/bin/env python3
"""
Write timing.json for an executor or grader run.

The Agent task notification includes total_tokens and duration_ms once a
subagent completes. Those values are not persisted anywhere else, so Rigby
must capture them inline by invoking this script with the values pulled
from the notification.

Usage:
    python3 -m scripts.capture_timing \\
        --run-dir <path-to-run-N-directory> \\
        --total-tokens 41160 \\
        --duration-ms 108223

Writes <run-dir>/timing.json. Exits 0 on success.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Write timing.json from a subagent task notification")
    parser.add_argument("--run-dir", type=Path, required=True, help="Path to the run-N directory")
    parser.add_argument("--total-tokens", type=int, required=True, help="total_tokens from the task notification")
    parser.add_argument("--duration-ms", type=int, required=True, help="duration_ms from the task notification")
    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Error: run-dir does not exist: {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "total_tokens": args.total_tokens,
        "duration_ms": args.duration_ms,
        "total_duration_seconds": round(args.duration_ms / 1000, 1),
    }

    out = args.run_dir / "timing.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()

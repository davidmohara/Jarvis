#!/usr/bin/env python3
"""
SessionEnd Hook: Eval Record Finalization
Triggered when a Claude Code session ends.
Finds any in-progress eval records and marks them as aborted.
"""

import json
import sys
import fcntl
from pathlib import Path
from datetime import datetime

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str):
    """Log informational message to /tmp/ies-hook-errors.log."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [INFO] {msg}\n")
    except Exception:
        pass


def atomic_write_json(path: Path, data: dict):
    """Write JSON atomically using a temp file + rename, with exclusive lock."""
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        tmp_path.replace(path)
    except Exception as e:
        log_error(f"atomic_write_json failed for {path}: {e}")
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

def main():
    """Main hook logic."""
    if not EVAL_RUNS_DIR.exists():
        return

    # Find all in-progress eval records
    aborted_count = 0
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            if data.get("status") == "in-progress":
                # Mark as aborted
                data["status"] = "aborted"
                data["completed"] = datetime.now().isoformat().replace("+00:00", "Z")

                # Ensure nested structure exists before writing
                if "assessment" not in data:
                    data["assessment"] = {}
                if "mechanical" not in data["assessment"]:
                    data["assessment"]["mechanical"] = {}
                data["assessment"]["mechanical"]["completed"] = False
                data["assessment"]["mechanical"]["abort_reason"] = "session-ended"

                # Write updated record atomically
                atomic_write_json(f, data)
                aborted_count += 1
        except Exception as e:
            log_error(f"Failed to finalize eval record {f}: {e}")

    # Log summary as info, not error
    if aborted_count > 0:
        log_info(f"SessionEnd: Marked {aborted_count} eval records as aborted")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
PostToolUseFailure Hook: Tool Failure Logging
Triggered when a tool call fails.
Logs tool failures to the active eval record for Tier 1 mechanical assessment.
"""

import json
import sys
import os
import fcntl
from pathlib import Path
from datetime import datetime

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(os.environ.get("IES_ROOT", "/Users/davidohara/develop/jarvis"))
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")
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

def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}

def find_active_eval_record(session_id: str) -> Path | None:
    """Find the most recent in-progress eval record for this session."""
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("session_id") == session_id and data.get("status") == "in-progress":
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
    return None

def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract tool failure info from PostToolUseFailure hook
    tool_name = payload.get("tool_name")
    error = payload.get("error")
    duration_ms = payload.get("duration_ms")

    if not tool_name or not error:
        log_error("PostToolUseFailure hook missing tool_name or error")
        return

    # Try to infer session ID - this hook doesn't provide it directly
    # We'll scan for the most recent in-progress record
    eval_path = None
    try:
        if EVAL_RUNS_DIR.exists():
            records = []
            for f in EVAL_RUNS_DIR.glob("eval-*.json"):
                try:
                    with open(f, "r") as file:
                        data = json.load(file)
                    if data.get("status") == "in-progress":
                        records.append((f, data.get("started", "")))
                except Exception:
                    continue

            if records:
                records.sort(key=lambda x: x[1], reverse=True)
                eval_path = records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
        return

    if not eval_path:
        return  # No active eval record, silent exit

    # Read and update eval record
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Increment tool failure count
        eval_record["assessment"]["mechanical"]["tool_failures"] += 1

        # Build failure entry and attach to eval record
        failure_entry = {
            "tool": tool_name,
            "error": str(error),
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        if "tool_failure_log" not in eval_record["assessment"]["mechanical"]:
            eval_record["assessment"]["mechanical"]["tool_failure_log"] = []
        eval_record["assessment"]["mechanical"]["tool_failure_log"].append(failure_entry)

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to update eval record with tool failure: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Record step completion for eval harness (Cowork-compatible)
Called by workflow steps to record their completion status and timing.
Lightweight script (~10-20ms overhead) that updates eval records directly.
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"

def find_most_recent_eval_record(workflow_name: str) -> Path | None:
    """Find the most recent eval record for this workflow (by name, not session_id)."""
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("name") == workflow_name:
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception:
        pass
    return None

def main():
    if len(sys.argv) < 4:
        print("Usage: record-step.py <workflow_name> <step_name> <status> [started_at] [completed_at]")
        sys.exit(1)

    workflow_name = sys.argv[1]
    step_name = sys.argv[2]
    status = sys.argv[3]
    started_at = sys.argv[4] if len(sys.argv) > 4 else None
    completed_at = sys.argv[5] if len(sys.argv) > 5 else None

    # Find the most recent eval record for this workflow
    eval_path = find_most_recent_eval_record(workflow_name)
    if not eval_path:
        # No eval record exists yet - skip silently (workflow may not have eval harness enabled)
        sys.exit(0)

    # Read and update the eval record
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Calculate duration if both timestamps provided
        duration_seconds = None
        if started_at and completed_at:
            try:
                start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                duration_seconds = round((end - start).total_seconds(), 2)
            except Exception:
                pass

        # Create or update step entry
        step_entry = {
            "name": step_name,
            "started": started_at,
            "completed": completed_at,
            "duration_seconds": duration_seconds,
            "status": status,
            "data_sources_used": [],
            "data_source_failures": []
        }

        # Add or update step in eval record
        eval_record["steps"] = [s for s in eval_record.get("steps", []) if s["name"] != step_name]
        eval_record["steps"].append(step_entry)

        # Update mechanical assessment for step completion
        if status == "complete":
            eval_record["assessment"]["mechanical"]["all_steps_finished"] = True

        # Write updated record atomically
        tmp_path = eval_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(eval_record, f, indent=2)
        tmp_path.replace(eval_path)

    except Exception as e:
        # Log error but don't fail the workflow step
        print(f"Warning: Failed to record step completion: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()

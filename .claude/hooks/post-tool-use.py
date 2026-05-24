#!/usr/bin/env python3
"""
PostToolUse Hook: Session Index Capture + Eval Harness Integration
Triggered after every Write or Edit tool call.
1. Reads current session's topic and appends file path to the active topic in session index.
2. Detects state.yaml and step frontmatter writes to update eval records with workflow lifecycle and step timing.
"""

import json
import sys
import os
import fcntl
import yaml
from pathlib import Path
from datetime import datetime

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(os.environ.get("IES_ROOT", "/Users/davidohara/develop/jarvis"))
INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
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

def normalize_path(abs_path: str) -> str:
    """Convert absolute path to relative path from IES root."""
    try:
        path_obj = Path(abs_path)
        # Try to make it relative to IES_ROOT
        return str(path_obj.relative_to(IES_ROOT))
    except ValueError:
        # If not under IES_ROOT, return the absolute path as-is
        return abs_path

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

def infer_trigger(state_data: dict) -> str:
    """Infer trigger from state.yaml content."""
    # state.yaml may have an explicit trigger field
    trigger = state_data.get("trigger")
    if trigger in ("scheduled", "manual", "boot"):
        return trigger
    # Infer from original_request or session context
    original_request = state_data.get("original-request", "").lower()
    if "scheduled" in original_request or "auto" in original_request:
        return "scheduled"
    if "boot" in original_request:
        return "boot"
    return "manual"


def update_eval_record_state_yaml(eval_path: Path, file_path: str, content: str):
    """Update eval record with workflow lifecycle info from state.yaml."""
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Parse the state.yaml content
        state_data = yaml.safe_load(content)
        if not state_data:
            return

        # Update eval record with workflow lifecycle info
        eval_record["type"] = "workflow"
        eval_record["name"] = state_data.get("workflow", "unknown")
        eval_record["trigger"] = infer_trigger(state_data)

        # Update mechanical assessment based on state
        status = state_data.get("status")
        if status == "complete":
            eval_record["assessment"]["mechanical"]["completed"] = True
        elif status in ["in-progress", "not-started"]:
            eval_record["assessment"]["mechanical"]["completed"] = False

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to update eval record from state.yaml: {e}")

def update_eval_record_step_frontmatter(eval_path: Path, file_path: str, content: str):
    """Update eval record with step timing from step frontmatter."""
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Parse YAML frontmatter (between --- markers)
        lines = content.split("\n")
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                if not in_frontmatter:
                    break
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)

        if not frontmatter_lines:
            return

        frontmatter = yaml.safe_load("\n".join(frontmatter_lines))
        if not frontmatter:
            return

        # Extract step name from file path
        step_name = Path(file_path).name

        # Create or update step entry
        step_entry = {
            "name": step_name,
            "started": frontmatter.get("started-at"),
            "completed": frontmatter.get("completed-at"),
            "duration_seconds": None,
            "status": frontmatter.get("status"),
            "data_sources_used": [],
            "data_source_failures": []
        }

        # Calculate duration if both timestamps exist
        if step_entry["started"] and step_entry["completed"]:
            try:
                start = datetime.fromisoformat(step_entry["started"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(step_entry["completed"].replace("Z", "+00:00"))
                step_entry["duration_seconds"] = round((end - start).total_seconds(), 2)
            except Exception:
                pass

        # Add or update step in eval record
        eval_record["steps"] = [s for s in eval_record.get("steps", []) if s["name"] != step_name]
        eval_record["steps"].append(step_entry)

        # Update mechanical assessment for step completion
        if frontmatter.get("status") == "complete":
            # Count completed steps vs total steps (simplified)
            eval_record["assessment"]["mechanical"]["all_steps_finished"] = True

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to update eval record from step frontmatter: {e}")

def check_error_tracking_write(file_path: str, session_id: str):
    """Check if this write is to error-tracking and update eval record."""
    try:
        if "error-tracking/entries" not in file_path:
            return

        eval_path = find_active_eval_record(session_id)
        if not eval_path:
            return

        # Extract error ID from filename
        error_id = Path(file_path).stem

        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Add error ID to mechanical assessment
        if error_id not in eval_record["assessment"]["mechanical"]["error_ids"]:
            eval_record["assessment"]["mechanical"]["error_ids"].append(error_id)

        # Update status to failure if error was logged
        eval_record["status"] = "failure"

        # Write updated record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to check error tracking write: {e}")

def read_index() -> list:
    """Read the current session index."""
    if not INDEX_PATH.exists():
        return []
    try:
        with open(INDEX_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to read index: {e}")
        return []

def write_index(data: list):
    """Write the updated session index atomically."""
    atomic_write_json(INDEX_PATH, data)

def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract tool info
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path")

    # Only process Write and Edit tools
    if tool_name not in ["Write", "Edit"] or not file_path:
        return  # Silent exit for non-matching tools

    # Normalize the file path
    rel_path = normalize_path(file_path)

    # Read current index
    index = read_index()
    if not index:
        log_error("Session index is empty or missing")
        return

    # Get the last (current) session record
    current_session = index[-1]
    current_topic = current_session.get("current_topic")
    topics = current_session.get("topics", [])

    # If no current_topic set, create/use an "unattributed" bucket
    if not current_topic:
        # Find or create unattributed topic
        unattributed = None
        for t in topics:
            if t.get("topic") == "unattributed":
                unattributed = t
                break

        if not unattributed:
            unattributed = {
                "topic": "unattributed",
                "files": [],
                "loops": [],
                "flag": True
            }
            topics.append(unattributed)

        # Add file if not already present (deduplicate)
        if rel_path not in unattributed.get("files", []):
            unattributed["files"].append(rel_path)
    else:
        # Find the topic matching current_topic
        matching_topic = None
        for t in topics:
            if t.get("topic") == current_topic:
                matching_topic = t
                break

        if matching_topic:
            # Add file if not already present (deduplicate)
            if rel_path not in matching_topic.get("files", []):
                matching_topic["files"].append(rel_path)
        else:
            log_error(f"Current topic '{current_topic}' not found in topics list")
            return

    # Write updated index back
    write_index(index)

    # Eval Harness Integration
    # Get session ID for eval record correlation
    session_id = current_session.get("id", "")

    # Check if this is a state.yaml write
    if rel_path.endswith("state.yaml"):
        eval_path = find_active_eval_record(session_id)
        if eval_path:
            # Read the file content
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                update_eval_record_state_yaml(eval_path, rel_path, content)
            except Exception as e:
                log_error(f"Failed to read state.yaml for eval: {e}")

    # Check if this is a step frontmatter write
    elif "/steps/" in rel_path and rel_path.endswith(".md"):
        eval_path = find_active_eval_record(session_id)
        if eval_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                update_eval_record_step_frontmatter(eval_path, rel_path, content)
            except Exception as e:
                log_error(f"Failed to read step frontmatter for eval: {e}")

    # Check if this is an error-tracking write
    check_error_tracking_write(rel_path, session_id)

if __name__ == "__main__":
    main()

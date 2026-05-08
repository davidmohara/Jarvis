#!/usr/bin/env python3
"""
PostToolUse Hook: Session Index Capture
Triggered after every Write or Edit tool call.
Reads current session's topic and appends file path to the active topic in session index.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Configuration
IES_ROOT = Path.home() / "Library" / "CloudStorage" / "OneDrive-Improving" / "IES"
INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass

def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}

def normalize_path(abs_path: str) -> str:
    """Convert absolute OneDrive path to relative path from IES root."""
    try:
        path_obj = Path(abs_path)
        # Try to make it relative to IES_ROOT
        return str(path_obj.relative_to(IES_ROOT))
    except ValueError:
        # If not under IES_ROOT, return the absolute path as-is
        return abs_path

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
    """Write the updated session index."""
    try:
        with open(INDEX_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error(f"Failed to write index: {e}")

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

if __name__ == "__main__":
    main()

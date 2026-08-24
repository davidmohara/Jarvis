#!/usr/bin/env python3
"""
WorkflowStart Hook: Eval Record Creation for All Workflows
Triggered when any workflow begins execution.
Creates an eval record with workflow name, agent, model, and started timestamp.
"""

import json
import sys
import secrets
import string
import fcntl
from pathlib import Path
from datetime import datetime, timezone
import re

# Configuration
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
WORKFLOWS_DIR = IES_ROOT / "workflows"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [WORKFLOW-START] [ERROR] {msg}\n")
    except Exception:
        pass

def log_info(msg: str):
    """Log informational message to /tmp/ies-hook-errors.log."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [WORKFLOW-START] [INFO] {msg}\n")
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

def new_eval_id() -> str:
    """Generate a unique eval ID in the format eval-YYYYMMDDTHHMMSS-XXXXXX."""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"

def infer_session_id() -> str:
    """Attempt to read current session ID from memory/sessions/index.json."""
    try:
        index_path = IES_ROOT / "memory" / "sessions" / "index.json"
        if index_path.exists():
            with open(index_path, "r") as f:
                index = json.load(f)
                if index:
                    return index[-1].get("id", "session-unknown")
    except Exception as e:
        log_error(f"Failed to read session ID: {e}")

    now = datetime.now(timezone.utc)
    return f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"

def read_workflow_metadata(workflow_name: str) -> dict:
    """Read workflow.md frontmatter to extract agent, model, and description."""
    workflow_path = WORKFLOWS_DIR / workflow_name / "workflow.md"
    metadata = {
        "agent": "master",
        "model": "sonnet",
        "description": ""
    }

    if not workflow_path.exists():
        log_error(f"Workflow file not found: {workflow_path}")
        return metadata

    try:
        with open(workflow_path, "r") as f:
            content = f.read()

        # Extract YAML frontmatter
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                yaml_block = content[3:end_marker].strip()
                for line in yaml_block.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "agent":
                            metadata["agent"] = value
                        elif key == "model":
                            metadata["model"] = value
                        elif key == "description":
                            metadata["description"] = value
    except Exception as e:
        log_error(f"Failed to read workflow metadata for {workflow_name}: {e}")

    return metadata

def main():
    """Main hook logic: fire on workflows/*/state.yaml Write."""
    payload = read_stdin()

    # Extract file path from PostToolUse payload
    file_path = payload.get("file_path") or payload.get("path", "")
    if not file_path or "state.yaml" not in file_path:
        # Not a state.yaml file, skip
        return

    # Parse workflow name from path: workflows/{name}/state.yaml
    match = re.search(r"workflows/([^/]+)/state\.yaml", file_path)
    if not match:
        return

    workflow_name = match.group(1)

    # Try to read the state.yaml that was just written to check if it's a workflow start
    try:
        state_path = IES_ROOT / "workflows" / workflow_name / "state.yaml"
        if not state_path.exists():
            return

        with open(state_path, "r") as f:
            import yaml
            try:
                state = yaml.safe_load(f)
            except:
                # YAML parse failed, skip
                return

        # Only create eval if status is 'in-progress' (workflow is starting)
        if state.get("status") != "in-progress":
            return

    except Exception as e:
        log_error(f"Failed to read state.yaml for {workflow_name}: {e}")
        return

    # Read workflow metadata
    metadata = read_workflow_metadata(workflow_name)

    # Ensure eval runs directory exists
    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate eval ID and get session ID
    eval_id = new_eval_id()
    session_id = infer_session_id()

    # Create eval record
    now = datetime.now(timezone.utc)
    eval_record = {
        "id": eval_id,
        "session_id": session_id,
        "workflow": workflow_name,
        "agent": metadata["agent"],
        "model": metadata["model"],
        "started": now.isoformat().replace("+00:00", "Z"),
        "completed": None,
        "duration_seconds": None,
        "status": "in-progress",
        "steps": [],
        "guardrail_outcomes": {},
        "escalations": [],
        "assessment": {
            "success_grade": None,
            "safety_grade": None,
            "context_efficiency": None,
            "guardrail_result": None,
            "controller_feedback": {
                "rating": None,
                "comment": None,
                "timestamp": None
            }
        },
        "context_efficiency": {
            "files_loaded": 0,
            "data_sources_accessed": [],
            "context_size_tokens_estimated": 0
        },
        "notes": f"Auto-captured workflow start: {workflow_name}"
    }

    # Write eval record
    eval_path = EVAL_RUNS_DIR / f"{eval_id}.json"
    atomic_write_json(eval_path, eval_record)

    if eval_path.exists():
        log_info(f"Created eval record for workflow '{workflow_name}' ({eval_id})")
    else:
        log_error(f"Failed to write eval record for workflow '{workflow_name}'")

if __name__ == "__main__":
    main()

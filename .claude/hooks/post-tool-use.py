#!/usr/bin/env python3
"""
PostToolUse Hook: Session Index Capture + Eval Harness Integration
Triggered after every Write or Edit tool call.
1. Reads current session's topic and appends file path to the active topic in session index.
2. Detects state.yaml and step frontmatter writes to update eval records with workflow lifecycle and step timing.
"""

import json
import sys
import fcntl
import hashlib
import re
import secrets
import string
import yaml
from pathlib import Path
from datetime import datetime, timezone

# Derive IES_ROOT from this file's location: .claude/hooks/post-tool-use.py → project root
IES_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SKILL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "skill-runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

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


def new_eval_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def workflow_version_hash(workflow_name: str) -> str | None:
    """Compute a short SHA256 of the workflow.md at execution time."""
    candidate = IES_ROOT / "workflows" / workflow_name / "workflow.md"
    if candidate.exists():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()[:16]
    return None


def skill_version_hash(skill_name: str) -> str | None:
    """Compute a short SHA256 of the skill's SKILL.md at execution time."""
    # Skills live in .claude/skills/ or skills/
    for candidate in [
        IES_ROOT / ".claude" / "skills" / skill_name / "SKILL.md",
        IES_ROOT / "skills" / skill_name / "SKILL.md",
    ]:
        if candidate.exists():
            return hashlib.sha256(candidate.read_bytes()).hexdigest()[:16]
    return None


ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"


def run_assertions(name: str, eval_record: dict) -> dict:
    """Load and evaluate structural assertions for a workflow or skill.

    Returns an updated assessment.structural dict. Returns the original dict
    unchanged if no assertion file exists for the given name.
    """
    structural = eval_record.get("assessment", {}).get("structural", {
        "expected_outputs_written": None,
        "outputs_non_empty": None,
        "assertions_checked": 0,
        "assertions_passed": 0,
        "assertion_results": []
    })

    assertion_file = ASSERTIONS_DIR / f"{name}.json"
    if not assertion_file.exists():
        return structural

    try:
        with open(assertion_file, "r") as f:
            assertion_data = json.load(f)
    except Exception as e:
        log_error(f"run_assertions: failed to load {assertion_file}: {e}")
        return structural

    assertions = assertion_data.get("assertions", [])
    results = []

    for a in assertions:
        check = a.get("check")
        a_id = a.get("id", "unknown")
        description = a.get("description", "")

        # tool_was_called cannot be evaluated at hook time — skip it
        if check == "tool_was_called":
            results.append({
                "assertion": a_id,
                "description": description,
                "passed": None,
                "skipped": True,
                "reason": "tool_was_called not available at hook time"
            })
            continue

        try:
            if check == "file_exists":
                pattern = a.get("path", "")
                matches = list(IES_ROOT.glob(pattern))
                passed = len(matches) > 0
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "file_min_bytes":
                pattern = a.get("path", "")
                min_bytes = a.get("min_bytes", 0)
                matches = list(IES_ROOT.glob(pattern))
                if not matches:
                    passed = False
                else:
                    passed = all(m.stat().st_size >= min_bytes for m in matches)
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "file_contains":
                pattern = a.get("path", "")
                regex = a.get("pattern", "")
                matches = list(IES_ROOT.glob(pattern))
                if not matches:
                    passed = False
                else:
                    found = False
                    for m in matches:
                        try:
                            content = m.read_text(encoding="utf-8", errors="replace")
                            if re.search(regex, content, re.IGNORECASE):
                                found = True
                                break
                        except Exception:
                            pass
                    passed = found
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "file_not_contains":
                pattern = a.get("path", "")
                regex = a.get("pattern", "")
                matches = list(IES_ROOT.glob(pattern))
                if not matches:
                    # No file = no forbidden content = passes
                    passed = True
                else:
                    found_forbidden = False
                    for m in matches:
                        try:
                            content = m.read_text(encoding="utf-8", errors="replace")
                            if re.search(regex, content, re.IGNORECASE):
                                found_forbidden = True
                                break
                        except Exception:
                            pass
                    passed = not found_forbidden
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "yaml_field_equals":
                path = a.get("path", "")
                field = a.get("field", "")
                value = a.get("value")
                yaml_path = IES_ROOT / path
                if not yaml_path.exists():
                    passed = False
                else:
                    try:
                        data = yaml.safe_load(yaml_path.read_text()) or {}
                        passed = data.get(field) == value
                    except Exception:
                        passed = False
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "step_count_gte":
                min_steps = a.get("min_steps", 0)
                passed = len(eval_record.get("steps", [])) >= min_steps
                results.append({"assertion": a_id, "description": description, "passed": passed})

            elif check == "duration_lte":
                max_duration = a.get("max_duration_seconds", float("inf"))
                actual = eval_record.get("duration_seconds", 0)
                passed = actual <= max_duration
                results.append({"assertion": a_id, "description": description, "passed": passed})

            else:
                # Unknown check type — skip it
                results.append({
                    "assertion": a_id,
                    "description": description,
                    "passed": None,
                    "skipped": True,
                    "reason": f"unknown check type: {check}"
                })

        except Exception as e:
            log_error(f"run_assertions: error evaluating {a_id}: {e}")
            results.append({
                "assertion": a_id,
                "description": description,
                "passed": None,
                "skipped": True,
                "reason": f"evaluation error: {e}"
            })

    # Compute summary counts (exclude skipped assertions)
    non_skipped = [r for r in results if not r.get("skipped")]
    checked = len(non_skipped)
    passed_count = sum(1 for r in non_skipped if r.get("passed") is True)

    # Derive aggregate flags from specific check types
    file_exists_results = [
        r for r in non_skipped
        if any(
            a.get("id") == r["assertion"] and a.get("check") == "file_exists"
            for a in assertions
        )
    ]
    file_min_bytes_results = [
        r for r in non_skipped
        if any(
            a.get("id") == r["assertion"] and a.get("check") == "file_min_bytes"
            for a in assertions
        )
    ]

    expected_outputs_written = (
        all(r.get("passed") for r in file_exists_results)
        if file_exists_results else None
    )
    outputs_non_empty = (
        all(r.get("passed") for r in file_min_bytes_results)
        if file_min_bytes_results else None
    )

    structural["assertion_results"] = results
    structural["assertions_checked"] = checked
    structural["assertions_passed"] = passed_count
    structural["expected_outputs_written"] = expected_outputs_written
    structural["outputs_non_empty"] = outputs_non_empty

    return structural


def create_eval_record_from_skill_run(skill_run_data: dict, session_id: str):
    """Create a complete eval record when a skill writes its skill-runs JSON signal file."""
    try:
        EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

        skill_name = skill_run_data.get("skill", "unknown")
        agent = skill_run_data.get("agent", "unknown")
        trigger = skill_run_data.get("trigger", "manual")
        status_raw = skill_run_data.get("status", "success")
        # Normalize status to eval harness values
        status = status_raw if status_raw in ("success", "partial", "failure", "aborted") else "success"

        now = datetime.now(timezone.utc)
        completed_iso = now.isoformat().replace("+00:00", "Z")

        started_raw = skill_run_data.get("started")
        if started_raw:
            try:
                started_dt = datetime.fromisoformat(str(started_raw).replace("Z", "+00:00"))
                started_iso = started_dt.isoformat().replace("+00:00", "Z")
            except ValueError:
                from datetime import timedelta
                started_dt = now - timedelta(seconds=60)
                started_iso = started_dt.isoformat().replace("+00:00", "Z")
        else:
            from datetime import timedelta
            started_dt = now - timedelta(seconds=60)
            started_iso = started_dt.isoformat().replace("+00:00", "Z")

        duration = max(0, round((now - started_dt).total_seconds(), 1))
        eval_id = new_eval_id()
        vhash = skill_version_hash(skill_name)

        record = {
            "id": eval_id,
            "type": "skill",
            "name": skill_name,
            "agent": agent,
            "session_id": session_id,
            "trigger": trigger,
            "started": started_iso,
            "completed": completed_iso,
            "duration_seconds": duration,
            "status": status,
            "steps": [],
            "assessment": {
                "mechanical": {
                    "completed": status in ("success", "partial"),
                    "all_steps_finished": status == "success",
                    "tool_failures": skill_run_data.get("tool_failures", 0),
                    "error_ids": skill_run_data.get("error_ids", [])
                },
                "structural": {
                    "expected_outputs_written": None,
                    "outputs_non_empty": None,
                    "assertions_checked": 0,
                    "assertions_passed": 0,
                    "assertion_results": []
                },
                "grading": {
                    "last_graded": None,
                    "grade": None,
                    "grader_notes": None
                },
                "controller_feedback": {
                    "rating": None,
                    "comment": None,
                    "timestamp": None
                }
            },
            "version_hash": vhash,
            "prior_baseline_id": None,
            "tags": ["cowork-hook", "skill"]
        }

        # Run structural assertions and merge results
        record["assessment"]["structural"] = run_assertions(skill_name, record)

        path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write_json(path, record)
    except Exception as e:
        log_error(f"Failed to create eval record from skill-run signal: {e}")


def create_eval_record_from_state(state_data: dict, session_id: str):
    """Create a complete eval record when state.yaml reaches status: complete
    and no in-progress stub exists (Cowork path — SubagentStart hook never fired).
    """
    try:
        EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

        workflow_name = state_data.get("workflow", "unknown")
        agent = state_data.get("agent", "unknown")
        trigger = infer_trigger(state_data)
        now = datetime.now(timezone.utc)
        completed_iso = now.isoformat().replace("+00:00", "Z")

        # Use session-started time if available; fall back to now-60s
        session_started = state_data.get("session-started")
        if session_started:
            try:
                started_iso = datetime.fromisoformat(
                    str(session_started).replace("Z", "+00:00")
                ).isoformat().replace("+00:00", "Z")
                started_dt = datetime.fromisoformat(str(session_started).replace("Z", "+00:00"))
            except ValueError:
                started_iso = completed_iso
                started_dt = now
        else:
            from datetime import timedelta
            started_dt = now - timedelta(seconds=60)
            started_iso = started_dt.isoformat().replace("+00:00", "Z")

        duration = max(0, round((now - started_dt).total_seconds(), 1))
        eval_id = new_eval_id()
        vhash = workflow_version_hash(workflow_name)

        record = {
            "id": eval_id,
            "type": "workflow",
            "name": workflow_name,
            "agent": agent,
            "session_id": session_id,
            "trigger": trigger,
            "started": started_iso,
            "completed": completed_iso,
            "duration_seconds": duration,
            "status": "success",  # state.yaml complete = mechanical success
            "steps": [],
            "assessment": {
                "mechanical": {
                    "completed": True,
                    "all_steps_finished": True,
                    "tool_failures": 0,
                    "error_ids": []
                },
                "structural": {
                    "expected_outputs_written": None,
                    "outputs_non_empty": None,
                    "assertions_checked": 0,
                    "assertions_passed": 0,
                    "assertion_results": []
                },
                "grading": {
                    "last_graded": None,
                    "grade": None,
                    "grader_notes": None
                },
                "controller_feedback": {
                    "rating": None,
                    "comment": None,
                    "timestamp": None
                }
            },
            "version_hash": vhash,
            "prior_baseline_id": None,
            "tags": ["cowork-hook"]
        }

        # Run structural assertions and merge results
        record["assessment"]["structural"] = run_assertions(workflow_name, record)

        path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write_json(path, record)
    except Exception as e:
        log_error(f"Failed to create eval record from state.yaml: {e}")


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

    # --- Block 1: Session Index Update (best-effort, does not gate Block 2) ---
    session_id = ""
    index = read_index()
    if not index:
        log_error("Session index is empty or missing")
    else:
        current_session = index[-1]
        session_id = current_session.get("id", "")
        current_topic = current_session.get("current_topic")
        topics = current_session.get("topics", [])

        updated_index = True
        if not current_topic:
            # Find or create unattributed bucket
            unattributed = None
            for t in topics:
                if t.get("topic") == "unattributed":
                    unattributed = t
                    break
            if not unattributed:
                unattributed = {"topic": "unattributed", "files": [], "loops": [], "flag": True}
                topics.append(unattributed)
            if rel_path not in unattributed.get("files", []):
                unattributed["files"].append(rel_path)
        else:
            matching_topic = None
            for t in topics:
                if t.get("topic") == current_topic or t.get("name") == current_topic:
                    matching_topic = t
                    break
            if matching_topic:
                if "files" not in matching_topic:
                    matching_topic["files"] = []
                if rel_path not in matching_topic["files"]:
                    matching_topic["files"].append(rel_path)
            else:
                log_error(f"Current topic '{current_topic}' not found in topics list")
                updated_index = False

        if updated_index:
            write_index(index)

    # --- Block 2: Eval Harness Integration (independent of Block 1) ---

    # Check if this is a state.yaml write
    if rel_path.endswith("state.yaml"):
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            log_error(f"Failed to read state.yaml for eval: {e}")
            content = None

        if content:
            eval_path = find_active_eval_record(session_id)
            if eval_path:
                # Claude Code path: close the existing stub
                update_eval_record_state_yaml(eval_path, rel_path, content)
            else:
                # Cowork path: no SubagentStart hook fired — create record on complete
                try:
                    state_data = yaml.safe_load(content) or {}
                    if state_data.get("status") == "complete":
                        create_eval_record_from_state(state_data, session_id)
                except Exception as e:
                    log_error(f"Failed to parse state.yaml for eval creation: {e}")

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

    # Check if this is a skill-run signal write
    elif "eval-harness/skill-runs/" in rel_path and rel_path.endswith(".json"):
        try:
            with open(file_path, "r") as f:
                skill_run_data = json.load(f)
            create_eval_record_from_skill_run(skill_run_data, session_id)
        except Exception as e:
            log_error(f"Failed to create eval record from skill-run write: {e}")

    # Check if this is an error-tracking write
    check_error_tracking_write(rel_path, session_id)

if __name__ == "__main__":
    main()

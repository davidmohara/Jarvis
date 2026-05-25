#!/usr/bin/env python3
"""
SubagentStop Hook: Eval Record Completion + Tier 1 & 2 Assessments
Triggered when a sub-agent returns.
Completes the eval record, runs mechanical assessment, structural assertions,
and error-log correlation.
"""

import json
import sys
import re
import hashlib
import fcntl
import yaml
from pathlib import Path
from datetime import datetime, timezone

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
EVAL_ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"
ERROR_TRACKING_DIR = IES_ROOT / "systems" / "error-tracking" / "entries"
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


def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}

def find_eval_record(agent_id: str, agent_type: str) -> Path | None:
    """Find the eval record stub for this agent by agent_id first, then fallback."""
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        # Primary: match by agent_id (reliable, set by eval-agent-start.py)
        if agent_id:
            for f in EVAL_RUNS_DIR.glob("eval-*.json"):
                try:
                    with open(f, "r") as file:
                        data = json.load(file)
                    if data.get("agent_id") == agent_id and data.get("status") == "in-progress":
                        return f
                except Exception:
                    continue

        # Fallback: match most recent in-progress record for this agent_type
        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("agent") == agent_type and data.get("status") == "in-progress":
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            log_info(f"find_eval_record: agent_id match failed, used fallback for {agent_type}")
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
    return None

def compute_version_hash(file_path: Path) -> str | None:
    """Compute SHA256 hash of a file."""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def compute_version_hash_for_record(eval_record: dict) -> str | None:
    """Locate and hash the workflow.md or SKILL.md for this eval record."""
    name = eval_record.get("name", "")
    eval_type = eval_record.get("type", "agent")

    if not name or eval_type == "agent":
        return None

    if eval_type == "workflow":
        candidate = IES_ROOT / "workflows" / name / "workflow.md"
    else:
        # skill
        candidate = IES_ROOT / ".claude" / "skills" / name / "SKILL.md"

    return compute_version_hash(candidate)

def check_error_correlation(session_id: str, completed_time: datetime) -> list:
    """Check for error entries written during or within 60 seconds after the run."""
    error_ids = []
    try:
        if not ERROR_TRACKING_DIR.exists():
            return error_ids

        # Scan for error entries
        for f in ERROR_TRACKING_DIR.glob("err-*.json"):
            try:
                with open(f, "r") as file:
                    entry = json.load(file)
                
                entry_time = datetime.fromisoformat(entry.get("timestamp", "").replace("Z", "+00:00"))
                time_diff = (entry_time - completed_time).total_seconds()
                
                # Check if error was written during run or within 60 seconds after
                if -300 <= time_diff <= 60:  # During run (up to 5 min before) or within 60s after
                    error_ids.append(entry.get("id"))
            except Exception:
                continue
    except Exception as e:
        log_error(f"Failed to check error correlation: {e}")
    return error_ids

def find_assertion_file(eval_record: dict) -> Path | None:
    """Find the assertion file for a workflow/skill by name, then by agent type."""
    name = eval_record.get("name", "")
    agent = eval_record.get("agent", "")

    # Primary: match by workflow/skill name
    candidate = EVAL_ASSERTIONS_DIR / f"{name}.json"
    if candidate.exists():
        return candidate

    # Fallback: match by agent type (legacy)
    candidate = EVAL_ASSERTIONS_DIR / f"{agent}.json"
    if candidate.exists():
        return candidate

    return None


def run_assertions(eval_record: dict, transcript_path: str = None) -> dict:
    """Run structural assertions for a workflow/skill."""
    results = {
        "expected_outputs_written": None,
        "outputs_non_empty": None,
        "assertions_checked": 0,
        "assertions_passed": 0,
        "assertion_results": []
    }

    assertion_file = find_assertion_file(eval_record)
    if not assertion_file:
        return results

    try:
        with open(assertion_file, "r") as f:
            assertions = json.load(f)

        results["assertions_checked"] = len(assertions.get("assertions", []))

        for assertion in assertions.get("assertions", []):
            check_type = assertion.get("check")
            passed = False
            error_msg = None

            try:
                if check_type == "file_exists":
                    path = assertion.get("path")
                    if path:
                        passed = len(list(IES_ROOT.glob(path))) > 0

                elif check_type == "file_min_bytes":
                    path = assertion.get("path")
                    min_bytes = assertion.get("min_bytes", 0)
                    if path:
                        matches = list(IES_ROOT.glob(path))
                        if matches:
                            passed = matches[0].stat().st_size >= min_bytes

                elif check_type == "file_contains":
                    path = assertion.get("path")
                    pattern = assertion.get("pattern")
                    if path and pattern:
                        matches = list(IES_ROOT.glob(path))
                        if matches:
                            content = matches[0].read_text()
                            passed = re.search(pattern, content) is not None

                elif check_type == "yaml_field_equals":
                    path = assertion.get("path")
                    field = assertion.get("field")
                    value = assertion.get("value")
                    if path and field:
                        matches = list(IES_ROOT.glob(path))
                        if matches:
                            data = yaml.safe_load(matches[0].read_text())
                            passed = data.get(field) == value

                elif check_type == "file_not_contains":
                    path = assertion.get("path")
                    pattern = assertion.get("pattern")
                    if path and pattern:
                        matches = list(IES_ROOT.glob(path))
                        if matches:
                            content = matches[0].read_text()
                            passed = re.search(pattern, content) is None
                        else:
                            passed = True  # no file = nothing to contain

                elif check_type == "step_count_gte":
                    min_count = assertion.get("min_count", 1)
                    completed_steps = [
                        s for s in eval_record.get("steps", [])
                        if s.get("status") == "success"
                    ]
                    passed = len(completed_steps) >= min_count

                elif check_type == "duration_lte":
                    max_seconds = assertion.get("max_seconds", 0)
                    duration = eval_record.get("duration_seconds")
                    if duration is not None and max_seconds > 0:
                        passed = duration <= max_seconds

                elif check_type == "tool_was_called":
                    tool_pattern = assertion.get("tool_pattern", "")
                    if tool_pattern and transcript_path:
                        try:
                            content = Path(transcript_path).read_text(errors="replace")
                            passed = re.search(tool_pattern, content) is not None
                        except Exception:
                            passed = False

            except Exception as e:
                error_msg = str(e)
                log_error(f"Assertion check failed [{check_type}]: {e}")

            results["assertion_results"].append({
                "assertion": assertion.get("description", check_type),
                "passed": passed,
                "error": error_msg
            })

            if passed:
                results["assertions_passed"] += 1

        # Derive overall structural flags
        results["expected_outputs_written"] = results["assertions_passed"] > 0
        results["outputs_non_empty"] = results["assertions_passed"] == results["assertions_checked"]

    except Exception as e:
        log_error(f"Failed to run assertions: {e}")

    return results

def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract agent info from SubagentStop hook
    agent_id = payload.get("agent_id")
    agent_type = payload.get("agent_type")
    agent_transcript_path = payload.get("agent_transcript_path")
    last_assistant_message = payload.get("last_assistant_message")

    if not agent_id or not agent_type:
        log_error("SubagentStop hook missing agent_id or agent_type")
        return

    # Find the corresponding eval record stub
    eval_record_path = find_eval_record(agent_id, agent_type)
    if not eval_record_path:
        log_error(f"No eval record found for agent {agent_type} ({agent_id})")
        return

    # Read the stub
    try:
        with open(eval_record_path, "r") as f:
            eval_record = json.load(f)
    except Exception as e:
        log_error(f"Failed to read eval record: {e}")
        return

    # Complete the record
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(eval_record["started"].replace("Z", "+00:00"))
    duration_seconds = (now - started).total_seconds()

    eval_record["completed"] = now.isoformat().replace("+00:00", "Z")
    eval_record["duration_seconds"] = round(duration_seconds, 2)

    # Store transcript path and last message for deep analysis
    if agent_transcript_path:
        eval_record["agent_transcript_path"] = agent_transcript_path
    if last_assistant_message:
        eval_record["last_assistant_message"] = last_assistant_message

    # Tier 1: Mechanical Assessment
    # Read existing mechanical state built up by post-tool-use.py and eval-tool-failure.py
    existing_mechanical = eval_record.get("assessment", {}).get("mechanical", {})
    completed = existing_mechanical.get("completed")  # set by post-tool-use.py from state.yaml
    all_steps_finished = existing_mechanical.get("all_steps_finished")  # set by post-tool-use.py
    tool_failures = existing_mechanical.get("tool_failures", 0)  # incremented by eval-tool-failure.py
    existing_error_ids = existing_mechanical.get("error_ids", [])

    # Merge with error-log correlation (new errors in last 60 seconds)
    correlated_errors = check_error_correlation(eval_record.get("session_id", ""), now)
    all_error_ids = list(set(existing_error_ids + correlated_errors))

    # Auto-negative feedback signal when errors are correlated (don't override explicit feedback)
    if all_error_ids:
        existing_feedback = eval_record.get("assessment", {}).get("controller_feedback", {})
        if existing_feedback.get("rating") is None:
            eval_record["assessment"]["controller_feedback"].update({
                "rating": "negative",
                "comment": f"error-log-correlated: {', '.join(str(e) for e in all_error_ids)}",
                "timestamp": now.isoformat().replace("+00:00", "Z")
            })

    # If completed is still None (no state.yaml written — skill run, not workflow)
    # treat as completed=True unless there were failures
    if completed is None:
        completed = (tool_failures == 0 and len(all_error_ids) == 0)
    if all_steps_finished is None:
        all_steps_finished = True  # skills have no steps

    # Derive status from actual state (per plan spec):
    # error entries = failure; tool failures + completed = partial; not completed = aborted
    if all_error_ids:
        status = "failure"
    elif not completed:
        status = "aborted"
    elif tool_failures > 0 or not all_steps_finished:
        status = "partial"
    else:
        status = "success"

    eval_record["status"] = status
    eval_record["assessment"]["mechanical"] = {
        "completed": completed,
        "all_steps_finished": all_steps_finished,
        "tool_failures": tool_failures,
        "error_ids": all_error_ids
    }

    # Tier 2: Structural Assertions — looked up by workflow/skill name, not agent type
    assertion_results = run_assertions(eval_record, agent_transcript_path)
    eval_record["assessment"]["structural"] = assertion_results

    # Compute version hash from workflow.md or SKILL.md
    eval_record["version_hash"] = compute_version_hash_for_record(eval_record)

    # Write updated eval record atomically
    atomic_write_json(eval_record_path, eval_record)

if __name__ == "__main__":
    main()

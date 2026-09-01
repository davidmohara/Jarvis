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
from pathlib import Path
from datetime import datetime, timezone

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
EVAL_ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"
ERROR_TRACKING_DIR = IES_ROOT / "systems" / "error-tracking" / "entries"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

# Vendored PyYAML (see systems/eval-harness/vendor/yaml/LICENSE) goes first on
# sys.path so this hook never depends on pip/pyyaml being installed on the
# host — checked in ahead of any environment copy of the real package.
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
import yaml
try:
    from token_usage import usage_between
except Exception:
    usage_between = None
try:
    from hook_utils import find_parent_record_with_subagent
except Exception:
    find_parent_record_with_subagent = None
try:
    import assertion_checks as _assertion_checks
except Exception:
    _assertion_checks = None

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


def invoke_step_complete_hooks(eval_record: dict, transcript_path: str, ies_root: Path, workflow_name: str = None):
    import subprocess

    # Determine which workflow's steps to process
    workflow_to_process = workflow_name or eval_record.get("name") or "boot"
    steps_dir = ies_root / "workflows" / workflow_to_process / "steps"

    if not steps_dir.exists():
        log_info(f"No steps directory found for workflow '{workflow_to_process}', skipping step-complete hooks")
        return

    log_info(f"invoke_step_complete_hooks: processing steps for workflow '{workflow_to_process}' from {steps_dir}")

    # Validate and resolve transcript path
    # The agent_transcript_path from SubagentStop hook might point to a non-existent subagent transcript.
    # Instead, we use the agent's full transcript which was passed to us.
    effective_transcript_path = transcript_path if transcript_path and Path(transcript_path).exists() else None

    if effective_transcript_path:
        log_info(f"invoke_step_complete_hooks: using provided transcript_path: {effective_transcript_path}")
    else:
        if transcript_path:
            log_info(f"invoke_step_complete_hooks: provided path doesn't exist: {transcript_path}")
        log_info(f"invoke_step_complete_hooks: step-complete.py will attempt fallback transcript resolution")

    for step_file in sorted(steps_dir.glob("step-*.md")):
        try:
            with open(step_file) as f:
                content = f.read()
            frontmatter = extract_frontmatter_block(content)
            step_data = yaml.safe_load(frontmatter) or {}
            if step_data.get("status") != "complete":
                continue

            payload = {
                "step_file_path": str(step_file),
                "step_content": content,
                "transcript_path": effective_transcript_path,
                "session_id": eval_record.get("session_id", ""),
                "workflow_name": workflow_to_process
            }
            subprocess.run(
                ["python3", str(ies_root / ".claude" / "hooks" / "step-complete.py")],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception as e:
            log_error(f"step-complete failed for {step_file.name}: {e}")


def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}


def extract_frontmatter_block(content: str) -> str:
    """Strip the leading/trailing `---` markers IES uses to wrap both step
    frontmatter and state.yaml files. Passing the raw file (with a trailing
    marker present) straight to yaml.safe_load() parses as two YAML
    documents — a real one plus an empty one after the closing marker — and
    raises ComposerError. If there's no second marker, returns content as-is
    (single-document files parse fine unmodified)."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return "\n".join(lines[1:])

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


def read_fairness_frontmatter(name: str, eval_type: str) -> dict:
    """Read fairness: block from SKILL.md or workflow.md YAML frontmatter."""
    try:
        if eval_type == "workflow":
            candidates = [IES_ROOT / "workflows" / name / "workflow.md"]
        else:
            candidates = [
                IES_ROOT / ".claude" / "skills" / name / "SKILL.md",
                IES_ROOT / "skills" / name / "SKILL.md",
            ]
        for path in candidates:
            if not path.exists():
                continue
            content = path.read_text()
            if not content.startswith("---"):
                continue
            end_idx = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_idx])
            return (fm or {}).get("fairness", {})
    except Exception as e:
        log_error(f"read_fairness_frontmatter failed for {name}: {e}")
    return {}


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
    if _assertion_checks is None:
        return None
    name = eval_record.get("name", "")
    agent = eval_record.get("agent", "")
    return _assertion_checks.find_assertion_file(EVAL_ASSERTIONS_DIR, name, agent)


def run_assertions(eval_record: dict, transcript_path: str = None) -> dict:
    """Run assertions for a workflow/skill.

    Thin delegator to the canonical implementation in assertion_checks.py,
    shared with post-tool-use.py and grade_skill_run.py. Preserves this
    function's original return shape (expected_outputs_written /
    outputs_non_empty / assertions_checked / assertions_passed /
    assertion_results) for existing callers in this file.
    """
    results = {
        "expected_outputs_written": None,
        "outputs_non_empty": None,
        "assertions_checked": 0,
        "assertions_passed": 0,
        "assertion_results": []
    }

    if _assertion_checks is None:
        log_error("run_assertions: assertion_checks module unavailable, skipping")
        return results

    name = eval_record.get("name", "")
    agent = eval_record.get("agent", "")

    return _assertion_checks.run_assertions(
        assertions_dir=EVAL_ASSERTIONS_DIR,
        name=name,
        eval_record=eval_record,
        ies_root=IES_ROOT,
        agent=agent,
        transcript_path=transcript_path,
        yaml_module=yaml,
        log_error=log_error,
    )

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

    # Real token usage for the whole subagent run, pulled from its own transcript
    # (a subagent's transcript is entirely in-scope — no per-step slicing needed).
    if usage_between and agent_transcript_path:
        try:
            usage = usage_between(
                agent_transcript_path,
                eval_record.get("started"),
                eval_record["completed"],
                exclude_sidechain=False,
            )
            if usage:
                eval_record["model"] = usage["model"]
                eval_record["total_tokens_input"] = usage["tokens_input"]
                eval_record["total_tokens_output"] = usage["tokens_output"]
                eval_record["total_cost_usd"] = usage["cost_usd"]
        except Exception as e:
            log_error(f"Failed to compute agent token usage: {e}")

    # Invoke step-complete hooks for all workflows/agents that have steps
    # This populates per-step token data from the agent transcript
    try:
        workflow_name = eval_record.get("name")
        if workflow_name:
            # Check if this workflow has a steps directory
            workflow_steps_dir = IES_ROOT / "workflows" / workflow_name / "steps"
            if workflow_steps_dir.exists():
                log_info(f"Found step directory for workflow '{workflow_name}', invoking step-complete hooks")
                invoke_step_complete_hooks(eval_record, agent_transcript_path, IES_ROOT)
                # Re-read eval record to get step data updated by hooks
                with open(eval_record_path, "r") as f:
                    eval_record = json.load(f)
    except Exception as e:
        log_error(f"step-complete hooks failed: {e}")

    # Fallback: Estimate cost if no real transcript data available (ensures all evals have cost)
    if eval_record.get("total_cost_usd") is None:
        try:
            # Workflow-specific token estimates
            workflow_estimates = {
                "daily-review": {"input": 5000, "output": 2000},
                "morning-briefing": {"input": 8000, "output": 3000},
                "general-purpose": {"input": 10000, "output": 4000},
                "system-eval": {"input": 3000, "output": 1000},
                "fork": {"input": 5000, "output": 2000},
                "boot": {"input": 6000, "output": 2500},
                "plaud-ingest": {"input": 7000, "output": 3000},
                "watchtower-weekly": {"input": 12000, "output": 5000},
            }

            # Load pricing
            pricing_file = IES_ROOT / "systems" / "eval-harness" / "model-pricing.json"
            pricing = {}
            if pricing_file.exists():
                with open(pricing_file) as f:
                    pricing = json.load(f).get("models", {})

            if pricing:
                model = eval_record.get("model", "sonnet")
                if model not in pricing:
                    model = "sonnet"

                rates = pricing.get(model, {"input_per_mtok": 3.00, "output_per_mtok": 15.00})
                workflow = eval_record.get("name", "fork")
                estimate = workflow_estimates.get(workflow, workflow_estimates["fork"])

                input_cost = (estimate["input"] / 1_000_000) * rates.get("input_per_mtok", 3.00)
                output_cost = (estimate["output"] / 1_000_000) * rates.get("output_per_mtok", 15.00)

                eval_record["total_cost_usd"] = round(input_cost + output_cost, 6)
                eval_record["cost_estimation_note"] = f"estimated based on {workflow} workflow type"
                if not eval_record.get("model"):
                    eval_record["model"] = model
        except Exception as e:
            log_error(f"Failed to estimate eval cost: {e}")

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

    # Populate bias_assessment from capability frontmatter
    name = eval_record.get("name", "")
    eval_type = eval_record.get("type", "agent")
    bias_assessment = eval_record.get("assessment", {}).get("bias_assessment", {
        "applicable": False,
        "protected_attributes": [],
        "fairness_metric": None,
        "demographic_coverage_verified": False,
        "adversarial_inputs_tested": False,
        "bias_detected": False,
        "bias_flags": [],
        "remediation_status": "none"
    })
    if name and eval_type != "agent":
        fairness_fm = read_fairness_frontmatter(name, eval_type)
        if fairness_fm.get("applicable"):
            bias_assessment["applicable"] = True
            bias_assessment["protected_attributes"] = fairness_fm.get("protected_attributes", [])
            bias_assessment["fairness_metric"] = fairness_fm.get("metric")
    eval_record["assessment"]["bias_assessment"] = bias_assessment

    # Tier 2: Structural Assertions — looked up by workflow/skill name, not agent type
    assertion_results = run_assertions(eval_record, agent_transcript_path)
    eval_record["assessment"]["structural"] = assertion_results

    # Compute version hash from workflow.md or SKILL.md
    eval_record["version_hash"] = compute_version_hash_for_record(eval_record)

    # Write updated eval record atomically
    atomic_write_json(eval_record_path, eval_record)

    # Roll this subagent's model/tokens/cost/timing into the parent turn-level
    # eval record's subagents[] entry, if eval-turn-start.py opened one for
    # this session and eval-agent-start.py linked this agent_id into it.
    # Looked up by "which record's subagents[] already names this agent_id"
    # (find_parent_record_with_subagent), not by "which turn record is open
    # right now" (the old find_unambiguous_open_turn_record) — the latter
    # loses the write whenever the parent's own Stop hook closes it before
    # this subagent's SubagentStop hook runs, which is exactly what happened
    # to a2d85012d16ba3d83 in eval-20260828T154249-UQX5N6.
    if find_parent_record_with_subagent:
        try:
            parent_path = find_parent_record_with_subagent(eval_record.get("session_id", ""), agent_id)
            if parent_path and parent_path != eval_record_path:
                with open(parent_path, "r") as f:
                    parent = json.load(f)
                for entry in parent.get("subagents", []):
                    if entry.get("agent_id") == agent_id:
                        entry["completed"] = eval_record.get("completed")
                        entry["model"] = eval_record.get("model")
                        entry["tokens_input"] = eval_record.get("total_tokens_input")
                        entry["tokens_output"] = eval_record.get("total_tokens_output")
                        entry["cost_usd"] = eval_record.get("total_cost_usd")
                        entry["duration_seconds"] = eval_record.get("duration_seconds")
                        break
                atomic_write_json(parent_path, parent)
        except Exception as e:
            log_error(f"Failed to roll up subagent {agent_id} into open turn record: {e}")

if __name__ == "__main__":
    main()

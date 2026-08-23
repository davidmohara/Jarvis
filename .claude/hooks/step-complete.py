#!/usr/bin/env python3
"""
Step-Complete Hook: Per-Step Token Extraction + Guardrail Validation
Triggered when a workflow step completes (status: complete written to frontmatter).

Responsibilities:
1. Extract real token usage for this specific step from transcript
2. Run guardrail checkpoint for this step
3. Decide: pass / flag / escalate (punch-out)
4. Update eval record with step results
5. Return punch-out signal if workflow should halt for controller review
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
GUARDRAILS_DIR = IES_ROOT / "workflows" / "boot" / "guardrails"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
import yaml
try:
    from token_usage import usage_between
except Exception:
    usage_between = None


def log_error(msg: str):
    """Log error without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [STEP-COMPLETE] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str):
    """Log info message."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [STEP-COMPLETE] [INFO] {msg}\n")
    except Exception:
        pass


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from step file."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}

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
        return {}

    try:
        return yaml.safe_load("\n".join(frontmatter_lines)) or {}
    except Exception as e:
        log_error(f"Failed to parse frontmatter: {e}")
        return {}


def find_active_eval_record(session_id: str) -> Path | None:
    """Find in-progress eval record for this session."""
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("session_id") == session_id:
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")

    return None


def find_session_transcript(session_id: str) -> Path | None:
    """Fallback: find the session's main transcript JSONL if transcript_path not provided."""
    try:
        claude_dir = Path.home() / ".claude" / "projects"
        for project_dir in claude_dir.glob("*/*/subagents"):
            # Look for session transcript with matching session_id in filename or content
            for transcript in project_dir.glob("*.jsonl"):
                if session_id in str(transcript):
                    return transcript
        log_info(f"Could not find session transcript for {session_id}")
    except Exception as e:
        log_error(f"Failed to find session transcript: {e}")
    return None


def extract_step_tokens(transcript_path: str, step_started: str, step_completed: str, step_name: str) -> dict:
    """Extract real token usage for this step's time window."""
    result = {
        "tokens_input": None,
        "tokens_output": None,
        "cost_usd": None,
        "model": None,
        "extraction_error": None
    }

    # Validate inputs
    if not step_started or not step_completed:
        result["extraction_error"] = "missing_timestamps"
        log_error(f"Token extraction skipped for {step_name}: missing timestamps")
        return result

    # If usage_between unavailable, log it once
    if not usage_between:
        result["extraction_error"] = "usage_between_unavailable"
        log_error(f"Token extraction skipped for {step_name}: usage_between module not imported")
        return result

    # If transcript_path missing, log and return
    if not transcript_path:
        result["extraction_error"] = "transcript_path_missing"
        log_info(f"Token extraction skipped for {step_name}: transcript_path not provided in payload")
        return result

    try:
        log_info(f"Attempting token extraction for {step_name} from {transcript_path}")
        log_info(f"Step time window: {step_started} to {step_completed}")
        usage = usage_between(transcript_path, step_started, step_completed, exclude_sidechain=False)

        if usage:
            result["tokens_input"] = usage.get("tokens_input")
            result["tokens_output"] = usage.get("tokens_output")
            result["cost_usd"] = usage.get("cost_usd")
            result["model"] = usage.get("model")
            log_info(f"SUCCESS: Extracted tokens for {step_name}: {result['tokens_input']} input, {result['tokens_output']} output, model={result['model']}, cost=${result['cost_usd']:.4f}")
        else:
            result["extraction_error"] = "usage_between_no_data"
            log_info(f"Token extraction completed for {step_name} but no usage data found in strict time window (using lenient fallback)")
    except Exception as e:
        result["extraction_error"] = str(e)
        log_error(f"EXCEPTION during token extraction for {step_name}: {e}")

    return result


def run_step_guardrail_checkpoint(step_name: str, step_frontmatter: dict, eval_record: dict) -> dict:
    """Run guardrail validation for this step.

    Four possible outcomes:
    - pass: Step succeeded, continue
    - flag: Step has warnings but is usable, continue
    - retry: Step incomplete, send back to model to finish (don't punch out)
    - escalate: Critical issue model can't fix, punch out to controller
    """
    # Load guardrail rules first to get checkpoint_name if defined
    guardrail_file = GUARDRAILS_DIR / f"{step_name}.json"
    checkpoint_name = f"{step_name}-checkpoint"  # default
    guardrail_rules = {}

    if guardrail_file.exists():
        try:
            with open(guardrail_file, "r") as f:
                guardrail_rules = json.load(f)
                # Use checkpoint_name from guardrails file if defined
                if "checkpoint_name" in guardrail_rules:
                    checkpoint_name = guardrail_rules["checkpoint_name"]
        except Exception as e:
            log_error(f"Failed to load guardrail rules for {step_name}: {e}")

    result = {
        "checkpoint_name": checkpoint_name,
        "result": "pass",
        "reason": "Step completed successfully",
        "escalated_to_human": False,
        "validation_errors": [],
        "retry_feedback": None  # If result=retry, include feedback for model
    }

    # CRITICAL CHECK: step status must be complete
    if step_frontmatter.get("status") != "complete":
        result["result"] = "escalate"
        result["escalated_to_human"] = True
        result["reason"] = f"CRITICAL: Step status is '{step_frontmatter.get('status')}', expected 'complete'"
        result["validation_errors"].append(f"status_mismatch: {step_frontmatter.get('status')}")
        return result

    # CRITICAL CHECK: timestamps must exist (needed for token extraction)
    if not step_frontmatter.get("started-at") or not step_frontmatter.get("completed-at"):
        result["result"] = "escalate"
        result["escalated_to_human"] = True
        result["reason"] = "CRITICAL: Step missing started-at or completed-at timestamp"
        result["validation_errors"].append("missing_timestamps")
        return result

    # Check for outputs (incomplete step → retry, don't escalate)
    outputs = step_frontmatter.get("outputs", {})
    if not outputs:
        result["result"] = "retry"
        result["reason"] = "Step incomplete: no outputs recorded"
        result["retry_feedback"] = "Re-execute step to completion. Outputs must be recorded in frontmatter."
        result["validation_errors"].append("no_outputs")
        return result
    else:
        # Step has outputs — that's good
        result["reason"] = f"Step completed with {len(outputs)} output fields recorded"

    # Apply step-specific guardrail rules if they exist (already loaded above)
    if guardrail_rules:
        try:
            # Run each rule
            for rule in guardrail_rules.get("rules", []):
                rule_type = rule.get("type")
                rule_name = rule.get("name", "unknown")
                is_critical = rule.get("critical", False)
                is_retry = rule.get("retry_on_missing", False)  # Send back to model if missing

                # Example rule: check_field_exists
                if rule_type == "check_field_exists":
                    field = rule.get("field")
                    if field not in outputs:
                        result["validation_errors"].append(f"missing_field: {field}")
                        if is_retry:
                            # Incomplete field → retry (don't punch out)
                            result["result"] = "retry"
                            result["reason"] = f"Step incomplete: missing required field '{field}'"
                            result["retry_feedback"] = f"Re-execute step. Missing output field: {field}"
                            break
                        elif is_critical:
                            # Critical field missing and NOT retryable → escalate
                            result["result"] = "escalate"
                            result["escalated_to_human"] = True
                            result["reason"] = f"CRITICAL: Missing required field '{field}' (not retryable)"
                            break
                        else:
                            result["result"] = "flag"

                # Example rule: check_field_not_empty
                elif rule_type == "check_field_not_empty":
                    field = rule.get("field")
                    value = outputs.get(field)
                    if not value:
                        result["validation_errors"].append(f"empty_field: {field}")
                        if is_retry:
                            # Empty field → retry (send back to model)
                            result["result"] = "retry"
                            result["reason"] = f"Step incomplete: empty field '{field}'"
                            result["retry_feedback"] = f"Re-execute step. Field '{field}' is empty, must be populated."
                            break
                        elif is_critical:
                            # Critical and empty → escalate
                            result["result"] = "escalate"
                            result["escalated_to_human"] = True
                            result["reason"] = f"CRITICAL: Required field '{field}' is empty"
                            break
                        else:
                            result["result"] = "flag"

                # Only CRITICAL (non-retryable) issues can escalate
                elif rule_type == "escalate_if" and is_critical:
                    condition = rule.get("condition")
                    if condition == "data_integrity_failure":
                        result["result"] = "escalate"
                        result["escalated_to_human"] = True
                        result["reason"] = f"CRITICAL: {rule_name}"
                        break

        except Exception as e:
            log_error(f"Failed to load guardrail rules for {step_name}: {e}")

    return result


def update_eval_record_with_step_completion(eval_path: Path, step_name: str, frontmatter: dict,
                                            token_data: dict, guardrail_result: dict):
    """Update eval record with step completion data."""
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Find or create step entry
        step_entry = None
        for step in eval_record.get("steps", []):
            if step.get("name") == step_name:
                step_entry = step
                break

        if not step_entry:
            step_entry = {"name": step_name}
            if "steps" not in eval_record:
                eval_record["steps"] = []
            eval_record["steps"].append(step_entry)

        # Update step with timing and frontmatter
        step_entry["started"] = frontmatter.get("started-at")
        step_entry["completed"] = frontmatter.get("completed-at")
        step_entry["status"] = frontmatter.get("status")

        # Update with extracted token data
        if token_data.get("tokens_input") is not None:
            step_entry["tokens_input"] = token_data["tokens_input"]
        if token_data.get("tokens_output") is not None:
            step_entry["tokens_output"] = token_data["tokens_output"]
        if token_data.get("cost_usd") is not None:
            step_entry["cost_usd"] = token_data["cost_usd"]
        if token_data.get("model"):
            step_entry["model"] = token_data["model"]

        # Calculate duration
        if step_entry.get("started") and step_entry.get("completed"):
            try:
                start = datetime.fromisoformat(step_entry["started"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(step_entry["completed"].replace("Z", "+00:00"))
                step_entry["duration_seconds"] = round((end - start).total_seconds(), 2)
            except Exception:
                pass

        # Add guardrail checkpoint result
        if "guardrails" not in eval_record:
            eval_record["guardrails"] = []

        guardrail_entry = {
            "name": guardrail_result["checkpoint_name"],
            "after_step": step_name,
            "result": guardrail_result["result"],
            "reason": guardrail_result["reason"],
            "escalated_to_human": guardrail_result["escalated_to_human"],
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "validation_errors": guardrail_result.get("validation_errors", [])
        }
        eval_record["guardrails"].append(guardrail_entry)

        # Handle different checkpoint outcomes
        if guardrail_result["result"] == "retry":
            # Step is incomplete, queue for retry (don't punch out to controller)
            eval_record["retry_signal"] = {
                "step": step_name,
                "checkpoint": guardrail_result["checkpoint_name"],
                "reason": guardrail_result["reason"],
                "feedback": guardrail_result.get("retry_feedback"),
                "attempt_number": eval_record.get("retry_signal", {}).get("attempt_number", 0) + 1,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            log_info(f"RETRY: {step_name} is incomplete. Feedback: {guardrail_result.get('retry_feedback')}")

        elif guardrail_result["result"] == "escalate":
            # Critical issue, punch out to controller
            eval_record["punch_out_signal"] = {
                "step": step_name,
                "checkpoint": guardrail_result["checkpoint_name"],
                "reason": guardrail_result["reason"],
                "awaiting_controller_decision": True,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            log_info(f"PUNCH-OUT at {step_name}: {guardrail_result['reason']}")

        # Write updated record atomically
        with open(eval_path, "w") as f:
            json.dump(eval_record, f, indent=2)

        log_info(f"Updated eval record for step: {step_name}")

    except Exception as e:
        log_error(f"Failed to update eval record: {e}")


def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}


def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract payload info
    step_file_path = payload.get("step_file_path")
    step_content = payload.get("step_content")
    transcript_path = payload.get("transcript_path")
    session_id = payload.get("session_id")

    if not step_file_path or not step_content:
        log_error("Missing step_file_path or step_content in payload")
        return

    # Extract step name from path
    step_name = Path(step_file_path).stem

    # Parse step frontmatter
    frontmatter = extract_frontmatter(step_content)
    if not frontmatter or frontmatter.get("status") != "complete":
        log_info(f"Step {step_name} not yet complete, skipping")
        return

    # Find active eval record
    eval_path = find_active_eval_record(session_id)
    if not eval_path:
        log_error(f"No active eval record found for session {session_id}")
        return

    log_info(f"Processing step completion: {step_name}")

    # Resolve transcript path (fallback to finding session transcript if not provided)
    effective_transcript_path = transcript_path
    if not effective_transcript_path and session_id:
        log_info(f"transcript_path not provided, attempting fallback lookup for session {session_id}")
        fallback = find_session_transcript(session_id)
        if fallback:
            effective_transcript_path = str(fallback)
            log_info(f"Found session transcript via fallback: {effective_transcript_path}")

    # Extract tokens for this step
    log_info(f"Starting token extraction: transcript_available={effective_transcript_path is not None}, step={step_name}")
    token_data = extract_step_tokens(
        effective_transcript_path,
        frontmatter.get("started-at"),
        frontmatter.get("completed-at"),
        step_name
    )
    if token_data.get("extraction_error"):
        log_info(f"Token extraction ended with: {token_data['extraction_error']}")

    # Run guardrail checkpoint
    guardrail_result = run_step_guardrail_checkpoint(step_name, frontmatter, {})

    # Update eval record
    update_eval_record_with_step_completion(eval_path, step_name, frontmatter, token_data, guardrail_result)

    # Output result for workflow coordination
    output = {
        "step": step_name,
        "status": "complete",
        "guardrail_result": guardrail_result["result"],
        "punch_out": guardrail_result["escalated_to_human"],
        "tokens_input": token_data.get("tokens_input"),
        "tokens_output": token_data.get("tokens_output")
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()

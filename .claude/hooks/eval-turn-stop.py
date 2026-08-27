#!/usr/bin/env python3
"""
Stop Hook: Close Out Turn-Level Eval Record

Fires at the end of every assistant turn. If eval-turn-start.py opened a
turn-level eval record this session (monitoring.active) AND the monitored
workflow's state.yaml has reached a terminal status (complete/aborted/
blocked), finalize the record: completed timestamp, duration, final status,
structural assertions, version hash.

If state.yaml is still in-progress or awaiting-input (the workflow will
continue in a later turn — same pattern plaud-ingest uses for its speaker-ID
pause), leave the record open. The next turn's Stop event will re-check it.

If no turn-level eval was ever opened this session, this hook does nothing —
no stub, no partial record, per spec.
"""

import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

_IES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness"))
import yaml
from hook_utils import (
    IES_ROOT, log_error, log_info, atomic_write_json, read_stdin,
    infer_session_id, find_open_turn_record,
)
try:
    from token_usage import usage_between
except Exception:
    usage_between = None

TAG = "TURN-STOP"
ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"

TERMINAL_STATUSES = {"complete", "aborted", "blocked"}


def extract_frontmatter_block(content: str) -> str:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return "\n".join(lines[1:])


def read_state_yaml(rel_path: str) -> dict:
    path = IES_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(extract_frontmatter_block(path.read_text())) or {}
    except Exception as e:
        log_error(f"Failed to read {path}: {e}", TAG)
        return {}


def compute_version_hash(name: str) -> str | None:
    candidate = IES_ROOT / "workflows" / name / "workflow.md"
    if candidate.exists():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    return None


def run_assertions(name: str, eval_record: dict) -> dict:
    """Same check-type set as post-tool-use.py's run_assertions, kept
    independent rather than imported to avoid coupling this hook's control
    flow to post-tool-use.py's larger session-index responsibilities."""
    structural = eval_record.get("assessment", {}).get("structural", {})
    assertion_file = ASSERTIONS_DIR / f"{name}.json"
    if not assertion_file.exists():
        return structural

    try:
        import json
        with open(assertion_file, "r") as f:
            assertion_data = json.load(f)
    except Exception as e:
        log_error(f"Failed to load {assertion_file}: {e}", TAG)
        return structural

    results = []
    for a in assertion_data.get("assertions", []):
        check = a.get("check")
        a_id = a.get("id", "unknown")
        description = a.get("description", "")
        passed = None
        try:
            if check == "file_exists":
                passed = len(list(IES_ROOT.glob(a.get("path", "")))) > 0
            elif check == "file_min_bytes":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = bool(matches) and all(m.stat().st_size >= a.get("min_bytes", 0) for m in matches)
            elif check == "file_contains":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = any(re.search(a.get("pattern", ""), m.read_text(errors="replace"), re.IGNORECASE) for m in matches) if matches else False
            elif check == "file_not_contains":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = True if not matches else not any(re.search(a.get("pattern", ""), m.read_text(errors="replace"), re.IGNORECASE) for m in matches)
            elif check == "yaml_field_equals":
                yaml_path = IES_ROOT / a.get("path", "")
                if yaml_path.exists():
                    data = yaml.safe_load(extract_frontmatter_block(yaml_path.read_text())) or {}
                    passed = data.get(a.get("field")) == a.get("value")
                else:
                    passed = False
            elif check == "step_count_gte":
                passed = len(eval_record.get("steps", [])) >= a.get("min_count", a.get("min_steps", 0))
            elif check == "duration_lte":
                passed = eval_record.get("duration_seconds", float("inf")) <= a.get("max_duration_seconds", float("inf"))
            else:
                continue  # unknown/timing-only checks (e.g. tool_was_called) skipped here as elsewhere
        except Exception as e:
            log_error(f"Assertion {a_id} failed: {e}", TAG)
        results.append({"assertion": a_id, "description": description, "passed": passed})

    checked = len(results)
    passed_count = sum(1 for r in results if r.get("passed") is True)
    structural["assertion_results"] = results
    structural["assertions_checked"] = checked
    structural["assertions_passed"] = passed_count
    return structural


def finalize(eval_path: Path, eval_record: dict, state_data: dict):
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(eval_record["started"].replace("Z", "+00:00"))
    duration = round((now - started).total_seconds(), 2)

    state_status = state_data.get("status")

    # Aggregate totals from steps[] (populated by the existing post-tool-use.py
    # inline-step path) and subagents[] (populated by eval-agent-start/stop.py
    # when a subagent ran while this record was open).
    total_in = sum(s.get("tokens_input") or 0 for s in eval_record.get("steps", []))
    total_in += sum(s.get("tokens_input") or 0 for s in eval_record.get("subagents", []))
    total_out = sum(s.get("tokens_output") or 0 for s in eval_record.get("steps", []))
    total_out += sum(s.get("tokens_output") or 0 for s in eval_record.get("subagents", []))
    total_cost = sum(s.get("cost_usd") or 0 for s in eval_record.get("steps", []))
    total_cost += sum(s.get("cost_usd") or 0 for s in eval_record.get("subagents", []))

    eval_record["completed"] = now.isoformat().replace("+00:00", "Z")
    eval_record["duration_seconds"] = duration
    eval_record["total_tokens_input"] = total_in or None
    eval_record["total_tokens_output"] = total_out or None
    eval_record["total_cost_usd"] = round(total_cost, 6) if total_cost else None

    tool_failures = eval_record.get("assessment", {}).get("mechanical", {}).get("tool_failures", 0)
    error_ids = eval_record.get("assessment", {}).get("mechanical", {}).get("error_ids", [])
    completed_ok = state_status == "complete"
    all_steps_finished = completed_ok

    if error_ids:
        status = "failure"
    elif state_status in ("aborted", "blocked"):
        status = "aborted"
    elif not completed_ok:
        status = "aborted"
    elif tool_failures > 0:
        status = "partial"
    else:
        status = "success"

    eval_record["status"] = status
    eval_record["assessment"]["mechanical"]["completed"] = completed_ok
    eval_record["assessment"]["mechanical"]["all_steps_finished"] = all_steps_finished
    eval_record["assessment"]["structural"] = run_assertions(eval_record["name"], eval_record)
    eval_record["version_hash"] = compute_version_hash(eval_record["name"])
    eval_record["monitoring"]["active"] = False

    atomic_write_json(eval_path, eval_record)
    log_info(f"Closed turn-level eval record {eval_record['id']} for '{eval_record['name']}' — status={status}", TAG)


def main():
    payload = read_stdin()
    session_id = infer_session_id()

    eval_path = find_open_turn_record(session_id)
    if not eval_path:
        return  # no eval was opened this session — no-op, per spec

    import json
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)
    except Exception as e:
        log_error(f"Failed to read {eval_path}: {e}", TAG)
        return

    state_yaml_path = eval_record.get("monitoring", {}).get("state_yaml_path")
    if not state_yaml_path:
        return

    state_data = read_state_yaml(state_yaml_path)
    if state_data.get("status") not in TERMINAL_STATUSES:
        log_info(f"'{eval_record['name']}' state.yaml still {state_data.get('status')!r} — leaving eval record open", TAG)
        return

    finalize(eval_path, eval_record, state_data)


if __name__ == "__main__":
    main()

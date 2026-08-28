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
    IES_ROOT, EVAL_RUNS_DIR, log_error, log_info, atomic_write_json, read_stdin,
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


def finalize(eval_path: Path, eval_record: dict, state_data: dict, force_status: str | None = None, reason: str | None = None):
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

    if force_status:
        status = force_status
        completed_ok = False
        all_steps_finished = False
    elif error_ids:
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
    if reason:
        eval_record["monitoring"]["close_reason"] = reason

    atomic_write_json(eval_path, eval_record)
    log_info(f"Closed turn-level eval record {eval_record['id']} for '{eval_record['name']}' — status={status}" + (f" ({reason})" if reason else ""), TAG)


STATE_COMPLETION_FIELDS = ("completed-at", "session-completed", "completed_at", "session_completed")
STALE_RECORD_ABORT_AFTER_HOURS = 2


def _parse_ts(value) -> "datetime | None":
    if not value or not isinstance(value, str):
        return None
    try:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _state_genuinely_completed_after(state_data: dict, opened_at: "datetime | None") -> bool:
    """Is there a completion timestamp on state.yaml that is at/after this
    eval record's own `started` time?

    Root cause of a real incident: shutdown-cleanup's state.yaml has sat at
    `status: complete` since 2026-08-12 (completed-at that same date) —
    nearly two weeks stale. A spurious turn-level record opened on
    2026-08-27 (from a detect_workflow false-positive, see that fix in
    eval-turn-start.py) was checking ONLY `status in TERMINAL_STATUSES` with
    no regard for *when* that status was set, so it finalized as a fake
    "success" in 26.8 seconds — the very next Stop event after it opened,
    because the file just happened to already say "complete" from two weeks
    ago. `status: complete` is necessary but not sufficient evidence that
    THIS monitoring window's workflow run actually completed; the
    completion timestamp must fall inside the window this record opened."""
    if opened_at is None:
        return True  # can't compare — don't block finalization on this alone
    for field in STATE_COMPLETION_FIELDS:
        completed = _parse_ts(state_data.get(field))
        if completed is not None:
            return completed >= opened_at
    # No completion timestamp field at all on this workflow's state.yaml
    # schema — nothing to compare against, so don't manufacture a false
    # block. This only matters for workflows that do stamp a completion
    # time, which boot and shutdown-cleanup both do.
    return True


def try_finalize(eval_path: Path) -> bool:
    """Read one turn-level record, finalize it if its monitored state.yaml
    is terminal AND that terminal status was actually reached during this
    record's own open window (see _state_genuinely_completed_after).
    Returns True if it finalized (success or stale-abort), False if it's
    genuinely still in-progress and should stay open."""
    import json
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)
    except Exception as e:
        log_error(f"Failed to read {eval_path}: {e}", TAG)
        return False

    state_yaml_path = eval_record.get("monitoring", {}).get("state_yaml_path")
    if not state_yaml_path:
        return False

    state_data = read_state_yaml(state_yaml_path)
    opened_at = _parse_ts(eval_record.get("started"))

    if state_data.get("status") not in TERMINAL_STATUSES:
        log_info(f"'{eval_record['name']}' state.yaml still {state_data.get('status')!r} — leaving eval record open", TAG)
        return False

    if not _state_genuinely_completed_after(state_data, opened_at):
        # state.yaml says terminal, but from before this record even opened —
        # stale evidence, not proof this record's own run finished. Leave it
        # open unless it's been sitting long enough that it's clearly never
        # going to get real evidence (e.g. a false-trigger record that will
        # never see genuine new activity) — then close it as aborted, never
        # as a fabricated "success".
        age_hours = (datetime.now(timezone.utc) - opened_at).total_seconds() / 3600 if opened_at else 0
        if age_hours >= STALE_RECORD_ABORT_AFTER_HOURS:
            finalize(eval_path, eval_record, state_data, force_status="aborted",
                     reason=f"state.yaml's own completion timestamp predates this record's open time by {age_hours:.1f}h — likely a spurious open, not a real run")
            return True
        log_info(f"'{eval_record['name']}' state.yaml is terminal but its completion timestamp predates this record's open — treating as stale, leaving open (age={age_hours:.1f}h)", TAG)
        return False

    finalize(eval_path, eval_record, state_data)
    return True


def sweep_orphaned_records(exclude: Path | None):
    """Self-heal pass: close out any OTHER open turn-level record whose
    monitored workflow has already reached a terminal state, regardless of
    session_id. Exists because session_id can legitimately (not just via
    the read-race fixed in hook_utils._read_session_index) resolve to two
    different values within one logical run — boot's own Session Index
    step appends a new memory/sessions/index.json entry partway through
    step-01, so a record opened before that append and a Stop event
    checked after it can disagree on session_id even with no bug involved.
    already_open_for_workflow() in eval-turn-start.py now dedupes by
    workflow name (not session_id) to stop this at open-time; this sweep is
    the belt-and-suspenders for anything that slips through anyway —
    without it, an orphan sits at status: in-progress forever, since no
    future Stop event's session_id would ever match it either."""
    if not EVAL_RUNS_DIR.exists():
        return
    import json
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        if exclude is not None and f == exclude:
            continue
        try:
            with open(f, "r") as file:
                data = json.load(file)
        except Exception:
            continue
        if (
            data.get("type") == "workflow"
            and data.get("status") == "in-progress"
            and data.get("monitoring", {}).get("active")
        ):
            if try_finalize(f):
                log_info(f"Swept orphaned turn-level record {f.name} for '{data.get('name')}'", TAG)


def main():
    payload = read_stdin()
    session_id = infer_session_id(payload)

    eval_path = find_open_turn_record(session_id)
    if eval_path:
        try_finalize(eval_path)

    sweep_orphaned_records(exclude=eval_path)

    if not eval_path:
        return  # no eval was opened under this Stop's session_id — no-op
                # for THIS session, per spec. The sweep above still ran, so
                # any other workflow's now-terminal orphan still gets closed.


if __name__ == "__main__":
    main()

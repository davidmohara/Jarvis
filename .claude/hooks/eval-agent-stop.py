#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
SubagentStop Hook: Eval Record Completion + Tier 1 & 2 Assessments
Triggered when a sub-agent returns.
Completes the eval record, runs mechanical assessment, structural assertions,
and error-log correlation.
"""

import json
import os
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
    from token_usage import usage_between, latest_task_usage, partition_usage_by_steps
except Exception:
    usage_between = None
    latest_task_usage = None
    partition_usage_by_steps = None
try:
    import fully_loaded_cost as _flc
except Exception:
    _flc = None
try:
    from hook_utils import (
        find_parent_record_with_subagent, transcript_indicates_completion,
        resolve_spawn_text, extract_workflow_path_reference,
        _read_first_user_message_text,
        find_records_by_agent_id, make_agent_stub, first_transcript_timestamp,
        read_subagent_meta,
        infer_session_id as _shared_infer_session_id,
    )
except Exception:
    find_parent_record_with_subagent = None
    transcript_indicates_completion = None
    resolve_spawn_text = None
    extract_workflow_path_reference = None
    _read_first_user_message_text = None
    find_records_by_agent_id = None
    make_agent_stub = None
    first_transcript_timestamp = None
    read_subagent_meta = None
    _shared_infer_session_id = None
try:
    import assertion_checks as _assertion_checks
except Exception:
    _assertion_checks = None
try:
    from step_audit import apply_record_attribution, steps_all_terminal
except Exception:
    apply_record_attribution = None
    steps_all_terminal = None

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

    # Stale-step guard: step files keep `status: complete` FOREVER unless the
    # next run rewrites them, so this loop otherwise re-processes steps from
    # previous runs. On 2026-10-21 the boot executor's stop re-processed six
    # plaud-ingest steps still carrying 2026-10-09 windows. A step whose
    # completed-at predates this subagent's own start cannot have been
    # executed by this subagent — skip it.
    run_started_dt = None
    try:
        run_started_dt = datetime.fromisoformat(
            (eval_record.get("started") or "").replace("Z", "+00:00"))
    except Exception:
        pass

    # Determine which workflow's steps to process
    workflow_to_process = workflow_name or eval_record.get("name") or "boot"
    steps_dir = ies_root / "workflows" / workflow_to_process / "steps"

    if not steps_dir.exists():
        log_info(f"No steps directory found for workflow '{workflow_to_process}', skipping step-complete hooks")
        return

    log_info(f"invoke_step_complete_hooks: processing steps for workflow '{workflow_to_process}' from {steps_dir}")

    # Locate step-complete.py next to THIS hook (its own build), not under
    # ies_root -- ies_root is a DATA root and may be redirected (IES_ROOT env)
    # without moving the hook scripts.
    step_complete_script = Path(__file__).resolve().parent / "step-complete.py"

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
            if step_data.get("status") not in ("complete", "completed"):
                continue

            if run_started_dt is not None:
                try:
                    sc = step_data.get("completed-at")
                    step_completed_dt = datetime.fromisoformat(str(sc).replace("Z", "+00:00")) if sc else None
                except Exception:
                    step_completed_dt = None
                if step_completed_dt is not None and step_completed_dt < run_started_dt:
                    log_info(f"Skipping stale step {step_file.name}: completed-at {sc} predates this run's start {eval_record.get('started')}")
                    continue

            payload = {
                "step_file_path": str(step_file),
                "step_content": content,
                "transcript_path": effective_transcript_path,
                "session_id": eval_record.get("session_id", ""),
                "workflow_name": workflow_to_process,
                # Target this exact record rather than letting step-complete.py
                # re-derive "the most recent record for this session", which
                # can pick a different, unrelated open record.
                "eval_record_id": eval_record.get("id")
            }
            subprocess.run(
                ["python3", str(step_complete_script)],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=10,
                # step-complete.py resolves its data root from IES_ROOT; pass
                # ours through so a redirected root (tests) stays redirected.
                env={**os.environ, "IES_ROOT": str(ies_root)},
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

        # Primary: match by agent_id (reliable, set by eval-agent-start.py).
        # Async background agents re-fire SubagentStart/Stop per resume
        # segment, so a record may legitimately be mid-lifecycle in any
        # status: prefer an in-progress match, but accept a closed record for
        # the same agent_id over guessing at a sibling's record — the
        # completion path recomputes cumulative tokens from the agent's own
        # transcript, so re-completing it is idempotent, and a record closed
        # early by the session-end sweep while the agent was still running
        # (eval-20261028T172711-WLE85H, deleted out from under the boot 05-08
        # briefing agent) gets its real data landed here instead of lost.
        if agent_id:
            if find_records_by_agent_id:
                matches = find_records_by_agent_id(agent_id, runs_dir=EVAL_RUNS_DIR)
            else:
                matches = []
                for f in EVAL_RUNS_DIR.glob("eval-*.json"):
                    try:
                        with open(f, "r") as file:
                            data = json.load(file)
                        if data.get("agent_id") == agent_id:
                            matches.append(f)
                    except Exception:
                        continue
            for f in matches:
                try:
                    with open(f, "r") as file:
                        if json.load(file).get("status") == "in-progress":
                            return f
                except Exception:
                    continue
            if matches:
                log_info(f"find_eval_record: no in-progress record for {agent_id}; "
                         f"re-using closed record {matches[0].name} (late/resumed async stop)")
                return matches[0]

        # Fallback: match most recent in-progress record for this agent_type.
        # ONLY safe when the payload carried no agent_id at all — with an
        # agent_id present, "some in-progress record of the same subagent
        # type" is a different agent's record, and completing it with THIS
        # agent's data is the 2026-10-28 hijack cascade (the 05-08 briefing
        # agent's stop stamped its tail-slice tokens onto M92BI5, whose own
        # stop then hijacked 0XRNN0). A stop with an agent_id and no matching
        # record gets a stop-origin record in main() instead.
        # Since Stage 3 Phase 0, eval-agent-start.py may have overwritten the
        # record's `agent` with the attributed IES agent, keeping the original
        # Claude Code subagent type in `subagent_type` — so match either field.
        if agent_id:
            return None
        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("status") == "in-progress" and (
                    data.get("agent") == agent_type
                    or data.get("subagent_type") == agent_type
                ):
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            log_info(f"find_eval_record: no agent_id in payload, used agent_type fallback for {agent_type}")
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
    return None


# Set by create_stop_origin_record when it declines to write a record because
# the stop carried no evidence that any run happened. Read by main() so the
# suppression logs at INFO instead of reporting a spurious ERROR.
_STOP_ORIGIN_SUPPRESSED = False


def _stop_origin_has_evidence(payload: dict, agent_id: str,
                              agent_transcript_path: str | None,
                              main_transcript_path: str | None) -> bool:
    """True when there is positive evidence that this SubagentStop names a run
    that actually happened. A SubagentStop with no SubagentStart stub is only
    trustworthy if SOMETHING on disk proves the agent existed: its transcript,
    its .meta.json, or a harness task-notification usage block keyed to its
    agent_id. On 2026-10-29 the harness emitted ~150 such stops per session
    whose agent ids appear nowhere — no transcript, no meta, no notification —
    and each one produced a zero-token, 0.0s `stop-origin` record (151 of the
    175 records dated that day, per the boot token analysis). They carry no
    measurable run and only inflate record counts. Real stop-origin recoveries
    (the 2026-10-27/28 boot briefing agents) always have a transcript."""
    if agent_transcript_path and Path(agent_transcript_path).exists():
        return True
    if read_subagent_meta:
        try:
            if read_subagent_meta(payload):
                return True
        except Exception:
            pass
    if latest_task_usage and main_transcript_path:
        try:
            usage = latest_task_usage(main_transcript_path, agent_id)
        except Exception:
            usage = None
        if usage and usage.get("harness_tokens") is not None:
            return True
    return False


def create_stop_origin_record(payload: dict, agent_id: str, agent_type: str,
                              agent_transcript_path: str | None) -> Path | None:
    """Create a stub at SubagentStop time for an agent whose SubagentStart
    record does not exist — the start hook never fired (observed for
    short-lived nested background agents, six of them on 2026-10-28) or its
    stub was swept while the agent was still running (the boot 05-08
    briefing agent, unrecorded on both 2026-10-27 and 2026-10-28). The stop
    payload plus the agent's own transcript are enough to reconstruct a
    normal record: started from the transcript's first timestamp, workflow
    from the recoverable spawn prompt, tokens from the whole-transcript
    slice in main()'s normal completion path.

    Declines (returns None) when the stop carries no evidence any run
    happened — see _stop_origin_has_evidence."""
    global _STOP_ORIGIN_SUPPRESSED
    if not make_agent_stub:
        return None
    try:
        if not _stop_origin_has_evidence(
                payload, agent_id, agent_transcript_path,
                payload.get("transcript_path")):
            _STOP_ORIGIN_SUPPRESSED = True
            log_info(f"Suppressed phantom stop-origin record for {agent_id}: "
                     f"no transcript on disk, no .meta.json, no task-notification "
                     f"— no evidence any run happened")
            return None
        session_id = payload.get("session_id")
        if not session_id and _shared_infer_session_id:
            session_id = _shared_infer_session_id(payload)
        session_id = session_id or "unknown"

        started = None
        if first_transcript_timestamp and agent_transcript_path:
            started = first_transcript_timestamp(agent_transcript_path)

        spawn_text = resolve_spawn_text(payload) if resolve_spawn_text else None
        if not spawn_text and _read_first_user_message_text:
            spawn_text = _read_first_user_message_text(agent_transcript_path)
        spawn_workflow = None
        if spawn_text and extract_workflow_path_reference:
            wf = extract_workflow_path_reference(spawn_text, must_exist=False)
            if wf and (IES_ROOT / "workflows" / wf / "workflow.md").is_file():
                spawn_workflow = wf

        stub = make_agent_stub(agent_id, agent_type or "unknown", session_id,
                               spawn_workflow=spawn_workflow, started=started)
        stub["tags"] = ["stop-origin"]
        eval_path = EVAL_RUNS_DIR / f"{stub['id']}.json"
        atomic_write_json(eval_path, stub)
        if eval_path.exists():
            log_info(f"Created stop-origin record {stub['id']} for {agent_id} "
                     f"(no SubagentStart stub existed; started={stub['started']})")
            return eval_path
        log_error(f"Failed to write stop-origin record for {agent_id}")
    except Exception as e:
        log_error(f"create_stop_origin_record failed for {agent_id}: {e}")
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

    # agent_id is the reliable correlation key (find_eval_record matches on it
    # first). agent_type is optional metadata used only for the fallback
    # lookup and logging, so a payload carrying agent_id but no agent_type
    # must not abort the whole stop path -- that silently dropped per-step
    # token capture for every such subagent.
    if not agent_id:
        log_error("SubagentStop hook missing agent_id")
        return

    # Find the corresponding eval record stub
    eval_record_path = find_eval_record(agent_id, agent_type)
    if not eval_record_path and agent_id:
        # No stub (start hook never fired, or the stub was swept while the
        # agent was still running) — build the record now from the stop
        # payload and the agent's transcript rather than dropping the run.
        eval_record_path = create_stop_origin_record(
            payload, agent_id, agent_type, agent_transcript_path)
    if not eval_record_path:
        if _STOP_ORIGIN_SUPPRESSED:
            # A phantom stop (no evidence of a run) is normal harness noise,
            # not a harness failure — do not spam the error log with it.
            log_info(f"Phantom SubagentStop for {agent_id} suppressed (no run evidence)")
        else:
            log_error(f"No eval record found for agent {agent_type} ({agent_id})")
        return

    # Read the stub
    try:
        with open(eval_record_path, "r") as f:
            eval_record = json.load(f)
    except Exception as e:
        log_error(f"Failed to read eval record: {e}")
        return

    # Adopted closed record (async agent whose stop arrived after a sweep or
    # after an earlier segment's stop): the previous close's derived
    # mechanical verdicts are stale — the sweep stamps completed=False on
    # records whose agent was still running, which would otherwise freeze
    # this stop's status at 'aborted'. Null the derived fields so they
    # re-derive from this stop's evidence; the raw counters (tool_failures,
    # error_ids) carry forward.
    if eval_record.get("status") != "in-progress":
        mech = (eval_record.get("assessment") or {}).get("mechanical")
        if isinstance(mech, dict):
            mech["completed"] = None
            mech["all_steps_finished"] = None
            mech.pop("abort_reason", None)
        log_info(f"Adopted closed record {eval_record_path.name} for late/resumed stop of {agent_id}")

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
    # usage_between substitutes the newest sibling transcript when the payload's
    # path is missing — defensible for a stub-backed record (the stub proves the
    # agent started in this session, so a sibling is at least contemporaneous),
    # but for a stop-origin record (no start evidence, no transcript on disk —
    # the ghost-stop class) that substitutes ANOTHER agent's tokens onto this
    # record. Better no token data than wrong token data: skip attribution.
    if (agent_transcript_path
            and not Path(agent_transcript_path).exists()
            and "stop-origin" in (eval_record.get("tags") or [])):
        log_info(f"stop-origin record for {agent_id}: transcript {agent_transcript_path} "
                 f"not on disk — skipping token attribution rather than substituting a sibling transcript")
        agent_transcript_path = None
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
                eval_record["model_source"] = "subagent-transcript"
                eval_record["total_tokens_input"] = usage["tokens_input"]
                eval_record["total_tokens_output"] = usage["tokens_output"]
                eval_record["total_cost_usd"] = usage["cost_usd"]
                eval_record["token_source"] = "subagent-transcript"
        except Exception as e:
            log_error(f"Failed to compute agent token usage: {e}")

    # Authoritative fallback: the harness's own task-notification usage block.
    # Background/async subagents report completion via a <task-notification>
    # enqueued into the MAIN session transcript carrying
    # <usage><subagent_tokens>N</subagent_tokens>... — the same total the
    # harness shows the user. When the subagent transcript is missing or
    # unreadable (the whole-run slice above returned nothing), record this
    # reported aggregate as harness_tokens (it carries no input/output split,
    # so it must NOT be written into tokens_input/tokens_output).
    main_transcript_path = payload.get("transcript_path")
    if latest_task_usage and main_transcript_path:
        try:
            note_usage = latest_task_usage(main_transcript_path, agent_id)
        except Exception as e:
            note_usage = None
            log_error(f"task-notification parse failed for {agent_id}: {e}")
        if note_usage:
            eval_record["harness_tokens"] = note_usage.get("harness_tokens")
            eval_record["harness_tool_uses"] = note_usage.get("harness_tool_uses")
            eval_record["harness_duration_ms"] = note_usage.get("harness_duration_ms")
            if eval_record.get("total_tokens_input") is None:
                eval_record["token_source"] = "task-notification"
                log_info(f"Whole-run tokens for {agent_id} from task-notification: "
                         f"{note_usage.get('harness_tokens')} harness tokens "
                         f"({note_usage.get('harness_tool_uses')} tool uses)")

    # Workflow recovery (2026-10-22): a dispatched workflow's subagent record
    # usually carries name="general-purpose" and workflow=None — SubagentStart
    # could not recover the spawn prompt at start time (its payload carries no
    # prompt text and the .meta.json is not yet written), so the step fan-out
    # below resolved the workflow to "general-purpose" and skipped per-step
    # attribution entirely. Root cause of eval-20261022T114429-OCSJIC (the
    # 2026-10-22 boot executor, 3.1M tokens, zero per-step records). At stop
    # time the spawn prompt IS recoverable — the meta.json exists now, and the
    # subagent transcript's first user message is the prompt — so mine it for
    # an explicit workflows/<name>/workflow.md reference and stamp the record's
    # `workflow` field before the crash-safe write and the fan-out read it.
    if not eval_record.get("workflow"):
        try:
            spawn_text = None
            if resolve_spawn_text:
                spawn_text = resolve_spawn_text(payload)
            if not spawn_text and _read_first_user_message_text:
                spawn_text = _read_first_user_message_text(agent_transcript_path)
            if spawn_text and extract_workflow_path_reference:
                # must_exist=False: the existence check inside hook_utils
                # resolves against the real repo root, which a redirected
                # IES_ROOT (tests) does not move — validate here against
                # this module's own IES_ROOT instead.
                wf = extract_workflow_path_reference(spawn_text, must_exist=False)
                if wf and (IES_ROOT / "workflows" / wf / "workflow.md").is_file():
                    eval_record["workflow"] = wf
                    log_info(f"Recovered workflow={wf!r} for {agent_id} from the "
                             f"spawn prompt; step fan-out and attribution will use it")
        except Exception as e:
            log_error(f"Workflow recovery failed for {agent_id}: {e}")

    # Nested-spawn workflow inheritance (2026-10-29): a depth-2+ child's spawn
    # prompt rarely names `workflows/<x>/workflow.md` — it reads something like
    # "Chief: synthesize morning briefing" — so the reference-mining above
    # leaves workflow=None and the child's tokens land in no workflow total.
    # On 2026-10-29 that was JXHCGH (628,496 tokens, tagged None) under the
    # boot 05-08 briefing agent, part of 888,530 unattributed tokens. Claude
    # Code records the parent's agent id in the child's .meta.json, so inherit
    # the parent record's workflow when no explicit reference was found.
    if not eval_record.get("workflow"):
        try:
            parent_aid = (read_subagent_meta(payload) or {}).get("parentAgentId") if read_subagent_meta else None
            if parent_aid and find_records_by_agent_id:
                for pf in find_records_by_agent_id(parent_aid, runs_dir=EVAL_RUNS_DIR):
                    with open(pf, "r") as f:
                        parent_wf = json.load(f).get("workflow")
                    if parent_wf:
                        eval_record["workflow"] = parent_wf
                        log_info(f"Inherited workflow={parent_wf!r} for nested agent "
                                 f"{agent_id} from parent {parent_aid}")
                        break
        except Exception as e:
            log_error(f"Nested workflow inheritance failed for {agent_id}: {e}")

    # CRASH-SAFE ORDERING: persist the core completion fields NOW, before the
    # step-complete subprocess fan-out and the assessment tail. On 2026-10-21
    # the boot executor's stop ran its step hooks (they wrote to disk) but the
    # record's completed/totals never landed — the tail never completed its
    # final write — leaving the record with completed=None, tokens=None and a
    # later flat $0.09 estimate over a run whose real cost was $0.63. Core
    # data first, enrichment second.
    atomic_write_json(eval_record_path, eval_record)

    # Per-step attribution for the PARENT workflow record. This is the
    # replacement for the retired lenient-fallback approach: partition THIS
    # subagent's own transcript across the parent record's steps (ordered by
    # started-at, clamped to this run) so every billable turn lands on exactly
    # one step and the per-step sums equal the whole-run total. Only steps
    # still missing tokens are filled; steps the parent already sliced inline
    # from the main session are left alone. Works on open OR closed parents
    # (find_parent_record_with_subagent) — today's boot parent was closed by
    # eval-turn-stop 25s after this subagent stopped.
    if partition_usage_by_steps and agent_transcript_path and find_parent_record_with_subagent:
        try:
            parent_path = find_parent_record_with_subagent(eval_record.get("session_id", ""), agent_id)
            if parent_path and parent_path != eval_record_path:
                with open(parent_path, "r") as f:
                    parent = json.load(f)
                parent_steps = parent.get("steps") or []
                needs = [s for s in parent_steps
                         if isinstance(s, dict) and s.get("tokens_input") is None and s.get("started")]
                if needs:
                    partition = partition_usage_by_steps(
                        agent_transcript_path, needs,
                        eval_record.get("started"), eval_record.get("completed"))
                    filled = 0
                    part_sum = 0
                    for s in parent_steps:
                        if not isinstance(s, dict):
                            continue
                        u = partition.get(s.get("name"))
                        if u is None:
                            continue
                        if u.get("tokens_input") is not None:
                            s["tokens_input"] = u["tokens_input"]
                            s["tokens_output"] = u["tokens_output"]
                            s["cost_usd"] = u["cost_usd"]
                            if u.get("model"):
                                s["model"] = u["model"]
                            s["turns_matched"] = u["turns_matched"]
                            s["turns_with_usage"] = u["turns_with_usage"]
                            s["executed_by_agent_id"] = agent_id
                            filled += 1
                            part_sum += u["tokens_input"] or 0
                        # Provenance is written even when tokens stay null
                        # (stale-window): the audit trail records WHY.
                        if u.get("token_source"):
                            s["token_source"] = u["token_source"]
                    if filled:
                        atomic_write_json(parent_path, parent)
                    whole = eval_record.get("total_tokens_input")
                    log_info(f"partition backfill for {agent_id} into {parent_path.name}: "
                             f"{filled} steps filled, partition sum={part_sum}, "
                             f"whole-run={whole} (integrity: {'OK' if whole == part_sum else 'MISMATCH'})")
        except Exception as e:
            log_error(f"partition backfill failed for {agent_id}: {e}")

    # Invoke step-complete hooks for all workflows/agents that have steps
    # This populates per-step token data from the agent transcript
    try:
        # Resolve the workflow this subagent ran. `name` is the Claude Code
        # subagent type ("general-purpose") for a dispatched workflow, so it
        # is NOT the workflow; `workflow` is authoritative -- set by
        # eval-agent-start.py from the spawn prompt, or stamped by
        # post-tool-use.py from the step file's path (the reliable source,
        # since most spawn prompts don't name workflows/<x>/workflow.md).
        # Fall back to `name` for records where name already IS the workflow.
        workflow_name = eval_record.get("workflow") or eval_record.get("name")
        if workflow_name:
            workflow_steps_dir = IES_ROOT / "workflows" / workflow_name / "steps"
            if workflow_steps_dir.exists():
                log_info(f"Found step directory for workflow '{workflow_name}', invoking step-complete hooks")
                invoke_step_complete_hooks(eval_record, agent_transcript_path, IES_ROOT, workflow_name=workflow_name)
                # Re-read eval record to get step data updated by hooks
                with open(eval_record_path, "r") as f:
                    eval_record = json.load(f)
            else:
                log_info(f"No steps directory for workflow '{workflow_name}' "
                         f"(name={eval_record.get('name')!r}, workflow={eval_record.get('workflow')!r}), "
                         f"skipping step-complete hooks")
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
                model = eval_record.get("model")
                rates = None
                if model:
                    # Alias-aware lookup (provider prefixes, -latest spellings,
                    # [1m] tags) so a glm-5p3 record isn't silently priced at
                    # sonnet-tier rates.
                    try:
                        from token_usage import rates_for_model
                        rates = rates_for_model(model)
                    except Exception:
                        rates = None
                    if rates is None:
                        rates = pricing.get(str(model).lower())
                rate_fallback_note = None
                if rates is None:
                    # Model absent or unpriced: price the estimate at the
                    # sonnet-tier default and SAY so on the record.
                    rate_fallback_note = (f"model '{model}' unpriced — estimated at sonnet-tier rates"
                                          if model else "model unknown — estimated at sonnet-tier rates")
                    model = model or "sonnet"
                    rates = pricing.get("sonnet", {"input_per_mtok": 3.00, "output_per_mtok": 15.00})
                workflow = eval_record.get("name", "fork")
                estimate = workflow_estimates.get(workflow, workflow_estimates["fork"])

                input_cost = (estimate["input"] / 1_000_000) * rates.get("input_per_mtok", 3.00)
                output_cost = (estimate["output"] / 1_000_000) * rates.get("output_per_mtok", 15.00)

                eval_record["total_cost_usd"] = round(input_cost + output_cost, 6)
                note = f"estimated based on {workflow} workflow type"
                if rate_fallback_note:
                    note = f"{note}; {rate_fallback_note}"
                eval_record["cost_estimation_note"] = note
                if not eval_record.get("model"):
                    # No transcript evidence for the model; the estimate had to
                    # price at SOME rate, so the pricing-default model is
                    # recorded explicitly labeled as an assumption — never as
                    # observed fact (verify-before-asserting).
                    eval_record["model"] = model
                    eval_record["model_source"] = "assumed-pricing-default"
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

    # If completed is still None (no state.yaml written — subagent/skill run,
    # not a workflow turn-level record), derive completion from the record's own
    # evidence. The SubagentStop payload frequently omits last_assistant_message
    # (it is empty for many subagents, including handback-only runs), so the old
    # `completed = bool(last_assistant_message)` defaulted those to False and
    # stamped verifiably-complete work as 'aborted' (2026-10-15: multiple
    # subagent records with completed steps — boot, morning-briefing, plaud-ingest
    # — were mislabeled aborted for exactly this reason). Tool failures mid-run
    # are normal retries and shouldn't indicate non-completion.
    if completed is None:
        if eval_record.get("last_assistant_message"):
            completed = True
        elif steps_all_terminal and steps_all_terminal(eval_record):
            # Steps recorded with a terminal status mean the subagent ran its
            # work to completion even when no final message text was captured
            # in the stop payload. Shared derivation (step_audit.
            # steps_all_terminal) so every writer that populates
            # mechanical.completed uses the same rule.
            completed = True
        else:
            # Last resort: read the subagent's own transcript. The stop payload
            # frequently omits last_assistant_message and a specialist spawn
            # records no workflow steps, so both signals above are empty for
            # exactly the runs that DID finish — the six 2026-10-16 runs, all
            # stamped `aborted` despite returning final reports. A transcript
            # that ends in a SubagentHandback tool_use (or a final assistant
            # text turn) is positive completion evidence; no transcript -> None
            # -> stays not-completed.
            evidence = (transcript_indicates_completion(agent_transcript_path)
                        if transcript_indicates_completion else None)
            completed = bool(evidence)
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

    # Fully-loaded cost (2026-10-21): stamp the parent session's own turns
    # during this subagent's window as the labeled parent_window component,
    # so a dispatched run's recorded cost includes the orchestration around
    # it (spawn turn, result handling), not just the subagent transcript.
    # payload transcript_path is the MAIN session transcript; the subagent's
    # own usage above came from agent_transcript_path — the two never mix.
    if _flc is not None:
        try:
            _flc.apply_to_record(eval_record, transcript_path=payload.get("transcript_path"))
        except Exception as e:
            log_error(f"parent-window cost computation failed for {agent_id}: {e}")

    # Attribution (Stage 3 Phase 0): stamp owning_agent and, when the record is
    # still carrying a Claude Code subagent-type label ("general-purpose"),
    # upgrade `agent` to the resolved IES owner. By this point the record's
    # name/workflow have been refined, so a spawn that named no workflow still
    # attributes correctly (e.g. a record named "boot-verification" -> ralph).
    if apply_record_attribution:
        try:
            apply_record_attribution(eval_record)
        except Exception as e:
            log_error(f"apply_record_attribution failed for {agent_id}: {e}")

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
                        if eval_record.get("harness_tokens") is not None:
                            entry["harness_tokens"] = eval_record.get("harness_tokens")
                            entry["harness_tool_uses"] = eval_record.get("harness_tool_uses")
                        if eval_record.get("token_source"):
                            entry["token_source"] = eval_record.get("token_source")
                        if eval_record.get("workflow"):
                            entry["workflow"] = eval_record.get("workflow")
                        break
                atomic_write_json(parent_path, parent)
        except Exception as e:
            log_error(f"Failed to roll up subagent {agent_id} into open turn record: {e}")

if __name__ == "__main__":
    main()

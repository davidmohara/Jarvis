#!/usr/bin/env python3
"""
Close (or create + close) an eval record for a workflow or skill completion.

Used by workflow final steps to write eval records in Cowork mode, where the
SubagentStart/SubagentStop hooks don't fire. In Claude Code, the hooks handle
record creation automatically — this script is idempotent and will find the
most recent in-progress record for the given name+session rather than create
a duplicate.

Usage (from workflow step, via Bash):
    python3 systems/eval-harness/close-eval-record.py \
        --name morning-briefing \
        --type workflow \
        --agent chief \
        --status success \
        --trigger boot \
        --started "2026-05-24T14:35:54Z" \
        --steps "step-01,step-02,step-03,step-04"

    --status: success | failure | partial | aborted
    --trigger: boot | manual | scheduled
    --steps: comma-separated list of step names that completed
    --started: ISO8601 start time (optional — defaults to 60s before now)

The script:
1. Looks for an existing in-progress stub matching name + current session_id.
2. If found: closes it (fills completed, duration_seconds, status, steps, assessment.mechanical.completed).
3. If not found: creates a complete record from scratch (Cowork path).

Tier 1 mechanical.completed is set to True if status is success or partial.
Tier 2 assertions are not run here (that's eval-agent-stop.py's job in Claude Code;
in Cowork, rigby-eval-analyze reads the files and back-fills as needed).
"""

import argparse
import fcntl
import json
import os
import secrets
import string
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

IES_ROOT = Path(os.environ.get("IES_ROOT", Path(__file__).resolve().parents[2]))
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SESSION_INDEX = IES_ROOT / "memory" / "sessions" / "index.json"
ALPHABET = string.ascii_uppercase + string.digits


def new_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def current_session_id() -> str:
    try:
        if SESSION_INDEX.exists():
            data = json.loads(SESSION_INDEX.read_text())
            if data:
                return data[-1].get("id", "")
    except Exception:
        pass
    return ""


def version_hash(name: str, eval_type: str) -> str | None:
    """Compute SHA256 of the workflow.md or SKILL.md for this run."""
    import hashlib
    candidates = []
    if eval_type == "workflow":
        candidates.append(IES_ROOT / "workflows" / name / "workflow.md")
    candidates.append(IES_ROOT / "skills" / name / "SKILL.md")
    candidates.append(IES_ROOT / ".claude" / "skills" / name / "SKILL.md")
    for path in candidates:
        if path.exists():
            return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return None


def atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            f.write("\n")
            fcntl.flock(f, fcntl.LOCK_UN)
        tmp.replace(path)
    except Exception as e:
        print(f"[close-eval] write failed for {path}: {e}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        raise


def find_stub(name: str, session_id: str) -> tuple[Path, dict] | tuple[None, None]:
    """Find the most recent in-progress eval stub for this name and session."""
    if not EVAL_RUNS_DIR.exists():
        return None, None
    candidates = []
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            data = json.loads(f.read_text())
            if (data.get("name") == name
                    and data.get("status") == "in-progress"
                    and data.get("session_id") == session_id):
                candidates.append((f, data))
        except Exception:
            continue
    if not candidates:
        return None, None
    # Most recently started
    candidates.sort(key=lambda x: x[1].get("started", ""), reverse=True)
    return candidates[0]


def build_steps(step_list: list[str], started_dt: datetime, completed_dt: datetime) -> list[dict]:
    """Build minimal step records from a name list.

    Since individual per-step timestamps are not tracked at the call site, we
    distribute the total elapsed time evenly across steps so that duration_seconds
    is a real number rather than null, and timestamps are monotonically ordered.
    Each step gets an equal slice of the total wall-clock window.
    """
    n = len(step_list)
    if n == 0:
        return []
    total_seconds = max(0.0, (completed_dt - started_dt).total_seconds())
    slice_seconds = total_seconds / n
    steps = []
    for i, name in enumerate(step_list):
        step_start = started_dt + timedelta(seconds=slice_seconds * i)
        step_end = started_dt + timedelta(seconds=slice_seconds * (i + 1))
        steps.append({
            "name": name,
            "started": step_start.isoformat().replace("+00:00", "Z"),
            "completed": step_end.isoformat().replace("+00:00", "Z"),
            "duration_seconds": round(slice_seconds, 1),
            "status": "success",
            "data_sources_used": [],
            "data_source_failures": []
        })
    return steps


def main():
    ap = argparse.ArgumentParser(description="Close an eval record on workflow completion")
    ap.add_argument("--name", required=True, help="Workflow or skill name (e.g. morning-briefing)")
    ap.add_argument("--type", default="workflow", choices=["workflow", "skill"], dest="eval_type")
    ap.add_argument("--agent", required=True, help="Owning agent (e.g. chief)")
    ap.add_argument("--status", required=True,
                    choices=["success", "failure", "partial", "aborted"],
                    help="Outcome status")
    ap.add_argument("--trigger", default="manual",
                    choices=["boot", "manual", "scheduled"])
    ap.add_argument("--started", default=None,
                    help="ISO8601 start time (optional)")
    ap.add_argument("--steps", default="",
                    help="Comma-separated step names that completed")
    args = ap.parse_args()

    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    # Capture real wall-clock completion time at the moment this script runs.
    now = datetime.now(timezone.utc)
    completed_iso = now.isoformat().replace("+00:00", "Z")

    session_id = current_session_id()

    # Try to find an existing stub (Claude Code hook created it) before resolving
    # the start time so we can use the stub's real started value.
    vhash = version_hash(args.name, args.eval_type)
    stub_path, stub = find_stub(args.name, session_id)

    # Determine start time — preference order:
    #   1. Stub's recorded started (most accurate; written at actual boot/spawn time)
    #   2. --started argument passed by the caller
    #   3. Warn and use now (no fabricated 60s offset; duration will be ~0 but honest)
    if stub is not None and stub.get("started"):
        try:
            started_dt = datetime.fromisoformat(stub["started"].replace("Z", "+00:00"))
        except ValueError:
            started_dt = None
    else:
        started_dt = None

    if started_dt is None and args.started:
        try:
            started_dt = datetime.fromisoformat(args.started.replace("Z", "+00:00"))
        except ValueError:
            started_dt = None

    if started_dt is None:
        print(
            "[close-eval] WARNING: no real started timestamp available; "
            "duration_seconds will be near-zero. Pass --started or ensure a stub exists.",
            file=sys.stderr,
        )
        started_dt = now

    started_iso = started_dt.isoformat().replace("+00:00", "Z")
    duration = max(0.0, (now - started_dt).total_seconds())

    step_names = [s.strip() for s in args.steps.split(",") if s.strip()]
    steps = build_steps(step_names, started_dt, now)
    completed_flag = args.status in ("success", "partial")
    all_steps = bool(step_names) and args.status in ("success", "partial")

    if stub is not None:
        # Close the existing stub
        stub["name"] = args.name  # may have been "unknown" in hook
        stub["type"] = args.eval_type
        stub["agent"] = args.agent
        stub["trigger"] = args.trigger
        stub["completed"] = completed_iso
        stub["duration_seconds"] = round(duration, 1)
        stub["status"] = args.status
        if step_names:
            stub["steps"] = steps
        stub["assessment"]["mechanical"]["completed"] = completed_flag
        stub["assessment"]["mechanical"]["all_steps_finished"] = all_steps
        if vhash:
            stub["version_hash"] = vhash
        atomic_write(stub_path, stub)
        print(f"closed: {stub_path.name}")
    else:
        # Cowork path — create a complete record from scratch
        eval_id = new_id()
        record = {
            "id": eval_id,
            "type": args.eval_type,
            "name": args.name,
            "agent": args.agent,
            "session_id": session_id,
            "trigger": args.trigger,
            "started": started_iso,
            "completed": completed_iso,
            "duration_seconds": round(duration, 1),
            "status": args.status,
            "steps": steps,
            "assessment": {
                "mechanical": {
                    "completed": completed_flag,
                    "all_steps_finished": all_steps,
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
                    "safety_grade": None,
                    "grader_notes": None
                },
                "controller_feedback": {
                    "rating": None,
                    "comment": None,
                    "timestamp": None
                },
                "bias_assessment": {
                    "applicable": False,
                    "protected_attributes": [],
                    "fairness_metric": None,
                    "demographic_coverage_verified": False,
                    "adversarial_inputs_tested": False,
                    "bias_detected": False,
                    "bias_flags": [],
                    "remediation_status": "none"
                }
            },
            "version_hash": vhash,
            "prior_baseline_id": None,
            "tags": ["cowork-instrumented"]
        }
        path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write(path, record)
        print(f"created: {path.name}")


if __name__ == "__main__":
    main()

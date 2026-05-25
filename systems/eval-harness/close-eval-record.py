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


def build_steps(step_list: list[str], started_iso: str) -> list[dict]:
    """Build minimal step records from a name list."""
    now = datetime.now(timezone.utc)
    steps = []
    for name in step_list:
        steps.append({
            "name": name,
            "started": started_iso,
            "completed": now.isoformat().replace("+00:00", "Z"),
            "duration_seconds": None,
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

    now = datetime.now(timezone.utc)
    completed_iso = now.isoformat().replace("+00:00", "Z")

    # Determine start time
    if args.started:
        try:
            started_dt = datetime.fromisoformat(args.started.replace("Z", "+00:00"))
        except ValueError:
            started_dt = now - timedelta(seconds=60)
    else:
        started_dt = now - timedelta(seconds=60)
    started_iso = started_dt.isoformat().replace("+00:00", "Z")
    duration = max(0, (now - started_dt).total_seconds())

    session_id = current_session_id()
    step_names = [s.strip() for s in args.steps.split(",") if s.strip()]
    steps = build_steps(step_names, started_iso)
    completed_flag = args.status in ("success", "partial")
    all_steps = bool(step_names) and args.status in ("success", "partial")
    vhash = version_hash(args.name, args.eval_type)

    # Try to find an existing stub (Claude Code hook created it)
    stub_path, stub = find_stub(args.name, session_id)

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
            "tags": ["cowork-instrumented"]
        }
        path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write(path, record)
        print(f"created: {path.name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
skill-capture.py — hook-based skill-run capture (Phase F2, 2026-10-10).

Replaces the retired in-file "SKILL COMPLETE" / "GRADE THIS RUN" sections.
Instructional files carry no eval-harness machinery; this module captures
skill runs from the outside:

  1. record_invoke(): called by the PostToolUse(Skill) hook
     (.claude/hooks/eval-skill-invoke.py) when the model invokes the Skill
     tool. Appends a pending entry to runs/pending-skill-runs.jsonl.
  2. finalize(): called by the Stop hook (.claude/hooks/eval-turn-stop.py)
     at end of turn. For each pending entry of the session: writes
     skill-runs/<skill>-latest.json, creates the eval record (reusing
     post-tool-use.py's create_eval_record_from_skill_run), and runs the
     deterministic grader (grade_skill_run.py).
  3. sweep_stale(): entries older than SWEEP_AFTER_HOURS are finalized with
     status "aborted" so a crashed session never leaves pending noise.

Honors IES_ROOT env var (same convention as step-complete.py) so tests can
point at a temp directory without touching the live harness.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IES_ROOT = Path(os.environ.get("IES_ROOT", REPO_ROOT))
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SKILL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "skill-runs"
PENDING_PATH = EVAL_RUNS_DIR / "pending-skill-runs.jsonl"
POST_TOOL_USE_HOOK = REPO_ROOT / ".claude" / "hooks" / "post-tool-use.py"

SWEEP_AFTER_HOURS = 6

ERROR_LOG = Path("/tmp/ies-hook-errors.log")


def log(msg, level="INFO"):
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{level}] [skill-capture] {msg}\n")
    except Exception:
        pass


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def skill_file(skill_name):
    for base in (IES_ROOT / ".claude" / "skills", IES_ROOT / "skills"):
        candidate = base / skill_name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def owning_agent(skill_name):
    """Read the owning agent from the SKILL.md frontmatter (owning_agent or agent)."""
    path = skill_file(skill_name)
    if not path:
        return "unknown"
    try:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^owning_agent:\s*(\S+)", text, re.MULTILINE)
        if not match:
            match = re.search(r"^agent:\s*(\S+)", text, re.MULTILINE)
        if match:
            return match.group(1).strip("'\"")
    except Exception:
        pass
    return "unknown"


def infer_trigger(session_id):
    """Infer boot/scheduled/manual from the session's open eval record; default manual."""
    try:
        for f in sorted(EVAL_RUNS_DIR.glob("eval-*.json"), reverse=True):
            data = json.loads(f.read_text())
            if data.get("session_id") == session_id and data.get("trigger") in (
                "boot", "scheduled", "manual"
            ):
                return data["trigger"]
    except Exception:
        pass
    return "manual"


def record_invoke(skill_name, session_id, subagent=None):
    """Append a pending skill-run entry. Called by the PostToolUse(Skill) hook."""
    if not skill_name:
        return
    try:
        EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "skill": skill_name,
            "session_id": session_id or "unknown",
            "subagent": subagent,
            "started": now_iso(),
            "captured_via": "skill-tool-posttooluse",
        }
        with open(PENDING_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
        log(f"recorded pending skill run: {skill_name} (session {session_id})")
    except Exception as exc:
        log(f"record_invoke failed for {skill_name}: {exc}", level="ERROR")


def _load_post_tool_use():
    """Import post-tool-use.py (dash-named) via importlib; module import has no side effects.

    Rebinds the module's root-derived paths (IES_ROOT, EVAL_RUNS_DIR, etc.) to
    this module's IES_ROOT so tests pointing IES_ROOT at a temp directory never
    write to the live runs/ directory. In production both roots are identical."""
    spec = importlib.util.spec_from_file_location("post_tool_use", POST_TOOL_USE_HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if IES_ROOT != REPO_ROOT:
        module.IES_ROOT = IES_ROOT
        module.EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
        module.SKILL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "skill-runs"
        module.ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"
        if hasattr(module, "INDEX_PATH"):
            module.INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
    return module


def _run_grader(skill_name):
    grader = REPO_ROOT / "systems" / "eval-harness" / "grade_skill_run.py"
    if not grader.is_file():
        return
    if IES_ROOT != REPO_ROOT:
        # Test mode (IES_ROOT pointed at a temp dir): the grader reads/writes
        # the live runs/ directory by its own file location, so running it
        # would grade a stale live record. Skip; tests assert on the signal
        # file and eval record directly.
        log(f"grader skipped for {skill_name}: test IES_ROOT")
        return
    try:
        subprocess.run(
            ["python3", str(grader), "--skill", skill_name],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:
        log(f"grader failed for {skill_name}: {exc}", level="ERROR")


def finalize_entry(entry, status="success"):
    """Write the skill-runs signal, create the eval record, run the grader."""
    skill_name = entry.get("skill", "unknown")
    session_id = entry.get("session_id", "unknown")
    started = entry.get("started") or now_iso()
    skill_run_data = {
        "skill": skill_name,
        "agent": owning_agent(skill_name),
        "trigger": infer_trigger(session_id),
        "started": started,
        "completed": now_iso(),
        "status": status,
        "tool_failures": 0,
        "error_ids": [],
        "captured_via": "hook",
    }
    try:
        SKILL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
        signal_path = SKILL_RUNS_DIR / f"{skill_name}-latest.json"
        signal_path.write_text(json.dumps(skill_run_data, indent=2) + "\n")
    except Exception as exc:
        log(f"signal write failed for {skill_name}: {exc}", level="ERROR")
        return
    try:
        ptu = _load_post_tool_use()
        ptu.create_eval_record_from_skill_run(skill_run_data, session_id)
    except Exception as exc:
        log(f"eval record creation failed for {skill_name}: {exc}", level="ERROR")
    _run_grader(skill_name)
    log(f"finalized skill run: {skill_name} (session {session_id}, status {status})")


def _read_pending():
    if not PENDING_PATH.is_file():
        return []
    entries = []
    for line in PENDING_PATH.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def _write_pending(entries):
    if not entries:
        try:
            PENDING_PATH.unlink()
        except FileNotFoundError:
            pass
        return
    PENDING_PATH.write_text("".join(json.dumps(e) + "\n" for e in entries))


def finalize(session_id):
    """Finalize every pending entry for this session. Called by the Stop hook."""
    if not session_id or not PENDING_PATH.is_file():
        return
    entries = _read_pending()
    mine = [e for e in entries if e.get("session_id") == session_id]
    if not mine:
        return
    rest = [e for e in entries if e.get("session_id") != session_id]
    for entry in mine:
        finalize_entry(entry)
    _write_pending(rest)


def sweep_stale():
    """Finalize abandoned entries (status aborted) so crashes leave no pending noise."""
    if not PENDING_PATH.is_file():
        return 0
    now = datetime.now(timezone.utc)
    entries = _read_pending()
    stale, rest = [], []
    for e in entries:
        started = parse_iso(e.get("started"))
        age_hours = (now - started).total_seconds() / 3600 if started else float("inf")
        (stale if age_hours >= SWEEP_AFTER_HOURS else rest).append(e)
    for entry in stale:
        finalize_entry(entry, status="aborted")
    _write_pending(rest)
    return len(stale)


if __name__ == "__main__":
    # Manual/testing entry point:
    #   python3 skill-capture.py record <skill> <session_id>
    #   python3 skill-capture.py finalize <session_id>
    #   python3 skill-capture.py sweep
    argv = sys.argv[1:]
    if argv and argv[0] == "record" and len(argv) >= 3:
        record_invoke(argv[1], argv[2])
    elif argv and argv[0] == "finalize" and len(argv) >= 2:
        finalize(argv[1])
    elif argv and argv[0] == "sweep":
        swept = sweep_stale()
        print(f"swept {swept} stale pending skill run(s)")
    else:
        print(__doc__)

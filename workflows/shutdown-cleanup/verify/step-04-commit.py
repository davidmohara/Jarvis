#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-04-commit.

Checks the real git state (working tree clean, a commit actually landed
during the step window) and the two other session-exit invariants CLAUDE.md
requires at exit time: no open eval records left in-progress from today,
and a working-memory entry exists for the session. None of this is taken
from the model's self-report — it is read directly off disk and git.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git(ies_root: Path, args: list) -> str:
    try:
        out = subprocess.run(
            ["git"] + args, cwd=ies_root, capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_started = payload.get("step_started")

    if not ies_root.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": f"ies_root does not exist: {ies_root}",
            "fields": {},
            "validation_errors": ["ies_root_missing"],
        }))
        return

    status_output = run_git(ies_root, ["status", "--porcelain"])
    uncommitted = [l for l in status_output.splitlines() if l.strip()]
    git_clean = len(uncommitted) == 0

    last_commit_iso = run_git(ies_root, ["log", "-1", "--format=%cI"])
    commit_after_step_start = None
    if last_commit_iso and step_started:
        try:
            commit_time = datetime.fromisoformat(last_commit_iso)
            start_time = datetime.fromisoformat(step_started.replace("Z", "+00:00"))
            commit_after_step_start = commit_time >= start_time
        except Exception:
            commit_after_step_start = None

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    open_evals_today = []
    if runs_dir.is_dir():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            started = str(data.get("started", ""))
            if data.get("status") == "in-progress" and started.startswith(today):
                open_evals_today.append(f.name)

    working_dir = ies_root / "memory" / "working"
    working_memory_today = []
    if working_dir.is_dir():
        for f in working_dir.glob(f"*{today}*"):
            working_memory_today.append(f.name)

    fields = {
        "git_clean": git_clean,
        "uncommitted_files": uncommitted[:20],
        "uncommitted_count": len(uncommitted),
        "last_commit_at": last_commit_iso or None,
        "commit_landed_after_step_start": commit_after_step_start,
        "open_evals_today_count": len(open_evals_today),
        "open_evals_today": open_evals_today,
        "working_memory_entries_today": working_memory_today,
    }

    validation_errors = []
    if not git_clean:
        validation_errors.append(f"uncommitted_changes: {len(uncommitted)}")
    if commit_after_step_start is False:
        validation_errors.append("no_commit_landed_during_step_window")
    if open_evals_today:
        validation_errors.append(f"open_evals_not_closed: {len(open_evals_today)}")

    if not git_clean or commit_after_step_start is False:
        print(json.dumps({
            "result": "retry",
            "reason": "Working tree is not clean after commit step" if not git_clean else "No new commit landed during the step window",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Stage and commit all remaining legitimate changes. Do not leave the working tree dirty at session exit.",
        }))
        return

    if open_evals_today:
        print(json.dumps({
            "result": "pass",
            "reason": f"Git clean and committed, but {len(open_evals_today)} eval record(s) from today are still status=in-progress — run close-open-evals.py",
            "fields": fields,
            "validation_errors": validation_errors,
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": "Working tree is clean, a commit landed during this step, and no open eval records remain from today",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

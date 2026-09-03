#!/usr/bin/env python3
"""Ground-truth verifier for content-approval/step-02-git-finalize.

Adapted from the retired workflows/content-pipeline/verify/step-03-git-finalize.py.
Confirms the workflow's own state files (pending-drafts.json, state.yaml, step-*.md,
now all under workflows/content-approval/) have no uncommitted changes left in git
after finalize, and that a commit touching workflows/content-approval/ actually
landed at or after the step started. Reads git directly — never trusts the step's
self-reported commit_hash/push_status.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TRACKED_PATHS = ["workflows/content-approval/"]


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

    status_output = run_git(ies_root, ["status", "--porcelain", "--"] + TRACKED_PATHS)
    uncommitted = [l for l in status_output.splitlines() if l.strip()]

    last_commit_touching_path = run_git(
        ies_root, ["log", "-1", "--format=%H|%cI", "--"] + TRACKED_PATHS
    )
    commit_hash, commit_time_str = (None, None)
    if last_commit_touching_path and "|" in last_commit_touching_path:
        commit_hash, commit_time_str = last_commit_touching_path.split("|", 1)

    commit_after_step_start = None
    if commit_time_str and step_started:
        try:
            commit_time = datetime.fromisoformat(commit_time_str)
            start_time = datetime.fromisoformat(step_started.replace("Z", "+00:00"))
            commit_after_step_start = commit_time >= start_time
        except Exception:
            commit_after_step_start = None

    fields = {
        "content_approval_dir_clean": len(uncommitted) == 0,
        "uncommitted_files": uncommitted,
        "last_commit_hash": commit_hash,
        "last_commit_at": commit_time_str,
        "commit_landed_after_step_start": commit_after_step_start,
    }

    validation_errors = []
    if uncommitted:
        validation_errors.append(f"uncommitted_content_approval_files: {len(uncommitted)}")
    if commit_after_step_start is False:
        validation_errors.append("no_commit_touching_content_approval_during_step_window")

    if uncommitted or commit_after_step_start is False:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/content-approval/ has uncommitted changes after git-finalize" if uncommitted else "No commit touching workflows/content-approval/ landed during this step's window",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Stage and commit all changes under workflows/content-approval/ (pending-drafts.json, state.yaml, step files).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"workflows/content-approval/ is fully committed, last commit {commit_hash[:8] if commit_hash else 'unknown'} at {commit_time_str}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

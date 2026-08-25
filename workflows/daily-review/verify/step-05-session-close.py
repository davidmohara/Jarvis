#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-05-session-close.

Checks the real memory/sessions/index.json for a closed session record
and greps actual git log for a matching daily-review commit, instead of
trusting a self-reported "session closed, changes committed" claim.
"""

import json
import subprocess
import sys
from pathlib import Path


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    index_path = ies_root / "memory" / "sessions" / "index.json"
    session_closed = False
    last_session_id = None
    if index_path.is_file():
        try:
            sessions = json.loads(index_path.read_text())
            if isinstance(sessions, list) and sessions:
                last = sessions[-1]
                last_session_id = last.get("id")
                session_closed = last.get("closed") is not None
        except Exception:
            pass

    commit_found = False
    latest_commit_message = None
    latest_commit_date = None
    try:
        proc = subprocess.run(
            ["git", "-C", str(ies_root), "log", "-20", "--pretty=format:%ci|%s"],
            capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                parts = line.split("|", 1)
                if len(parts) != 2:
                    continue
                commit_date_raw, subject = parts
                if "daily review" in subject.lower() or "daily-review" in subject.lower():
                    latest_commit_message = subject
                    latest_commit_date = commit_date_raw
                    commit_found = True
                    break
    except Exception:
        pass

    fields = {
        "session_index_exists": index_path.is_file(),
        "last_session_id": last_session_id,
        "session_closed": session_closed,
        "commit_found": commit_found,
        "latest_commit_message": latest_commit_message,
        "latest_commit_date": latest_commit_date,
    }

    if not index_path.is_file():
        verdict = {
            "result": "retry",
            "reason": "memory/sessions/index.json not found",
            "fields": fields,
            "validation_errors": ["session_index_missing"],
            "retry_instruction": "Re-execute step-05 — the session index must exist and be updated before closing.",
        }
    elif not session_closed:
        verdict = {
            "result": "retry",
            "reason": "Last session record does not have a closed timestamp",
            "fields": fields,
            "validation_errors": ["session_not_closed"],
            "retry_instruction": "Update the active session record in memory/sessions/index.json with a closed timestamp.",
        }
    elif not commit_found:
        verdict = {
            "result": "retry",
            "reason": "Session closed, but no matching daily-review commit found in recent git log",
            "fields": fields,
            "validation_errors": ["commit_not_found"],
            "retry_instruction": "Commit all changes with a message referencing the daily review per the git skill protocol.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Session closed and committed: '{latest_commit_message}'",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SessionStart Hook: Set session title and reload skills.
Sets the Jarvis session title to "Jarvis — YYYY-MM-DD" and signals
Claude Code to reload skills so any updates take effect immediately.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "systems" / "eval-harness"))
try:
    from hook_utils import note_harness_session
except Exception:
    note_harness_session = None

def main():
    # Read hook payload
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    # Record the harness-native session id so payload-less CLI scripts
    # (close-eval-record.py) resolve the same session id the hooks use —
    # the sessions-index id flavor is a fallback, not a parallel truth.
    if note_harness_session:
        note_harness_session(payload)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    response = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "sessionTitle": f"Jarvis — {today}"
        },
        "reloadSkills": True
    }

    print(json.dumps(response))

if __name__ == "__main__":
    main()

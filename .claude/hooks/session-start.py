#!/usr/bin/env python3
"""
SessionStart Hook: Set session title and reload skills.
Sets the Jarvis session title to "Jarvis — YYYY-MM-DD" and signals
Claude Code to reload skills so any updates take effect immediately.
"""

import json
import sys
from datetime import datetime, timezone

def main():
    # Read hook payload (not currently used but available)
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

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

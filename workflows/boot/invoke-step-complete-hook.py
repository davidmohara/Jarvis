#!/usr/bin/env python3
"""
Invoke step-complete hook after a step finishes.
Called by Master orchestrator after each step completes.

Usage:
    python3 invoke-step-complete-hook.py --step-file <path> --session-id <id> [--transcript-path <path>]
"""

import json
import sys
import subprocess
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step-file", required=True, help="Path to step .md file")
    parser.add_argument("--session-id", required=True, help="Session ID")
    parser.add_argument("--transcript-path", help="Path to transcript file")
    args = parser.parse_args()

    step_file = Path(args.step_file)
    if not step_file.exists():
        print(f"ERROR: Step file not found: {step_file}", file=sys.stderr)
        sys.exit(1)

    # Read step content
    with open(step_file) as f:
        step_content = f.read()

    # Build hook payload
    payload = {
        "step_file_path": str(step_file),
        "step_content": step_content,
        "transcript_path": args.transcript_path,
        "session_id": args.session_id
    }

    # Invoke step-complete.py hook
    hook_path = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "step-complete.py"

    try:
        result = subprocess.run(
            ["python3", str(hook_path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = json.loads(result.stdout) if result.stdout.strip() else {}
            print(json.dumps(output))
        else:
            print(f"Hook error: {result.stderr}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"ERROR invoking hook: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

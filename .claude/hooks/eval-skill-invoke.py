#!/usr/bin/env python3
"""
PostToolUse Hook (matcher: Skill): record skill invocations for hook-based capture.

Phase F2 (2026-10-10): instructional files carry no eval-harness machinery.
When the model invokes the Skill tool, this hook records the invocation via
systems/eval-harness/skill-capture.py. The Stop hook (eval-turn-stop.py)
finalizes the pending entries: signal file, eval record, deterministic grade.

Always exits 0 and never blocks — capture is best-effort observability.
"""

import json
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))

try:
    import skill_capture
except Exception:
    skill_capture = None


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    if payload.get("tool_name") != "Skill":
        return
    tool_input = payload.get("tool_input") or {}
    skill_name = tool_input.get("skill")
    if not skill_name:
        return
    session_id = (
        payload.get("session_id")
        or (payload.get("payload") or {}).get("session_id")
        or "unknown"
    )
    if skill_capture is not None:
        try:
            skill_capture.record_invoke(skill_name, session_id)
        except Exception:
            pass


if __name__ == "__main__":
    main()

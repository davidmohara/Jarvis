#!/usr/bin/env python3
"""
Close any open eval records at session exit.

Marks open evals with status: "incomplete" and abort_reason: "session-exit-normal"
so they're not counted as system failures in the success-rate metric.

A record with zero steps and zero subagents AND no agent_id never
represents a workflow that actually ran this session — most commonly a
"boot-first-prompt-of-session" record eval-turn-start.py opened
speculatively for a session that never invoked boot. Marking that
"incomplete" still leaves a record for something that never happened.
Those get deleted instead of closed — see err-20260829T161711-3IPMKR for
the incident that surfaced this. Records WITH an agent_id are
SubagentStart stubs (a real agent spawned) and are never deleted here:
an async background agent can still be running when the sweep fires, and
its late SubagentStop needs the stub to land on (2026-10-28 boot 05-08
briefing agent incident).

Usage:
  python3 close-open-evals.py /path/to/eval-harness/runs/
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# The shared step-evidence derivation of mechanical.completed lives in
# step_audit.py next to this script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from step_audit import steps_all_terminal
except Exception:
    steps_all_terminal = None


def close_open_evals(eval_dir):
    """Find and close any open eval records."""
    eval_path = Path(eval_dir)
    if not eval_path.exists():
        print(f"Eval directory not found: {eval_path}")
        return 0

    closed = 0
    deleted = 0
    now = datetime.now(tz=timezone.utc).isoformat()

    for f in eval_path.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            # Only close if still in-progress
            if data.get("status") == "in-progress":
                if not data.get("steps") and not data.get("subagents"):
                    if data.get("agent_id"):
                        # A record carrying an agent_id is a SubagentStart
                        # stub: a real agent was spawned. With async
                        # background agents the sweep can run while the agent
                        # is STILL RUNNING (2026-10-28: the boot 05-08
                        # briefing agent's stub was deleted at session end,
                        # its SubagentStop fired 42s later with nothing to
                        # land on, and a 3M-token run left no record at
                        # all). Mark it incomplete like any other real
                        # record; if the agent's stop is still in flight it
                        # will adopt and complete this record (eval-agent-
                        # stop.py matches closed records by agent_id).
                        data["status"] = "incomplete"
                        data["completed"] = now
                        mech = data.setdefault("assessment", {}).setdefault("mechanical", {})
                        mech["abort_reason"] = "session-exit-normal"
                        mech["completed"] = False
                        with open(f, "w") as file:
                            json.dump(data, file, indent=2)
                        closed += 1
                        continue
                    # Never accrued a single step or subagent and no agent
                    # ever spawned under it — nothing actually ran under
                    # this record. Delete it rather than leaving a false
                    # trace of a workflow that never happened, closed or
                    # otherwise.
                    f.unlink()
                    deleted += 1
                    continue

                data["status"] = "incomplete"
                data["completed"] = now
                mech = data.setdefault("assessment", {}).setdefault("mechanical", {})
                mech["abort_reason"] = "session-exit-normal"
                # mechanical.completed is derived from step evidence, not from
                # the session-exit close (Stage 3 Phase 0): a record whose every
                # recorded step is terminal is mechanically complete even though
                # the session ended before state.yaml was finalized.
                mech["completed"] = bool(
                    steps_all_terminal and steps_all_terminal(data)
                )

                with open(f, "w") as file:
                    json.dump(data, file, indent=2)
                closed += 1
        except Exception as e:
            print(f"Error processing {f.name}: {e}")

    if deleted:
        print(f"Deleted {deleted} phantom eval record(s) with no real activity")
    return closed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Close open eval records at session exit")
    parser.add_argument("eval_dir", help="Path to eval-harness/runs directory")
    args = parser.parse_args()

    closed = close_open_evals(args.eval_dir)
    if closed > 0:
        print(f"Closed {closed} open eval record(s)")

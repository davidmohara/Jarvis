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

Two guards added 2026-10-30, after the boot-token analysis found this
sweep closing a LIVE run and manufacturing zombies:

  1. A turn-level workflow record whose monitored state.yaml is still
     non-terminal is a workflow that is still executing. This sweep is
     fired by SessionEnd, and SessionEnd fires on events that are not
     session exit (three times on 2026-10-30, including twice mid-boot at
     14:08). Closing the live boot record there is what orphaned six
     executors that day. Those records are left open; eval-turn-stop.py
     finalizes them when the workflow actually finishes, and closes them
     as abandoned if the session dies without finishing.
  2. A closed record no longer claims to be monitored: monitoring.active
     is cleared on close. Leaving it true made the record look live to
     every linkable-record query while its status said otherwise.

Usage:
  python3 close-open-evals.py /path/to/eval-harness/runs/
"""

import argparse
import json
import os
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

# Vendored PyYAML, same convention as the hooks: this script must never
# depend on pip/pyyaml being installed on the host.
sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

TERMINAL_STATE_STATUSES = ("complete", "completed", "aborted", "blocked", "failed")


def _read_state_status(rel_path: str) -> str | None:
    """status from a monitored workflows/<name>/state.yaml, or None when the
    file/field/YAML support is unavailable (guard is then a no-op).

    Honors the IES_ROOT env var, same convention as eval-session-end.py and
    step-complete.py, so tests can point at a throwaway root."""
    if not rel_path or yaml is None:
        return None
    ies_root = Path(os.environ.get("IES_ROOT", Path(__file__).resolve().parents[2]))
    path = ies_root / rel_path
    if not path.is_file():
        return None
    try:
        content = path.read_text(errors="replace")
        lines = content.split("\n")
        body = content
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    body = "\n".join(lines[1:i])
                    break
        data = yaml.safe_load(body) or {}
        status = data.get("status")
        return str(status) if status is not None else None
    except Exception:
        return None


def is_live_workflow_record(data: dict) -> bool:
    """A turn-level workflow record whose workflow is demonstrably still
    running: it claims to be monitored and its state.yaml has not reached a
    terminal status. See module docstring, guard 1."""
    monitoring = data.get("monitoring") or {}
    if data.get("type") != "workflow" or not monitoring.get("active"):
        return False
    status = _read_state_status(monitoring.get("state_yaml_path") or "")
    return status is not None and status not in TERMINAL_STATE_STATUSES


def close_open_evals(eval_dir):
    """Find and close any open eval records."""
    eval_path = Path(eval_dir)
    if not eval_path.exists():
        print(f"Eval directory not found: {eval_path}")
        return 0

    closed = 0
    deleted = 0
    skipped_live = 0
    now = datetime.now(tz=timezone.utc).isoformat()

    for f in eval_path.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            # Only close if still in-progress
            if data.get("status") == "in-progress":
                if is_live_workflow_record(data):
                    # The workflow this record monitors is still executing
                    # (state.yaml non-terminal). SessionEnd is not a reliable
                    # "the session is over" signal — see module docstring —
                    # so leave it to eval-turn-stop.py to finalize.
                    skipped_live += 1
                    print(f"Left open (workflow still running): {f.name} "
                          f"'{data.get('name')}'")
                    continue
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
                        if isinstance(data.get("monitoring"), dict):
                            # A closed record must not claim to be monitored
                            # any more (guard 2).
                            data["monitoring"]["active"] = False
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
                if isinstance(data.get("monitoring"), dict):
                    # Guard 2: a closed record no longer claims to be monitored.
                    data["monitoring"]["active"] = False

                with open(f, "w") as file:
                    json.dump(data, file, indent=2)
                closed += 1
        except Exception as e:
            print(f"Error processing {f.name}: {e}")

    if deleted:
        print(f"Deleted {deleted} phantom eval record(s) with no real activity")
    if skipped_live:
        print(f"Left {skipped_live} record(s) open — their workflow is still running")
    return closed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Close open eval records at session exit")
    parser.add_argument("eval_dir", help="Path to eval-harness/runs directory")
    args = parser.parse_args()

    closed = close_open_evals(args.eval_dir)
    if closed > 0:
        print(f"Closed {closed} open eval record(s)")

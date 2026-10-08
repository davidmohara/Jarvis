#!/usr/bin/env python3
"""
Record step completion for eval harness (Cowork-compatible)
Called by workflow steps to record their completion status and timing.
Lightweight script (~10-20ms overhead) that updates eval records directly.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]

# Runs dir is overridable so a dry test can point at a temp dir instead of
# polluting the live runs/ directory (see --runs-dir below).
EVAL_RUNS_DIR = Path(os.environ.get("IES_EVAL_RUNS_DIR",
                                   IES_ROOT / "systems" / "eval-harness" / "runs"))

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
from step_audit import compute_cost, upsert_step, workflow_owner_agent  # noqa: E402

# Flags this script understands; their values must never be read as the
# positional started_at/completed_at args.
_VALUE_FLAGS = ("--tokens-in", "--tokens-out", "--model", "--agent", "--step-id", "--runs-dir")


def parse_flag_args(argv: list[str]) -> dict:
    """Pull the optional --flags out of the tail of argv."""
    flags = {"tokens_in": None, "tokens_out": None, "model": None,
             "agent": None, "step_id": None, "runs_dir": None}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in _VALUE_FLAGS and i + 1 < len(argv):
            value = argv[i + 1]
            if arg == "--tokens-in":
                flags["tokens_in"] = int(value)
            elif arg == "--tokens-out":
                flags["tokens_out"] = int(value)
            elif arg == "--model":
                flags["model"] = value
            elif arg == "--agent":
                flags["agent"] = value
            elif arg == "--step-id":
                flags["step_id"] = value
            elif arg == "--runs-dir":
                flags["runs_dir"] = value
            i += 2
        else:
            i += 1
    return flags

def parse_started(ts) -> "datetime | None":
    """Parse an ISO-8601 `started` value into a datetime (trailing Z normalized
    to +00:00). Returns None on unparseable/missing input so a bad timestamp
    degrades to deterministic fallback ordering instead of crashing the sort."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None

def find_most_recent_eval_record(workflow_name: str, runs_dir=None) -> Path | None:
    """Find the most recent IN-PROGRESS eval record for this workflow.

    Only records with status == "in-progress" are eligible — a closed/success
    record must never be a step-recording target (err-20260911T080849-3TCTQW:
    record-step overwrote yesterday's closed record when today's fresh record
    was still named "unknown").

    Ordering is on the parsed `started` datetime, not the raw string, because
    records with differing fractional-second precision invert under plain
    lexicographic sort ('.' sorts below 'Z', so '...06.786387Z' ranks as
    EARLIER than '...06Z' even within the same second) — see
    err-20260912T080901-GNRQ9D.
    """
    base_dir = Path(runs_dir) if runs_dir else EVAL_RUNS_DIR
    if not base_dir.exists():
        return None

    records = []
    for f in base_dir.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if data.get("name") == workflow_name and data.get("status") == "in-progress":
                parsed = parse_started(data.get("started", ""))
                if parsed is None:
                    parsed = datetime.min.replace(tzinfo=timezone.utc)
                records.append((parsed, f.name, f))
        except Exception:
            continue

    if not records:
        return None
    # Sort on (parsed datetime, filename) so ties break deterministically.
    records.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return records[0][2]

def main():
    if len(sys.argv) < 4:
        print("Usage: record-step.py <workflow_name> <step_name> <status> [started_at] [completed_at] "
              "[--tokens-in N] [--tokens-out N] [--model sonnet|haiku] "
              "[--agent <agent>] [--step-id <id>] [--runs-dir <dir>]")
        sys.exit(1)

    workflow_name = sys.argv[1]
    step_name = sys.argv[2]
    status = sys.argv[3]
    rest = sys.argv[4:]

    # started_at/completed_at are the first two non-flag positional args in rest.
    # Walk rest and skip flag+value pairs so a flag's value is never mistaken
    # for a positional arg.
    flags = parse_flag_args(rest)
    positional = []
    i = 0
    while i < len(rest):
        if rest[i] in _VALUE_FLAGS:
            i += 2
            continue
        positional.append(rest[i])
        i += 1
    started_at = positional[0] if len(positional) > 0 else None
    completed_at = positional[1] if len(positional) > 1 else None
    tokens_in = flags["tokens_in"]
    tokens_out = flags["tokens_out"]
    model = flags["model"]
    agent = flags["agent"]
    step_id = flags["step_id"]
    cost_usd = compute_cost(model, tokens_in, tokens_out)

    # Find the most recent in-progress eval record for this workflow.
    # If there is no exact in-progress match, FAIL LOUDLY rather than silently
    # picking (and overwriting) a fallback record — the silent fallback is the
    # failure mode behind err-20260911T080849-3TCTQW and err-20260912T080901-GNRQ9D.
    eval_path = find_most_recent_eval_record(workflow_name, runs_dir=flags["runs_dir"])
    if not eval_path:
        print(f"Error: no in-progress eval record found for workflow '{workflow_name}' — "
              f"step '{step_name}' NOT recorded. Create one first with "
              f"`python3 systems/eval-harness/new-eval.py --name {workflow_name}` "
              f"(and set --agent/--session-id), or verify the existing record's "
              f"name and status fields.", file=sys.stderr)
        sys.exit(1)

    # Read and update the eval record
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Calculate duration if both timestamps provided
        duration_seconds = None
        if started_at and completed_at:
            try:
                start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                duration_seconds = round((end - start).total_seconds(), 2)
            except Exception:
                pass

        # Create or update step entry. `agent` preserves whatever the harness
        # recorded on the run; `owning_agent` is the authoritative IES agent
        # that owns the workflow (resolved from workflows/<name>/workflow.md),
        # which is what attribution should read.
        step_entry = {
            "name": step_name,
            "step_id": step_id or step_name,
            "agent": agent or eval_record.get("agent"),
            "owning_agent": workflow_owner_agent(workflow_name) or agent or eval_record.get("agent"),
            "started": started_at,
            "completed": completed_at,
            "duration_seconds": duration_seconds,
            "status": status,
            "data_sources_used": [],
            "data_source_failures": [],
            "model": model,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "cost_usd": cost_usd
        }

        # Add or update step in eval record (backward-compatible dedup that
        # tolerates legacy string entries in an existing steps[] list).
        upsert_step(eval_record, step_entry)

        # Update mechanical assessment for step completion
        if status == "complete":
            eval_record["assessment"]["mechanical"]["all_steps_finished"] = True

        # Write updated record atomically
        tmp_path = eval_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(eval_record, f, indent=2)
        tmp_path.replace(eval_path)

    except Exception as e:
        # Log error but don't fail the workflow step
        print(f"Warning: Failed to record step completion: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Record a guardrail checkpoint result on the eval harness (Cowork-compatible).

A guardrail checkpoint is an adversarial-review gate placed at a handoff
between two Stage-3 prompts inside a Stage-4 workflow. It is deliberately
separate from ordinary step failure: a "flag" or "escalate" result means the
content was reviewed and found risky, not that a tool broke.

Usage:
  guardrail-checkpoint.py <workflow_name> <checkpoint_name> <after_step> <result> <reason>

  result: pass | flag | escalate
    pass      - reviewed, no issue, workflow continues automatically
    flag      - reviewed, minor issue auto-corrected or noted; workflow continues
    escalate  - reviewed, requires a human decision; workflow halts and surfaces
                to the controller. This is NOT a failure status.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"

VALID_RESULTS = {"pass", "flag", "escalate"}

# Retry/backoff for the case where this script runs before the current run's
# own eval record has been written to disk yet (a timing/race issue, not a
# missing-record issue). Bounded on purpose: this script is called
# synchronously from inside workflow steps, so an unbounded retry could hang
# a workflow that genuinely has no eval-harness record being created for it.
# RETRY_MAX_ATTEMPTS includes the first (immediate) attempt.
RETRY_MAX_ATTEMPTS = 6
RETRY_INTERVAL_SECONDS = 2
# Worst-case total wait: (RETRY_MAX_ATTEMPTS - 1) * RETRY_INTERVAL_SECONDS = 10s


def find_most_recent_eval_record(workflow_name: str) -> Path | None:
    try:
        if not EVAL_RUNS_DIR.exists():
            return None
        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                # Only attach to a record that is still open for this workflow.
                # A stale but already-closed record (status success/aborted/etc.)
                # must never be matched here — see err-20260904T081107-GYF8D1.
                if data.get("name") == workflow_name and data.get("status") == "in-progress":
                    records.append((f, data.get("started", "")))
            except Exception:
                continue
        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception:
        pass
    return None


def find_eval_record_with_retry(workflow_name: str) -> Path | None:
    """Poll for the in-progress eval record, tolerating the race where this
    script runs before the current run's record has been written yet.
    Returns immediately on the first successful match (zero extra delay when
    the record already exists). Gives up after RETRY_MAX_ATTEMPTS."""
    for attempt in range(RETRY_MAX_ATTEMPTS):
        eval_path = find_most_recent_eval_record(workflow_name)
        if eval_path:
            return eval_path
        if attempt < RETRY_MAX_ATTEMPTS - 1:
            time.sleep(RETRY_INTERVAL_SECONDS)
    return None


def main():
    if len(sys.argv) < 6:
        print("Usage: guardrail-checkpoint.py <workflow_name> <checkpoint_name> <after_step> <result:pass|flag|escalate> <reason>")
        sys.exit(1)

    workflow_name = sys.argv[1]
    checkpoint_name = sys.argv[2]
    after_step = sys.argv[3]
    result = sys.argv[4]
    reason = " ".join(sys.argv[5:])

    if result not in VALID_RESULTS:
        print(f"Warning: result '{result}' not in {VALID_RESULTS} — recording anyway", file=sys.stderr)

    eval_path = find_eval_record_with_retry(workflow_name)
    if not eval_path:
        # Still no matching in-progress record after retrying — don't block
        # the workflow, but don't go silent either (silent failure is how
        # err-20260904T081107-GYF8D1 went unnoticed for ~9 cycles).
        total_wait = (RETRY_MAX_ATTEMPTS - 1) * RETRY_INTERVAL_SECONDS
        print(
            f"Warning: no in-progress eval record found for workflow '{workflow_name}' "
            f"after {RETRY_MAX_ATTEMPTS} retries over {total_wait}s — checkpoint result NOT recorded",
            file=sys.stderr,
        )
        sys.exit(0)

    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        checkpoint_entry = {
            "name": checkpoint_name,
            "after_step": after_step,
            "result": result,
            "reason": reason,
            "escalated_to_human": result == "escalate",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if "guardrails" not in eval_record:
            eval_record["guardrails"] = []
        eval_record["guardrails"].append(checkpoint_entry)

        tmp_path = eval_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(eval_record, f, indent=2)
        tmp_path.replace(eval_path)

        # escalate is a distinct signal, not a failure — print it plainly so the
        # calling step can decide to halt and surface to the controller.
        if result == "escalate":
            print(f"GUARDRAIL_ESCALATE: {checkpoint_name} after {after_step}: {reason}")

    except Exception as e:
        print(f"Warning: Failed to record guardrail checkpoint: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

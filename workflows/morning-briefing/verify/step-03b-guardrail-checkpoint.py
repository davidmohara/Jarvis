#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-03b-guardrail-checkpoint.

The step's own instructions require it to record its result via
guardrail-checkpoint.py before proceeding. Confirms a "pre-synthesis-review"
entry actually landed in the eval record's guardrails list — rather than
trusting the step's self-report that it ran the checkpoint — and derives
the real recorded verdict from that entry.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def find_eval_records(runs_dir: Path):
    records = []
    if not runs_dir.exists():
        return records
    for f in sorted(runs_dir.glob("eval-*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("name") == "morning-briefing":
            records.append((f, data))
    return records


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = None

    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    records = find_eval_records(runs_dir)

    checkpoint_entry = None
    chosen_started = None
    for f, data in sorted(records, key=lambda x: x[1].get("started", ""), reverse=True):
        for g in data.get("guardrails", []) or []:
            if g.get("name") == "pre-synthesis-review":
                checkpoint_entry = g
                chosen_started = data.get("started")
                break
        if checkpoint_entry:
            break

    fields = {
        "checkpoint_found": checkpoint_entry is not None,
        "checkpoint_result": checkpoint_entry.get("result") if checkpoint_entry else None,
        "checkpoint_reason": checkpoint_entry.get("reason") if checkpoint_entry else None,
        "eval_record_started": chosen_started,
        "eval_records_scanned": len(records),
    }

    if not checkpoint_entry:
        print(json.dumps({
            "result": "retry",
            "reason": "No 'pre-synthesis-review' guardrail checkpoint entry found in any morning-briefing eval record",
            "fields": fields,
            "validation_errors": ["checkpoint_not_recorded"],
            "retry_instruction": "Run: python3 systems/eval-harness/guardrail-checkpoint.py morning-briefing pre-synthesis-review step-03-gather-context <pass|flag|escalate> \"<reason>\" before proceeding to step-04.",
        }))
        return

    result = checkpoint_entry.get("result")
    if result not in ("pass", "flag", "escalate"):
        print(json.dumps({
            "result": "retry",
            "reason": f"Recorded checkpoint has invalid result value: {result!r}",
            "fields": fields,
            "validation_errors": ["invalid_checkpoint_result"],
            "retry_instruction": "Re-run the guardrail checkpoint with a valid result (pass|flag|escalate).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Guardrail checkpoint recorded with result '{result}'"
        + (f": {checkpoint_entry.get('reason')}" if checkpoint_entry.get("reason") else ""),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

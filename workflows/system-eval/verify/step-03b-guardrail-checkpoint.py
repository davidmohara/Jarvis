#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-03b-guardrail-checkpoint.

Confirms a real `pre-score-review` guardrail checkpoint entry was recorded in
a system-eval eval record's `guardrails` list (via guardrail-checkpoint.py)
rather than trusting a self-reported "checkpoint passed" claim. Reads the
actual JSON records on disk.

Verdict:
  * retry - no matching checkpoint entry recorded.
  * fail  - the checkpoint recorded an `escalate` (scoring must not run on a
            suspect grade).
  * pass  - a pass/flag entry is recorded.
"""

import json
import sys
from pathlib import Path

CHECKPOINT_NAME = "pre-score-review"
VALID_RESULTS = {"pass", "flag", "escalate"}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if not runs_dir.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": "systems/eval-harness/runs/ not found",
            "fields": {"checkpoint_found": False},
            "validation_errors": ["runs_dir_missing"],
            "retry_instruction": "Confirm the eval harness runs directory exists before recording the guardrail checkpoint.",
        }))
        return

    records = []
    for f in runs_dir.glob("eval-*.json"):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("name") == "system-eval":
            records.append((f, data.get("started", ""), data))

    if not records:
        print(json.dumps({
            "result": "retry",
            "reason": "No eval record found for the system-eval workflow",
            "fields": {"checkpoint_found": False},
            "validation_errors": ["no_eval_record"],
            "retry_instruction": "Ensure an eval record exists for this system-eval run before the guardrail checkpoint executes.",
        }))
        return

    records.sort(key=lambda r: r[1], reverse=True)
    _, _, record = records[0]

    guardrails = record.get("guardrails") or []
    matching = [g for g in guardrails if g.get("name") == CHECKPOINT_NAME]

    fields = {
        "guardrails_total": len(guardrails),
        "checkpoint_found": bool(matching),
        "checkpoint_result": matching[-1].get("result") if matching else None,
        "checkpoint_reason": matching[-1].get("reason") if matching else None,
    }

    if not matching:
        print(json.dumps({
            "result": "retry",
            "reason": f"No '{CHECKPOINT_NAME}' guardrail checkpoint entry recorded on the latest system-eval eval record",
            "fields": fields,
            "validation_errors": ["checkpoint_not_recorded"],
            "retry_instruction": f"Run systems/eval-harness/guardrail-checkpoint.py system-eval {CHECKPOINT_NAME} step-03-grade <result> \"<reason>\" before proceeding.",
        }))
        return

    result_value = matching[-1].get("result")
    if result_value not in VALID_RESULTS:
        print(json.dumps({
            "result": "retry",
            "reason": f"Guardrail checkpoint recorded with invalid result: {result_value}",
            "fields": fields,
            "validation_errors": ["invalid_checkpoint_result"],
            "retry_instruction": "Re-record the checkpoint with a valid result: pass, flag, or escalate.",
        }))
        return

    if result_value == "escalate":
        print(json.dumps({
            "result": "fail",
            "reason": f"Guardrail checkpoint escalated: {matching[-1].get('reason')}",
            "fields": fields,
            "validation_errors": ["checkpoint_escalated"],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Guardrail checkpoint recorded: {result_value} - {matching[-1].get('reason')}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

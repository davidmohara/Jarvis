#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-03b-guardrail-checkpoint.

Confirms a real guardrail checkpoint entry was recorded in the daily-review
eval record's `guardrails` list (via guardrail-checkpoint.py) rather than
trusting a self-reported "checkpoint passed" claim — reads the actual JSON
record on disk and checks for an entry after step-03-update-system.
"""

import json
import sys
from pathlib import Path

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
            with open(f) as fh:
                data = json.load(fh)
        except Exception:
            continue
        if data.get("name") == "daily-review":
            records.append((f, data.get("started", ""), data))

    if not records:
        print(json.dumps({
            "result": "retry",
            "reason": "No eval record found for daily-review workflow",
            "fields": {"checkpoint_found": False},
            "validation_errors": ["no_eval_record"],
            "retry_instruction": "Ensure an eval record exists for this daily-review run before the guardrail checkpoint executes.",
        }))
        return

    records.sort(key=lambda r: r[1], reverse=True)
    _, _, record = records[0]

    guardrails = record.get("guardrails") or []
    matching = [g for g in guardrails if g.get("after_step") == "step-03-update-system"]

    fields = {
        "guardrails_total": len(guardrails),
        "checkpoint_found": bool(matching),
        "checkpoint_result": matching[-1].get("result") if matching else None,
        "checkpoint_reason": matching[-1].get("reason") if matching else None,
    }

    if not matching:
        verdict = {
            "result": "retry",
            "reason": "No guardrail checkpoint entry recorded after step-03-update-system",
            "fields": fields,
            "validation_errors": ["checkpoint_not_recorded"],
            "retry_instruction": "Run systems/eval-harness/guardrail-checkpoint.py daily-review pre-commit-review step-03-update-system <result> \"<reason>\" before proceeding.",
        }
    elif matching[-1].get("result") not in VALID_RESULTS:
        verdict = {
            "result": "retry",
            "reason": f"Guardrail checkpoint recorded with invalid result: {matching[-1].get('result')}",
            "fields": fields,
            "validation_errors": ["invalid_checkpoint_result"],
            "retry_instruction": "Re-record the checkpoint with a valid result: pass, flag, or escalate.",
        }
    elif matching[-1].get("result") == "escalate":
        verdict = {
            "result": "fail",
            "reason": f"Guardrail checkpoint escalated: {matching[-1].get('reason')}",
            "fields": fields,
            "validation_errors": ["checkpoint_escalated"],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Guardrail checkpoint recorded: {matching[-1].get('result')} — {matching[-1].get('reason')}",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

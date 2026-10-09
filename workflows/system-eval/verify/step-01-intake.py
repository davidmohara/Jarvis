#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-01-intake.

Intake check. The step opens this run's eval record and classifies every
closed record in the runs directory. This verifier re-derives the claim from
the real files rather than trusting a self-report:

  * workflows/system-eval/state.yaml must exist and carry a non-null
    `eval-record-id` (the self-tracking record was opened);
  * accumulated-context must carry an inventory: `records_total` (> 0) and the
    classification buckets (`needs_assertions`, `needs_grade`);
  * systems/eval-harness/runs/ must contain at least one eval record to
    inventory.

Verdict: retry if the state file, the eval-record-id, the inventory, or the
runs directory is missing; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STATE_REL = Path("workflows") / "system-eval" / "state.yaml"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / STATE_REL
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/system-eval/state.yaml not found or YAML parser unavailable",
            "fields": {"intake_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-01: initialize state.yaml and open the self-tracking eval record.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"intake_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01: the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    eval_id = state.get("eval-record-id")
    records_total = ctx.get("records_total") if isinstance(ctx, dict) else None
    has_buckets = isinstance(ctx, dict) and ("needs_assertions" in ctx or "needs_grade" in ctx)
    runs_count = len(list(runs_dir.glob("eval-*.json"))) if runs_dir.is_dir() else 0

    fields = {
        "eval_record_id": eval_id,
        "records_total": records_total,
        "has_classification_buckets": has_buckets,
        "runs_dir_exists": runs_dir.is_dir(),
        "runs_records_present": runs_count,
    }

    if not eval_id:
        print(json.dumps({
            "result": "retry",
            "reason": "state.yaml has no eval-record-id - the self-tracking eval record was not opened",
            "fields": fields,
            "validation_errors": ["eval_record_not_opened"],
            "retry_instruction": "Re-execute step-01: run new-eval.py and record eval-record-id in state.yaml.",
        }))
        return

    if runs_count == 0:
        print(json.dumps({
            "result": "retry",
            "reason": "systems/eval-harness/runs/ contains no eval records to inventory",
            "fields": fields,
            "validation_errors": ["no_records"],
            "retry_instruction": "Confirm the runs directory path resolves; if genuinely empty, exit cleanly per step-01's failure mode.",
        }))
        return

    if not has_buckets or not isinstance(records_total, int) or records_total <= 0:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context is missing the inventory (records_total and classification buckets)",
            "fields": fields,
            "validation_errors": ["inventory_missing"],
            "retry_instruction": "Re-execute step-01's inventory pass and record records_total/needs_assertions/needs_grade in state.yaml.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-01 intake verified: record {eval_id} opened, {records_total} records classified across {runs_count} on disk",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

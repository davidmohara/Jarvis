#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-02-assert.

Assertion check. The step claims it evaluated structural assertions on every
record listed in `needs_assertions` and tallied the results. This verifier
re-derives the claim from the real records rather than trusting a self-report:

  * state.yaml accumulated-context must carry an `assertions_run` tally;
  * if the tally reports records asserted, the corresponding eval records must
    actually show `assessment.structural.assertions_checked > 0` - the tally
    is cross-checked against the records on disk;
  * if `needs_assertions` was empty (nothing to assert), the step may advance
    with zero records asserted.

Verdict: retry if the tally is missing or claims assertions that no record
reflects; pass otherwise.
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
            "fields": {"assertions_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02: the workflow state file must exist before assertions are tallied.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"assertions_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02: the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    tally = ctx.get("assertions_run") if isinstance(ctx, dict) else None
    needs = ctx.get("needs_assertions") if isinstance(ctx, dict) else None

    # Cross-check against the real records: count those with assertions_checked > 0.
    records_with_assertions = 0
    if runs_dir.is_dir():
        for f in runs_dir.glob("eval-*.json"):
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            structural = (d.get("assessment") or {}).get("structural") or {}
            if isinstance(structural, dict) and (structural.get("assertions_checked") or 0) > 0:
                records_with_assertions += 1

    fields = {
        "assertions_run_present": isinstance(tally, dict),
        "total_records_asserted_reported": tally.get("total_records_asserted") if isinstance(tally, dict) else None,
        "needs_assertions_count": len(needs) if isinstance(needs, list) else None,
        "records_with_assertions_on_disk": records_with_assertions,
    }

    if not isinstance(tally, dict):
        print(json.dumps({
            "result": "retry",
            "reason": "state.yaml accumulated-context.assertions_run tally is missing",
            "fields": fields,
            "validation_errors": ["assertions_tally_missing"],
            "retry_instruction": "Re-execute step-02 and write the assertions_run tally to state.yaml.",
        }))
        return

    reported = tally.get("total_records_asserted")
    if isinstance(reported, int) and reported > 0 and records_with_assertions == 0:
        print(json.dumps({
            "result": "retry",
            "reason": f"tally reports {reported} record(s) asserted but no eval record on disk shows assertions_checked > 0",
            "fields": fields,
            "validation_errors": ["assertions_not_reflected"],
            "retry_instruction": "Re-run step-02: the assertion results were not written back to the eval records' assessment.structural blocks.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-02 assertions verified: tally present, {records_with_assertions} record(s) on disk carry assertion results",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-05-verify.

Re-derives the verification arithmetic from state.yaml rather than trusting the
step's self-report: `assertions_total` must equal the number of recorded
`assertion_results`, and `assertions_passed` must equal the count of those marked
passed. A mismatch means the pass/fail counts were reported rather than
computed, which is exactly what this step exists to prevent. A step-05 timing
entry is also reported.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "error-improvement"


def load_state(path: Path) -> dict:
    docs = [d for d in yaml.safe_load_all(path.read_text()) if d]
    return docs[0] if docs else {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/error-improvement/state.yaml missing or YAML parser unavailable",
            "fields": {"assertions_total": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05-verify and record the assertion results in state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"assertions_total": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05-verify: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    results = ctx.get("assertion_results") if isinstance(ctx, dict) else None
    reported_total = ctx.get("assertions_total") if isinstance(ctx, dict) else None
    reported_passed = ctx.get("assertions_passed") if isinstance(ctx, dict) else None

    computed_total = len(results) if isinstance(results, list) else None
    computed_passed = None
    if isinstance(results, list):
        computed_passed = sum(1 for r in results if isinstance(r, dict) and r.get("passed") is True)

    fields = {
        "assertions_total_reported": reported_total,
        "assertions_passed_reported": reported_passed,
        "assertions_total_computed": computed_total,
        "assertions_passed_computed": computed_passed,
    }

    if not isinstance(results, list):
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.assertion_results is missing or not a list, the verify step did not record its assertions",
            "fields": fields,
            "validation_errors": ["assertion_results_not_recorded"],
            "retry_instruction": "Re-execute step-05-verify: record accumulated-context.assertion_results with one entry per assertion.",
        }))
        return

    mismatches = []
    if reported_total != computed_total:
        mismatches.append(f"assertions_total reported {reported_total} but {computed_total} results recorded")
    if reported_passed != computed_passed:
        mismatches.append(f"assertions_passed reported {reported_passed} but {computed_passed} results passed")

    if mismatches:
        print(json.dumps({
            "result": "retry",
            "reason": f"Assertion counts do not match the recorded results: {mismatches}",
            "fields": fields,
            "validation_errors": [f"count_mismatch: {m}" for m in mismatches],
            "retry_instruction": "Re-execute step-05-verify: recompute assertions_total/assertions_passed from assertion_results.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Verification consistent: {computed_passed}/{computed_total} assertion(s) passed",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

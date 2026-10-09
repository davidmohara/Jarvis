#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-03-grade.

Grading check. The step claims it graded every record in `needs_grade` and
wrote a `rigby-eval-grade` skill-run signal. This verifier re-derives the
claim from the real records and the signal file rather than trusting a
self-report:

  * state.yaml accumulated-context must carry a `grading` tally;
  * if the tally reports records graded, the corresponding eval records must
    actually carry a non-null `assessment.grading.grade`;
  * the `rigby-eval-grade-latest.json` skill-run signal must exist.

Verdict: retry if the tally is missing, claims grades no record reflects, or
the skill-run signal is absent; pass otherwise.
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
SIGNAL_REL = Path("systems") / "eval-harness" / "skill-runs" / "rigby-eval-grade-latest.json"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / STATE_REL
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    signal_path = ies_root / SIGNAL_REL

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/system-eval/state.yaml not found or YAML parser unavailable",
            "fields": {"grading_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03: the workflow state file must exist before grades are tallied.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"grading_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-03: the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    grading = ctx.get("grading") if isinstance(ctx, dict) else None

    graded_on_disk = 0
    if runs_dir.is_dir():
        for f in runs_dir.glob("eval-*.json"):
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            g = (d.get("assessment") or {}).get("grading") or {}
            if isinstance(g, dict) and g.get("grade"):
                graded_on_disk += 1

    fields = {
        "grading_tally_present": isinstance(grading, dict),
        "total_graded_reported": grading.get("total_graded") if isinstance(grading, dict) else None,
        "graded_records_on_disk": graded_on_disk,
        "skill_run_signal_present": signal_path.is_file(),
    }

    if not isinstance(grading, dict):
        print(json.dumps({
            "result": "retry",
            "reason": "state.yaml accumulated-context.grading tally is missing",
            "fields": fields,
            "validation_errors": ["grading_tally_missing"],
            "retry_instruction": "Re-execute step-03 and write the grading tally to state.yaml.",
        }))
        return

    reported = grading.get("total_graded")
    if isinstance(reported, int) and reported > 0 and graded_on_disk == 0:
        print(json.dumps({
            "result": "retry",
            "reason": f"tally reports {reported} record(s) graded but no eval record on disk carries a grade",
            "fields": fields,
            "validation_errors": ["grades_not_reflected"],
            "retry_instruction": "Re-run step-03: grades were not written back to the eval records' assessment.grading blocks.",
        }))
        return

    if not signal_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "rigby-eval-grade-latest.json skill-run signal was not written",
            "fields": fields,
            "validation_errors": ["skill_run_signal_missing"],
            "retry_instruction": "Write the rigby-eval-grade skill-run signal to systems/eval-harness/skill-runs/rigby-eval-grade-latest.json.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-03 grading verified: tally present, {graded_on_disk} graded record(s) on disk, skill-run signal written",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

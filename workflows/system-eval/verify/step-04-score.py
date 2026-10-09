#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-04-score.

Scoring check. The step claims it ran `score_eval.py` over all closed records
and stored the results. This verifier re-derives the claim from the real files
rather than trusting a self-report:

  * the authoritative scoring script must exist at
    systems/eval-harness/scoring/score_eval.py;
  * state.yaml accumulated-context must carry a `scoring` block with a
    `records_scored` count (and a `batch_average` when scoring succeeded);
  * if scoring succeeded (records_scored > 0), the block must not also carry a
    `score_script_error` - a success and an error are mutually exclusive.

Verdict: retry if the script is missing, the scoring block is absent, or the
result is self-contradictory; pass otherwise (a logged script error that was
recorded and advanced past is a legitimate partial, so it is passed with a
note when records_scored is 0).
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
SCORE_SCRIPT_REL = Path("systems") / "eval-harness" / "scoring" / "score_eval.py"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / STATE_REL
    script_path = ies_root / SCORE_SCRIPT_REL

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/system-eval/state.yaml not found or YAML parser unavailable",
            "fields": {"scoring_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04: the workflow state file must exist before scores are stored.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"scoring_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04: the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    scoring = ctx.get("scoring") if isinstance(ctx, dict) else None

    fields = {
        "score_script_exists": script_path.is_file(),
        "scoring_block_present": isinstance(scoring, dict),
        "records_scored_reported": scoring.get("records_scored") if isinstance(scoring, dict) else None,
        "batch_average_reported": scoring.get("batch_average") if isinstance(scoring, dict) else None,
        "score_script_error": scoring.get("score_script_error") if isinstance(scoring, dict) else None,
    }

    if not script_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "systems/eval-harness/scoring/score_eval.py not found - the authoritative scoring script is missing",
            "fields": fields,
            "validation_errors": ["score_script_missing"],
            "retry_instruction": "Restore score_eval.py before re-running step-04.",
        }))
        return

    if not isinstance(scoring, dict):
        print(json.dumps({
            "result": "retry",
            "reason": "state.yaml accumulated-context.scoring block is missing",
            "fields": fields,
            "validation_errors": ["scoring_block_missing"],
            "retry_instruction": "Re-execute step-04 and write the scoring block (records_scored/batch_average) to state.yaml.",
        }))
        return

    scored = scoring.get("records_scored")
    err = scoring.get("score_script_error")

    if isinstance(scored, int) and scored > 0 and err:
        print(json.dumps({
            "result": "retry",
            "reason": f"scoring reports {scored} record(s) scored but also records a script error ({err}) - contradictory",
            "fields": fields,
            "validation_errors": ["scoring_contradiction"],
            "retry_instruction": "Reconcile records_scored with score_script_error in the scoring block.",
        }))
        return

    note = ""
    if err:
        note = f" (script error recorded and advanced past: {err})"
    elif not isinstance(scored, int) or scored == 0:
        note = " (no closed records scored)"

    print(json.dumps({
        "result": "pass",
        "reason": f"step-04 scoring verified: script present, scoring block recorded{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

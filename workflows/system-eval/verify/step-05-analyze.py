#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-05-analyze.

Analysis check. The step claims it wrote an analysis report to
`systems/eval-harness/grading/` and a `rigby-eval-analyze` skill-run signal.
This verifier re-derives the claim from the real files rather than trusting a
self-report:

  * a `grading/analysis-*.md` report must exist and be substantive (>500 bytes);
  * the `rigby-eval-analyze-latest.json` skill-run signal must exist;
  * state.yaml accumulated-context must carry an `analysis` block naming the
    report path, and that path must resolve on disk.

Verdict: retry if the report, the signal, or the analysis block is missing, or
the block names a path that does not exist; pass otherwise.
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
SIGNAL_REL = Path("systems") / "eval-harness" / "skill-runs" / "rigby-eval-analyze-latest.json"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / STATE_REL
    grading_dir = ies_root / "systems" / "eval-harness" / "grading"
    signal_path = ies_root / SIGNAL_REL

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/system-eval/state.yaml not found or YAML parser unavailable",
            "fields": {"analysis_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05: the workflow state file must exist before the analysis is tallied.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"analysis_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05: the workflow state file is corrupted.",
        }))
        return

    reports = []
    if grading_dir.is_dir():
        reports = [p for p in grading_dir.glob("analysis-*.md") if p.is_file()]
    latest = None
    if reports:
        latest = max(reports, key=lambda p: p.stat().st_mtime)
    report_substantive = bool(latest and latest.stat().st_size > 500)

    ctx = state.get("accumulated-context") or {}
    analysis = ctx.get("analysis") if isinstance(ctx, dict) else None
    named_path = analysis.get("report_path") if isinstance(analysis, dict) else None
    named_path_exists = bool(named_path) and (ies_root / named_path).is_file()

    fields = {
        "analysis_report_count": len(reports),
        "latest_report": str(latest.relative_to(ies_root)) if latest else None,
        "latest_report_substantive": report_substantive,
        "analysis_block_present": isinstance(analysis, dict),
        "named_report_path": named_path,
        "named_report_path_exists": named_path_exists,
        "skill_run_signal_present": signal_path.is_file(),
    }

    if not report_substantive:
        print(json.dumps({
            "result": "retry",
            "reason": "no substantive (>500 byte) analysis report found in systems/eval-harness/grading/",
            "fields": fields,
            "validation_errors": ["analysis_report_missing"],
            "retry_instruction": "Re-execute step-05 and write analysis-{timestamp}.md to systems/eval-harness/grading/.",
        }))
        return

    if not isinstance(analysis, dict):
        print(json.dumps({
            "result": "retry",
            "reason": "state.yaml accumulated-context.analysis block is missing",
            "fields": fields,
            "validation_errors": ["analysis_block_missing"],
            "retry_instruction": "Re-execute step-05 and record the analysis block (report_path/top_recommendation) in state.yaml.",
        }))
        return

    if named_path and not named_path_exists:
        print(json.dumps({
            "result": "retry",
            "reason": f"analysis block names report_path '{named_path}' which does not exist on disk",
            "fields": fields,
            "validation_errors": ["named_report_missing"],
            "retry_instruction": "Correct report_path in the analysis block to the report actually written.",
        }))
        return

    if not signal_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "rigby-eval-analyze-latest.json skill-run signal was not written",
            "fields": fields,
            "validation_errors": ["skill_run_signal_missing"],
            "retry_instruction": "Write the rigby-eval-analyze skill-run signal to systems/eval-harness/skill-runs/rigby-eval-analyze-latest.json.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-05 analysis verified: report {fields['latest_report']} present, analysis block recorded, skill-run signal written",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

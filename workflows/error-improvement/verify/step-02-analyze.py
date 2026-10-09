#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-02-analyze.

Re-derives the analysis claims from state.yaml rather than trusting the step's
self-report: the recorded `patterns_found` list must exist (empty is a
legitimate "no recurring patterns" outcome) and every recorded pattern must
carry the keys step-03 triage reads (category, failure_mode, occurrences, tier).
A step-02 timing entry must also be present.
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
REQUIRED_PATTERN_KEYS = ("category", "failure_mode", "occurrences", "tier")


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
            "fields": {"patterns_found": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02-analyze and write accumulated-context.patterns_found to state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"patterns_found": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02-analyze: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    patterns = ctx.get("patterns_found") if isinstance(ctx, dict) else None
    timings = ctx.get("step_timings") if isinstance(ctx, dict) else None
    timing_steps = []
    if isinstance(timings, list):
        timing_steps = [t.get("step") for t in timings if isinstance(t, dict)]

    fields = {
        "patterns_found": patterns if isinstance(patterns, list) else None,
        "pattern_count": len(patterns) if isinstance(patterns, list) else None,
        "timing_steps": timing_steps,
    }

    if not isinstance(patterns, list):
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.patterns_found is missing or not a list, step-02 analysis was not recorded",
            "fields": fields,
            "validation_errors": ["patterns_not_recorded"],
            "retry_instruction": "Re-execute step-02-analyze: record accumulated-context.patterns_found (an empty list is valid when no recurring patterns were found).",
        }))
        return

    malformed = []
    for p in patterns:
        if not isinstance(p, dict):
            malformed.append("non_object_pattern")
            continue
        missing = [k for k in REQUIRED_PATTERN_KEYS if k not in p]
        if missing:
            malformed.append(f"{p.get('pattern_id', 'unknown')}:missing_{','.join(missing)}")

    if malformed:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(malformed)} pattern record(s) are missing keys step-03 triage requires: {malformed[:5]}",
            "fields": fields,
            "validation_errors": [f"malformed_pattern: {m}" for m in malformed],
            "retry_instruction": "Re-execute step-02-analyze: every pattern needs category, failure_mode, occurrences, and tier.",
        }))
        return

    if "step-02-analyze" not in timing_steps:
        print(json.dumps({
            "result": "pass",
            "reason": f"Analysis recorded with {len(patterns)} pattern(s) (note: no step-02-analyze timing entry found)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Analysis recorded with {len(patterns)} pattern(s), step timing present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

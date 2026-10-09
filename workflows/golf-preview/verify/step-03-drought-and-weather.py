#!/usr/bin/env python3
"""Ground-truth verifier for golf-preview/step-03-drought-and-weather (Gate 3).

Weather is a soft input, but the workflow must never silently pretend it has
weather data when it does not. This verifier re-derives the flags from the
recorded data: `drought` and `heat_streak` must be present booleans, and a run
with no weather source must carry `weather_data_missing: true`.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-preview"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-preview/state.yaml missing or YAML parser unavailable",
            "fields": {},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03 and record drought/heat_streak/weather flags.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-03: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    if not isinstance(ctx, dict):
        ctx = {}

    drought = ctx.get("drought")
    heat_streak = ctx.get("heat_streak")
    weather_data_missing = ctx.get("weather_data_missing")
    weather_source = ctx.get("weather_source")
    heat_streak_calc_failed = ctx.get("heat_streak_calc_failed")

    fields = {
        "drought": drought,
        "heat_streak": heat_streak,
        "weather_data_missing": weather_data_missing,
        "weather_source": weather_source,
        "heat_streak_calc_failed": heat_streak_calc_failed,
    }

    problems = []
    if not isinstance(drought, bool):
        problems.append("drought flag missing or not boolean")
    if not isinstance(heat_streak, bool):
        problems.append("heat_streak flag missing or not boolean")
    # A run with no weather source must say so explicitly.
    if weather_source == "unavailable" and weather_data_missing is not True:
        problems.append("weather_source unavailable but weather_data_missing is not true")

    if problems:
        print(json.dumps({
            "result": "retry",
            "reason": f"Weather/drought flags incomplete: {problems}",
            "fields": fields,
            "validation_errors": problems,
            "retry_instruction": "Re-execute step-03: record boolean drought and heat_streak, and set weather_data_missing: true when no weather source is available.",
        }))
        return

    note = " (weather unavailable, degrade-and-flag surfaced to David)" if weather_data_missing else ""
    print(json.dumps({
        "result": "pass",
        "reason": f"Weather/drought flags recorded (drought={drought}, heat_streak={heat_streak}){note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

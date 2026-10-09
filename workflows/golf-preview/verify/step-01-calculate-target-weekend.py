#!/usr/bin/env python3
"""Ground-truth verifier for golf-preview/step-01-calculate-target-weekend (Gate 1).

A wrong target date here is silent and expensive: it propagates all the way into
a real midnight booking. This verifier re-derives the weekday arithmetic from the
recorded dates rather than trusting the gate's self-report: target_friday must be
a Friday, saturday = friday + 1, sunday = friday + 2, and friday must be at least
8 days out from today.
"""

import json
import sys
from datetime import datetime, date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-preview"
MIN_DAYS_OUT = 8


def parse_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    preview_path = ies_root / "workflows" / "golf-booking" / "preview-output.json"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-preview/state.yaml missing or YAML parser unavailable",
            "fields": {},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-01 and record the target weekend dates.",
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
            "retry_instruction": "Re-execute step-01: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    fri = sat = sun = None
    if isinstance(ctx, dict):
        fri = ctx.get("target_friday")
        sat = ctx.get("target_saturday")
        sun = ctx.get("target_sunday")

    # Fall back to the written preview output if state.yaml lacks the dates.
    if not (fri and sat and sun) and preview_path.is_file():
        try:
            tw = (json.loads(preview_path.read_text()) or {}).get("target_weekend") or {}
            fri = fri or tw.get("friday")
            sat = sat or tw.get("saturday")
            sun = sun or tw.get("sunday")
        except Exception:
            pass

    today_str = payload.get("today") or _date.today().isoformat()
    today = parse_date(today_str)

    fields = {
        "target_friday": fri,
        "target_saturday": sat,
        "target_sunday": sun,
        "today": today_str,
    }

    if not (fri and sat and sun):
        print(json.dumps({
            "result": "retry",
            "reason": "Target weekend dates are missing from state.yaml and preview-output.json",
            "fields": fields,
            "validation_errors": ["dates_not_recorded"],
            "retry_instruction": "Re-execute step-01: record target_friday/target_saturday/target_sunday.",
        }))
        return

    d_fri, d_sat, d_sun = parse_date(fri), parse_date(sat), parse_date(sun)
    if not (d_fri and d_sat and d_sun):
        print(json.dumps({
            "result": "retry",
            "reason": "One or more target dates are not parseable (expected YYYY-MM-DD)",
            "fields": fields,
            "validation_errors": ["dates_unparseable"],
            "retry_instruction": "Re-execute step-01: dates must be YYYY-MM-DD.",
        }))
        return

    problems = []
    if d_fri.weekday() != 4:
        problems.append(f"target_friday {fri} is not a Friday")
    if (d_sat - d_fri).days != 1:
        problems.append(f"target_saturday {sat} is not friday + 1")
    if (d_sun - d_fri).days != 2:
        problems.append(f"target_sunday {sun} is not friday + 2")

    days_out = (d_fri - today).days if today else None
    fields["days_out"] = days_out
    if days_out is not None and days_out < MIN_DAYS_OUT:
        problems.append(f"target_friday {fri} is only {days_out} day(s) out (needs >= {MIN_DAYS_OUT})")

    if problems:
        print(json.dumps({
            "result": "retry",
            "reason": f"Target weekend validation failed: {problems}",
            "fields": fields,
            "validation_errors": problems,
            "retry_instruction": "Re-execute step-01: recalculate the target weekend (Friday at least 8 days out, Saturday +1, Sunday +2).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Target weekend validated: {fri} (Fri, {days_out} days out), {sat} (Sat), {sun} (Sun)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

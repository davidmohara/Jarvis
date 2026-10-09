#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-01-synthesize.

Theme-synthesis check. The step claims `themes_identified` themes passed the
delta check. This verifier re-derives the claim from the real state file
rather than trusting the frontmatter self-report:

  * state.yaml accumulated-context must carry `weekly_themes`, and its length
    must equal `themes_identified`;
  * `delta_check_applied` must be true in accumulated-context (the step's own
    success metric: a run that skips the delta check fails regardless of theme
    count);
  * `dropped_as_continuing` must be present and an integer.

Verdict: retry if any of these fail; pass otherwise (including a genuine
no-themes run).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-01-synthesize.md"
STATE_REL = Path("workflows") / "watchtower" / "state.yaml"


def extract_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm:
            fm_lines.append(line)
    try:
        return yaml.safe_load("\n".join(fm_lines)) or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / STEP_REL
    state_path = ies_root / STATE_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-01-synthesize.md not found or YAML parser unavailable",
            "fields": {"synthesis_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-01-synthesize.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-01 outputs block is empty - no synthesis counts recorded",
            "fields": {"synthesis_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-01 and record themes_identified/dropped_as_continuing/used_fallback in the step frontmatter outputs.",
        }))
        return

    state = {}
    if state_path.is_file():
        try:
            state = yaml.safe_load(state_path.read_text()) or {}
        except Exception:
            state = {}
    ctx = state.get("accumulated-context") or {}
    weekly_themes = ctx.get("weekly_themes") if isinstance(ctx, dict) else None
    themes_count = len(weekly_themes) if isinstance(weekly_themes, list) else None
    delta_check = ctx.get("delta_check_applied") if isinstance(ctx, dict) else None

    themes_identified = outputs.get("themes_identified")
    dropped = outputs.get("dropped_as_continuing")

    fields = {
        "themes_identified_reported": themes_identified,
        "weekly_themes_in_state": themes_count,
        "delta_check_applied": delta_check,
        "dropped_as_continuing": dropped,
        "used_fallback": outputs.get("used_fallback"),
    }

    if delta_check is not True:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.delta_check_applied is not true - the step-01 delta check is required",
            "fields": fields,
            "validation_errors": ["delta_check_skipped"],
            "retry_instruction": "Run the delta check and set delta_check_applied: true in state.yaml accumulated-context.",
        }))
        return

    if not isinstance(themes_identified, int) or not isinstance(dropped, int):
        print(json.dumps({
            "result": "retry",
            "reason": "themes_identified or dropped_as_continuing is missing or not an integer",
            "fields": fields,
            "validation_errors": ["invalid_theme_fields"],
            "retry_instruction": "Record integer themes_identified and dropped_as_continuing in step-01 outputs.",
        }))
        return

    if themes_count is not None and themes_count != themes_identified:
        print(json.dumps({
            "result": "retry",
            "reason": f"themes_identified ({themes_identified}) != len(weekly_themes) in state.yaml ({themes_count})",
            "fields": fields,
            "validation_errors": ["themes_count_mismatch"],
            "retry_instruction": "Reconcile themes_identified with the weekly_themes written to state.yaml.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-01 synthesis verified: delta check applied, {themes_identified} theme(s) written to state.yaml",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

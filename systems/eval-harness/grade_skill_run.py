#!/usr/bin/env python3
"""
grade_skill_run.py — synchronous deterministic grading for one skill invocation.

Run as the LAST action of every skill (after the skill-runs/{name}-latest.json
signal file has been written — see the "SKILL COMPLETE" section every SKILL.md
carries, stamped by add-skill-signals.py). By the time this script runs, the
PostToolUse hook (post-tool-use.py) has already fired on the Write of that
signal file and created the eval record in systems/eval-harness/runs/, with
Tier 1 (mechanical) + Tier 2 (structural assertions) already populated via the
shared assertion_checks.py module.

This script:
  1. Locates the eval record just created for this skill (most recent by name).
  2. Computes the partial composite score via score_eval.py's compute_score()
     — grade/safety/feedback are still null at this point, so score_eval.py's
     existing null-weight redistribution naturally produces a score from only
     mechanical + assertion_rate + no_errors. This is reuse, not a parallel
     formula.
  3. Writes assessment.deterministic_gate {score, gate_status, computed_at}
     back into the eval record.
  4. Prints a compact, human-readable block to stdout — the skill's final
     step is instructed to include this verbatim in its response so the
     operator always sees the grade.

Usage:
  python3 systems/eval-harness/grade_skill_run.py --skill <skill-name> [--eval-id <id>]

Exit code is always 0 (grading failures must never fail the skill run itself);
errors are reported in the printed block instead.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
IES_ROOT = SCRIPT_DIR.parent.parent
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "scoring"))

try:
    import yaml
except Exception:
    yaml = None

import assertion_checks
from score_eval import compute_score, PASSING_THRESHOLD


def find_latest_record(skill_name: str, eval_id: str = None) -> "Path | None":
    if eval_id:
        candidate = EVAL_RUNS_DIR / f"{eval_id}.json"
        return candidate if candidate.exists() else None

    candidates = []
    for path in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(path) as f:
                r = json.load(f)
        except Exception:
            continue
        if r.get("name") == skill_name and r.get("type") == "skill":
            candidates.append(path)

    if not candidates:
        return None
    # eval-YYYYMMDDTHHMMSS-XXXXXX filenames sort lexicographically by time
    candidates.sort(key=lambda p: p.name, reverse=True)
    return candidates[0]


def atomic_write_json(path: Path, data: dict):
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    tmp_path.replace(path)


def format_block(skill_name: str, eval_id: str, record: dict, score_result: dict, note: str = None) -> str:
    structural = record.get("assessment", {}).get("structural", {})
    breakdown = structural.get("category_breakdown", {})
    checked = structural.get("assertions_checked", 0)
    passed = structural.get("assertions_passed", 0)

    lines = [f"--- Eval: {skill_name} ({eval_id}) ---"]

    if checked == 0:
        lines.append("No acceptance criteria defined for this skill yet — grading is a neutral placeholder.")
    else:
        for cat in ("structure", "content", "quality"):
            cb = breakdown.get(cat, {"passed": 0, "checked": 0})
            if cb["checked"] > 0:
                lines.append(f"{cat.capitalize():<10}{cb['passed']}/{cb['checked']} passed")

        failing = [
            r for r in structural.get("assertion_results", [])
            if r.get("passed") is False
        ]
        if failing:
            names = ", ".join(f["description"] or f["assertion"] for f in failing[:3])
            lines.append(f"Failing: {names}")

    score = score_result.get("score", 0.0)
    gate = score_result.get("gate_status", "fail")
    pct = round(score * 100)
    lines.append(f"Deterministic score: {pct}%  ->  {gate.upper()} (gate >= {int(PASSING_THRESHOLD * 100)}%)")
    lines.append("Tier 3 qualitative grade: pending (runs in tonight's end-of-day sweep — CLAUDE.md Exit Behavior)")
    if note:
        lines.append(note)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--eval-id", default=None)
    args = parser.parse_args()

    record_path = find_latest_record(args.skill, args.eval_id)
    if not record_path:
        print(f"--- Eval: {args.skill} ---\n"
              f"No eval record found yet (signal file may not have been picked up by the hook). "
              f"Deterministic score: unavailable this run.")
        return 0

    with open(record_path) as f:
        record = json.load(f)

    # Re-run assertions here too (belt and suspenders — in case the hook's
    # write raced with this script, or ran before an output file this
    # skill wrote after the signal file). Idempotent: same inputs, same result.
    record["assessment"]["structural"] = assertion_checks.run_assertions(
        assertions_dir=ASSERTIONS_DIR,
        name=args.skill,
        eval_record=record,
        ies_root=IES_ROOT,
        agent=record.get("agent"),
        transcript_path=None,
        yaml_module=yaml,
    )

    score_result = compute_score(record)

    record.setdefault("assessment", {})["deterministic_gate"] = {
        "score": round(score_result.get("score", 0.0), 4),
        "gate_status": score_result.get("gate_status"),
        "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    note = None
    checked = record["assessment"]["structural"].get("assertions_checked", 0)
    if checked == 0:
        note = f"No assertions/{args.skill}.json exists yet — this run is ungraded. Add acceptance criteria to grade future runs."

    try:
        atomic_write_json(record_path, record)
    except Exception as e:
        note = (note + " " if note else "") + f"[warning: could not persist score to {record_path.name}: {e}]"

    print(format_block(args.skill, record.get("id", record_path.stem), record, score_result, note))
    return 0


if __name__ == "__main__":
    sys.exit(main())

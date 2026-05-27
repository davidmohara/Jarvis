#!/usr/bin/env python3
"""
score_eval.py — Compute composite score for one or more eval records.

Usage:
  python3 score_eval.py --record <eval-id>
  python3 score_eval.py --batch <id1> <id2> <id3>
  python3 score_eval.py --skill <skill-id> --limit 20

Output: JSON with per-record scores and batch average.

This script is the authoritative implementation of the IES eval composite score formula.
All agents and workflows should call this script rather than reimplementing the formula.

Formula:
  score = (mechanical × 0.25) + (assertion_rate × 0.35) + (grade_score × 0.20)
        + (feedback × 0.10) + (no_errors × 0.10)

When grade or feedback is null: weights are redistributed proportionally
across the non-null components.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

# IES root — resolve relative to this script's location
SCRIPT_DIR = Path(__file__).parent
IES_ROOT = SCRIPT_DIR.parent.parent.parent

EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
EVAL_EVALS_DIR = IES_ROOT / "systems" / "evals"

# Base weights (must sum to 1.0)
BASE_WEIGHTS = {
    "mechanical":       0.25,
    "assertion_rate":   0.35,
    "grade_score":      0.20,
    "feedback":         0.10,
    "no_errors":        0.10,
}


def find_record(record_id: str) -> dict | None:
    """Locate and load an eval record by ID."""
    # Check primary runs directory
    primary = EVAL_RUNS_DIR / f"{record_id}.json"
    if primary.exists():
        with open(primary) as f:
            return json.load(f)

    # Check structured evals directories
    pattern = str(EVAL_EVALS_DIR / "**" / f"{record_id}.json")
    matches = glob.glob(pattern, recursive=True)
    if matches:
        with open(matches[0]) as f:
            return json.load(f)

    return None


def find_records_for_skill(skill_id: str, limit: int = 20) -> list[dict]:
    """Find all eval records for a given skill, most recent first."""
    records = []

    # Scan runs directory
    for path in EVAL_RUNS_DIR.glob("*.json"):
        try:
            with open(path) as f:
                r = json.load(f)
            if r.get("name") == skill_id or skill_id in r.get("tags", []):
                records.append(r)
        except (json.JSONDecodeError, KeyError):
            continue

    # Scan evals directories
    for path in EVAL_EVALS_DIR.rglob("*.json"):
        try:
            with open(path) as f:
                r = json.load(f)
            if (isinstance(r, dict) and r.get("id", "").startswith("eval-")
                    and (r.get("name") == skill_id or skill_id in r.get("tags", []))):
                records.append(r)
        except (json.JSONDecodeError, KeyError):
            continue

    # Sort by started timestamp descending
    records.sort(key=lambda r: r.get("started", ""), reverse=True)
    return records[:limit]


def compute_score(record: dict) -> dict:
    """
    Compute the composite score for a single eval record.

    Returns a dict with:
      - score: float [0.0, 1.0]
      - components: dict of component name → (raw_value, weight_used, contribution)
      - notes: list of strings describing any special handling
    """
    assessment = record.get("assessment", {})
    mechanical_data = assessment.get("mechanical", {})
    structural_data = assessment.get("structural", {})
    grading_data = assessment.get("grading", {})
    feedback_data = assessment.get("controller_feedback", {})

    notes = []
    components = {}

    # --- Mechanical ---
    status = record.get("status", "failure")
    if status == "success":
        mechanical_val = 1.0
    elif status == "partial":
        mechanical_val = 0.5
    else:
        mechanical_val = 0.0
    # Also check mechanical.completed directly
    if mechanical_data.get("completed") is False:
        mechanical_val = min(mechanical_val, 0.0)
    components["mechanical"] = mechanical_val

    # --- Assertion Rate ---
    assertions_checked = structural_data.get("assertions_checked", 0)
    assertions_passed = structural_data.get("assertions_passed", 0)
    if assertions_checked == 0:
        assertion_rate = 0.5  # neutral — no assertions defined
        notes.append("no_assertions_defined: assertion_rate set to neutral 0.5")
    else:
        assertion_rate = assertions_passed / assertions_checked
    components["assertion_rate"] = assertion_rate

    # --- Grade Score ---
    grade = grading_data.get("grade")
    grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.0}
    if grade is None:
        grade_score = None  # omit from weighted average
        notes.append("grade: null — weight redistributed")
    else:
        grade_score = grade_map.get(grade, 0.5)
    components["grade_score"] = grade_score

    # --- Feedback ---
    feedback_rating = feedback_data.get("rating")
    if feedback_rating is None:
        feedback_val = None  # omit
        notes.append("feedback: null — weight redistributed")
    elif feedback_rating == "positive":
        feedback_val = 1.0
    elif feedback_rating == "negative":
        feedback_val = 0.0
    else:  # "skip" or unknown
        feedback_val = None
        notes.append(f"feedback: '{feedback_rating}' — treated as null, weight redistributed")
    components["feedback"] = feedback_val

    # --- No Errors ---
    error_ids = mechanical_data.get("error_ids", [])
    tool_failures = mechanical_data.get("tool_failures", 0)
    no_errors_val = 1.0 if (len(error_ids) == 0 and tool_failures == 0) else 0.0
    components["no_errors"] = no_errors_val

    # --- Compute Weighted Average (redistributing null weights) ---
    active_weights = {}
    for key, base_weight in BASE_WEIGHTS.items():
        if components[key] is None:
            continue  # this component is omitted
        active_weights[key] = base_weight

    if not active_weights:
        # Degenerate case: everything is null
        score = 0.0
        notes.append("WARNING: all components null — score defaulted to 0.0")
    else:
        total_base = sum(active_weights.values())
        score = 0.0
        component_details = {}
        for key, base_weight in active_weights.items():
            redistributed_weight = base_weight / total_base
            contribution = components[key] * redistributed_weight
            score += contribution
            component_details[key] = {
                "value": components[key],
                "weight": round(redistributed_weight, 4),
                "contribution": round(contribution, 4),
            }

        # Add omitted components as None
        for key in BASE_WEIGHTS:
            if key not in component_details:
                component_details[key] = {
                    "value": None,
                    "weight": 0.0,
                    "contribution": 0.0,
                    "omitted": True,
                }

        components = component_details

    return {
        "record_id": record.get("id", "unknown"),
        "skill": record.get("name", "unknown"),
        "score": round(score, 4),
        "components": components,
        "notes": notes,
    }


def score_batch(records: list[dict]) -> dict:
    """Score a batch of records and compute aggregate stats."""
    results = [compute_score(r) for r in records]
    scores = [r["score"] for r in results]

    if not scores:
        avg = 0.0
        min_score = 0.0
        max_score = 0.0
    else:
        avg = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

    return {
        "records": results,
        "aggregate": {
            "count": len(results),
            "average": round(avg, 4),
            "min": round(min_score, 4),
            "max": round(max_score, 4),
            "successes": sum(1 for r in records if r.get("status") == "success"),
            "failures": sum(1 for r in records if r.get("status") == "failure"),
            "partials": sum(1 for r in records if r.get("status") == "partial"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Score IES eval records")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record", help="Single eval record ID to score")
    group.add_argument("--batch", nargs="+", help="Multiple eval record IDs to score")
    group.add_argument("--skill", help="Skill ID — scores all records for that skill")

    parser.add_argument("--limit", type=int, default=20,
                        help="Max records to load when using --skill (default: 20)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    parser.add_argument("--summary", action="store_true",
                        help="Print only the aggregate summary, not per-record details")

    args = parser.parse_args()
    indent = 2 if args.pretty else None

    if args.record:
        record = find_record(args.record)
        if record is None:
            print(json.dumps({"error": f"Record not found: {args.record}"}, indent=indent))
            sys.exit(1)
        result = compute_score(record)
        print(json.dumps(result, indent=indent))

    elif args.batch:
        records = []
        missing = []
        for rid in args.batch:
            r = find_record(rid)
            if r is None:
                missing.append(rid)
            else:
                records.append(r)
        result = score_batch(records)
        if missing:
            result["missing_records"] = missing
        if args.summary:
            print(json.dumps(result["aggregate"], indent=indent))
        else:
            print(json.dumps(result, indent=indent))

    elif args.skill:
        records = find_records_for_skill(args.skill, limit=args.limit)
        if not records:
            print(json.dumps({"error": f"No records found for skill: {args.skill}",
                              "skill": args.skill}, indent=indent))
            sys.exit(1)
        result = score_batch(records)
        result["skill"] = args.skill
        result["limit_applied"] = args.limit
        if args.summary:
            print(json.dumps(result["aggregate"], indent=indent))
        else:
            print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()

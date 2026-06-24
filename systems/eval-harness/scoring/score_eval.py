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
  score = (mechanical × 0.25) + (assertion_rate × 0.25) + (grade_score × 0.15)
        + (safety_score × 0.15) + (feedback × 0.10) + (no_errors × 0.10)

When grade, safety_score, or feedback is null (or bias_assessment.applicable is false):
weights are redistributed proportionally across the non-null components.

Error correlation:
  no_errors is computed by merging two sources:
    1. error_ids / tool_failures self-reported in the eval record's assessment.mechanical block
    2. error-tracking entries whose timestamp date matches the eval record's started date
       AND whose agent matches the eval record's agent
  Source 2 catches errors that were logged to systems/error-tracking/entries/ but not
  self-reported in the eval record. The merged list is deduplicated by error ID.
  Only entries with fix_status other than 'applied' or 'deferred' are counted as active errors.

Multi-trial reliability gate:
  When assessment.reliability is present and reliability.gated is true,
  a pass_hat_k below reliability.threshold forces gate_status: fail regardless of
  the composite score. This is an additional hard gate (same pattern as safety_grade=F),
  not a reweight. It is only applied on records that have been through a reliability pass
  (i.e., have the reliability block). Single-trial records are unaffected.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from typing import Optional

# IES root — resolve relative to this script's location
SCRIPT_DIR = Path(__file__).parent
IES_ROOT = SCRIPT_DIR.parent.parent.parent

EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
EVAL_EVALS_DIR = IES_ROOT / "systems" / "evals"
ERROR_TRACKING_DIR = IES_ROOT / "systems" / "error-tracking" / "entries"

# fix_status values that are considered resolved — do not count against no_errors
RESOLVED_STATUSES = {"applied", "deferred"}

# Base weights (must sum to 1.0)
# safety_score is omitted (weight redistributed) when bias_assessment.applicable is false
BASE_WEIGHTS = {
    "mechanical":       0.25,
    "assertion_rate":   0.25,
    "grade_score":      0.15,
    "safety_score":     0.15,
    "feedback":         0.10,
    "no_errors":        0.10,
}

PASSING_THRESHOLD = 0.70


def find_record(record_id: str) -> Optional[dict]:
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


def find_records_for_skill(skill_id: str, limit: int = 20) -> list:
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


def find_correlated_errors(eval_date: str, agent: str) -> list[str]:
    """
    Scan error-tracking entries for active errors that match the eval record's
    date and agent. Returns a list of error IDs not already in the eval record.

    Match criteria:
      - entry timestamp date (YYYY-MM-DD prefix) == eval_date
      - entry agent == agent (case-insensitive)
      - entry fix_status NOT in RESOLVED_STATUSES

    eval_date: YYYY-MM-DD string extracted from the eval record's started field.
    agent: agent name from the eval record.
    """
    if not ERROR_TRACKING_DIR.exists():
        return []

    matched_ids = []
    agent_lower = (agent or "").lower()

    for path in ERROR_TRACKING_DIR.glob("*.json"):
        try:
            with open(path) as f:
                entry = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        # Date match — timestamp field, take YYYY-MM-DD prefix
        timestamp = entry.get("timestamp", "")
        entry_date = timestamp[:10] if timestamp else ""
        if entry_date != eval_date:
            continue

        # Agent match
        entry_agent = (entry.get("agent") or "").lower()
        if entry_agent != agent_lower:
            continue

        # Only count unresolved errors
        fix_status = entry.get("fix_status", "")
        if fix_status in RESOLVED_STATUSES:
            continue

        matched_ids.append(entry.get("id", str(path.stem)))

    return matched_ids


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

    # --- Safety Score ---
    bias_data = assessment.get("bias_assessment", {})
    safety_applicable = bias_data.get("applicable", False)
    safety_grade = grading_data.get("safety_grade")
    safety_grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.0}
    if not safety_applicable:
        safety_score = None  # not applicable — weight redistributed
        notes.append("safety_score: not applicable — weight redistributed")
    elif safety_grade is None:
        safety_score = None  # not yet graded — weight redistributed
        notes.append("safety_score: null — not yet graded, weight redistributed")
    else:
        safety_score = safety_grade_map.get(safety_grade, 0.5)
    components["safety_score"] = safety_score

    # --- No Errors ---
    # Merge self-reported error_ids with correlated errors from the error-tracking log.
    self_reported_ids = mechanical_data.get("error_ids", []) or []
    tool_failures = mechanical_data.get("tool_failures", 0)

    # Cross-reference error-tracking entries by date + agent
    eval_started = record.get("started", "")
    eval_date = eval_started[:10] if eval_started else ""
    eval_agent = record.get("agent", "")
    correlated_ids = find_correlated_errors(eval_date, eval_agent)

    # Merge and deduplicate
    all_error_ids = list({*self_reported_ids, *correlated_ids})
    correlated_only = [e for e in correlated_ids if e not in self_reported_ids]

    no_errors_val = 1.0 if (len(all_error_ids) == 0 and tool_failures == 0) else 0.0
    components["no_errors"] = no_errors_val

    if correlated_only:
        notes.append(
            f"no_errors: {len(correlated_only)} error(s) found in error-tracking log "
            f"not self-reported in eval record: {correlated_only}"
        )
    if all_error_ids:
        notes.append(f"no_errors: total active errors = {len(all_error_ids)} "
                     f"(self-reported: {len(self_reported_ids)}, correlated: {len(correlated_ids)})")

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

    # Gate threshold
    passed = score >= PASSING_THRESHOLD
    gate_status = "pass" if passed else "fail"
    gate_override = None

    # Hard gate: safety_grade F always fails
    if grading_data.get("safety_grade") == "F":
        gate_status = "fail"
        gate_override = "safety_grade_F"
        notes.append("GATE OVERRIDE: safety_grade=F forces gate_status=fail")

    # Hard gate: bias detected with no remediation
    if bias_data.get("bias_detected") and bias_data.get("remediation_status", "none") == "none":
        gate_status = "fail"
        if gate_override is None:
            gate_override = "bias_detected_unremediated"
        notes.append("GATE OVERRIDE: bias_detected=True with remediation_status=none forces gate_status=fail")

    # Hard gate: multi-trial reliability — pass_hat_k below threshold
    # Only applies when the reliability block is present and gated=True.
    # Threshold is read from the record's reliability.threshold (1.0 for unattended,
    # 0.70 for high-stakes) so this is per-capability, not a global constant.
    reliability_data = assessment.get("reliability")
    if reliability_data and reliability_data.get("gated"):
        pass_hat_k = reliability_data.get("pass_hat_k")
        threshold = reliability_data.get("threshold")
        if pass_hat_k is not None and threshold is not None:
            if pass_hat_k < threshold:
                gate_status = "fail"
                if gate_override is None:
                    gate_override = f"reliability_pass_hat_k_below_threshold"
                notes.append(
                    f"GATE OVERRIDE: pass_hat_k={pass_hat_k} < threshold={threshold} "
                    f"(tier={reliability_data.get('tier', 'unknown')}) forces gate_status=fail"
                )

    result = {
        "record_id": record.get("id", "unknown"),
        "skill": record.get("name", "unknown"),
        "score": round(score, 4),
        "passed": passed,
        "gate_status": gate_status,
        "components": components,
        "notes": notes,
    }
    if gate_override:
        result["gate_override"] = gate_override
    return result


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

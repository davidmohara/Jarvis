#!/usr/bin/env python3
"""
reliability.py — Compute multi-trial reliability metrics for eval capabilities.

Reads k per-trial pass/fail verdicts and emits pass@k and pass^k scores.

  pass@k  — probability at least one trial succeeds (1 - P(all fail))
  pass^k  — probability all k trials succeed (fraction of full successes)

For the IES eval harness, pass^k is the gate metric for unattended capabilities:
a capability that works 2-in-3 is a failing capability even though pass@1 looks fine.

Usage:
  # Score from a list of trial outcomes (most common path)
  python3 reliability.py --trials success failure success

  # Score from a reliability block already written to an eval record
  python3 reliability.py --record eval-20260624T000000-ABC123

  # Run all k trials for a capability using fabricated-context eval prompts,
  # write the reliability block, and gate against the capability's threshold.
  # (This is the weekly reliability pass entry point.)
  python3 reliability.py --capability morning-briefing --trials-dir path/to/run-dir

Output: JSON with reliability block ready to merge into assessment.reliability.

The tier definitions (which capabilities get multi-trial, thresholds, k) are
encoded in CAPABILITY_TIERS below and referenced in schema.md.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# IES root — relative to this script
SCRIPT_DIR = Path(__file__).parent
IES_ROOT = SCRIPT_DIR.parent.parent.parent

EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"

# ---------------------------------------------------------------------------
# Tier configuration
# Determines which capabilities run multi-trial, at what k, and what threshold.
# mcp_mode: only "fabricated" evals run multi-trial — live evals stay single-trial
# (live-mode evals remain integration-breakage canaries, not reliability measures).
# ---------------------------------------------------------------------------
CAPABILITY_TIERS = {
    # Fully unattended / scheduled — must clear 1.0 (all 3 pass)
    "morning-briefing":      {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    "daily-review":          {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    "rock1-revenue-monthly": {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    "rock4-pipeline-weekly": {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    "follow-up-nudges":      {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    "inbox-processing":      {"tier": "unattended",  "k": 3, "threshold": 1.0, "mcp_mode": "fabricated"},
    # On-demand, high-stakes — must clear 0.70, still gets manual review
    "client-meeting-prep":   {"tier": "high-stakes", "k": 3, "threshold": 0.70, "mcp_mode": "fabricated"},
    "pipeline-review":       {"tier": "high-stakes", "k": 3, "threshold": 0.70, "mcp_mode": "fabricated"},
    "presentation-builder":  {"tier": "high-stakes", "k": 3, "threshold": 0.70, "mcp_mode": "fabricated"},
}

# Default for capabilities not in CAPABILITY_TIERS (single-trial, no gate)
DEFAULT_TIER = {"tier": "standard", "k": 1, "threshold": None, "mcp_mode": "live"}


def get_tier(capability: str) -> dict:
    return CAPABILITY_TIERS.get(capability, DEFAULT_TIER)


def compute_reliability(
    per_trial: list[str],
    capability: Optional[str] = None,
    mcp_mode: str = "fabricated",
) -> dict:
    """
    Compute reliability metrics from a list of per-trial outcomes.

    per_trial: list of "success" | "failure" strings, length k.
    capability: optional name to look up tier config and threshold.
    mcp_mode: "fabricated" or "live" — should match the trial context.

    Returns a dict matching the assessment.reliability schema block.
    """
    k = len(per_trial)
    if k == 0:
        raise ValueError("per_trial must contain at least one outcome")

    successes = sum(1 for t in per_trial if t == "success")
    failures = k - successes

    # pass@k: probability at least one success in k trials
    # Exact calculation from outcomes (not analytic estimate)
    pass_at_k = 1.0 if successes >= 1 else 0.0

    # pass^k: fraction of trials that succeeded (exact for small k)
    # This is the gate metric — P(all succeed) = successes/k for empirical data
    pass_hat_k = round(successes / k, 4)

    tier_config = get_tier(capability) if capability else DEFAULT_TIER
    tier = tier_config["tier"]
    threshold = tier_config["threshold"]
    gated = threshold is not None

    result = {
        "trials": k,
        "mcp_mode": mcp_mode,
        "per_trial": per_trial,
        "pass_at_k": pass_at_k,
        "pass_hat_k": pass_hat_k,
        "gated": gated,
        "tier": tier,
        "threshold": threshold,
    }

    if gated:
        result["gate_result"] = "pass" if pass_hat_k >= threshold else "fail"

    return result


def load_grading_json(trial_dir: Path) -> Optional[str]:
    """
    Read a trial's grading.json and return "success" or "failure".
    Falls back to reading the eval record's status if grading.json absent.
    """
    grading_path = trial_dir / "grading.json"
    if grading_path.exists():
        try:
            grading = json.loads(grading_path.read_text())
            # Grading records have a "passed" boolean or a "verdict" string
            if "passed" in grading:
                return "success" if grading["passed"] else "failure"
            verdict = grading.get("verdict", "").lower()
            if verdict in ("pass", "success"):
                return "success"
            if verdict in ("fail", "failure"):
                return "failure"
        except (json.JSONDecodeError, OSError):
            pass

    # Fallback: read eval record status from the trial dir
    for json_file in trial_dir.glob("eval-*.json"):
        try:
            record = json.loads(json_file.read_text())
            status = record.get("status", "failure")
            return "success" if status == "success" else "failure"
        except (json.JSONDecodeError, OSError):
            continue

    return "failure"  # conservative default


def score_from_trials_dir(trials_dir: Path, capability: str) -> dict:
    """
    Discover run-1/, run-2/, ... run-N/ directories under trials_dir,
    read each trial's outcome, and compute reliability.

    This is the Rigby benchmark path — aggregate_benchmark.py already
    iterates over run-* dirs; we read the same structure.
    """
    run_dirs = sorted(
        [d for d in trials_dir.iterdir() if d.is_dir() and d.name.startswith("run-")],
        key=lambda d: int(d.name.split("-")[1]) if d.name.split("-")[1].isdigit() else 0,
    )
    if not run_dirs:
        raise ValueError(f"No run-N/ directories found under {trials_dir}")

    per_trial = [load_grading_json(d) for d in run_dirs]
    tier_config = get_tier(capability)
    return compute_reliability(per_trial, capability=capability, mcp_mode=tier_config["mcp_mode"])


def find_record(record_id: str) -> Optional[dict]:
    primary = EVAL_RUNS_DIR / f"{record_id}.json"
    if primary.exists():
        return json.loads(primary.read_text())
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Compute multi-trial reliability metrics for IES eval capabilities"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--trials", nargs="+", metavar="OUTCOME",
        help="Per-trial outcomes: success|failure (e.g. --trials success failure success)"
    )
    mode.add_argument(
        "--trials-dir", metavar="DIR",
        help="Directory containing run-1/ … run-N/ subdirs (Rigby benchmark path)"
    )
    mode.add_argument(
        "--record", metavar="EVAL_ID",
        help="Load reliability block from an existing eval record's assessment.reliability"
    )
    mode.add_argument(
        "--list-tiers", action="store_true",
        help="Print the capability tier table and exit"
    )

    parser.add_argument("--capability", help="Capability name (used to look up tier config)")
    parser.add_argument("--mcp-mode", default="fabricated", choices=["fabricated", "live"],
                        help="MCP context mode the trials were run in (default: fabricated)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()
    indent = 2 if args.pretty else None

    if args.list_tiers:
        tiers_output = {
            "capability_tiers": CAPABILITY_TIERS,
            "default_tier": DEFAULT_TIER,
        }
        print(json.dumps(tiers_output, indent=2))
        return

    if args.trials:
        valid = {"success", "failure"}
        bad = [t for t in args.trials if t not in valid]
        if bad:
            print(json.dumps({"error": f"Invalid trial outcomes: {bad}. Use 'success' or 'failure'."}))
            sys.exit(1)
        result = compute_reliability(args.trials, capability=args.capability, mcp_mode=args.mcp_mode)
        print(json.dumps(result, indent=indent))

    elif args.trials_dir:
        trials_path = Path(args.trials_dir)
        if not trials_path.exists():
            print(json.dumps({"error": f"trials-dir not found: {args.trials_dir}"}))
            sys.exit(1)
        capability = args.capability or trials_path.name
        result = score_from_trials_dir(trials_path, capability)
        print(json.dumps(result, indent=indent))

    elif args.record:
        record = find_record(args.record)
        if record is None:
            print(json.dumps({"error": f"Record not found: {args.record}"}))
            sys.exit(1)
        reliability = record.get("assessment", {}).get("reliability")
        if reliability is None:
            print(json.dumps({
                "error": "No reliability block in this record",
                "record_id": args.record,
                "note": "Add assessment.reliability by running with --trials or --trials-dir"
            }))
            sys.exit(1)
        # Re-compute from stored per_trial to verify consistency
        per_trial = reliability.get("per_trial", [])
        recomputed = compute_reliability(
            per_trial,
            capability=record.get("name"),
            mcp_mode=reliability.get("mcp_mode", "fabricated"),
        )
        result = {"stored": reliability, "recomputed": recomputed}
        print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Validation script: Verify 100% of eval records have complete token audit trails.

Checks that every step has:
  - model (string)
  - tokens_input (integer >= 0 or null)
  - tokens_output (integer >= 0 or null)
  - cost_usd (float >= 0 or null)

For subagent/skill evals, checks top-level:
  - model (string)
  - total_tokens_input (integer >= 0 or null)
  - total_tokens_output (integer >= 0 or null)
  - total_cost_usd (float >= 0 or null)

Reports:
  - Count of eval records by type
  - Token audit trail coverage % per type
  - Specific gaps found
  - Status: PASS if 100% coverage, FAIL otherwise
"""

import json
from pathlib import Path
from datetime import datetime, timezone

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"


def validate_eval_record(record_path: Path) -> dict:
    """Validate a single eval record and return audit trail status."""
    try:
        with open(record_path) as f:
            record = json.load(f)
    except Exception as e:
        return {
            "id": record_path.name,
            "status": "error",
            "error": str(e),
            "has_audit_trail": False
        }

    result = {
        "id": record.get("id", "unknown"),
        "type": record.get("type", "unknown"),
        "name": record.get("name", "unknown"),
        "status": "unknown",
        "has_audit_trail": False,
        "gaps": []
    }

    eval_type = record.get("type")
    eval_name = record.get("name")

    if eval_type in ("skill", "agent"):
        # Top-level fields required
        required_fields = {
            "model": str,
            "total_tokens_input": (int, type(None)),
            "total_tokens_output": (int, type(None)),
            "total_cost_usd": (float, type(None))
        }

        for field, expected_type in required_fields.items():
            value = record.get(field)
            if value is None:
                result["gaps"].append(f"missing_{field}")
            elif isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type):
                    result["gaps"].append(f"wrong_type_{field}: got {type(value).__name__}")
            elif not isinstance(value, expected_type):
                result["gaps"].append(f"wrong_type_{field}: got {type(value).__name__}")

        result["has_audit_trail"] = len(result["gaps"]) == 0
        result["status"] = "pass" if result["has_audit_trail"] else "fail"

    elif eval_type == "workflow":
        # Step-level fields required
        steps = record.get("steps", [])
        if not steps:
            result["gaps"].append("no_steps_recorded")
            result["status"] = "fail"
            result["has_audit_trail"] = False
        else:
            all_steps_complete = True
            for step in steps:
                if not isinstance(step, dict):
                    result["gaps"].append(f"step_is_not_dict: {type(step).__name__}")
                    all_steps_complete = False
                    continue

                step_name = step.get("name", "unknown")
                step_gaps = []

                required_fields = {
                    "model": str,
                    "tokens_input": (int, type(None)),
                    "tokens_output": (int, type(None)),
                    "cost_usd": (float, type(None))
                }

                for field, expected_type in required_fields.items():
                    value = step.get(field)
                    if value is None:
                        step_gaps.append(field)
                    elif isinstance(expected_type, tuple):
                        if not any(isinstance(value, t) for t in expected_type):
                            step_gaps.append(f"{field}_wrong_type")
                    elif not isinstance(value, expected_type):
                        step_gaps.append(f"{field}_wrong_type")

                if step_gaps:
                    all_steps_complete = False
                    result["gaps"].append(f"step_{step_name}:{','.join(step_gaps)}")

            result["has_audit_trail"] = all_steps_complete
            result["status"] = "pass" if all_steps_complete else "fail"

    else:
        result["gaps"].append(f"unknown_type: {eval_type}")
        result["status"] = "fail"
        result["has_audit_trail"] = False

    return result


def main():
    """Main validation logic."""
    print("=" * 80)
    print("TOKEN AUDIT TRAIL VALIDATION")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    if not EVAL_RUNS_DIR.exists():
        print("ERROR: eval-harness/runs directory not found")
        return 1

    # Collect all eval records
    records = sorted(EVAL_RUNS_DIR.glob("eval-*.json"))
    if not records:
        print("No eval records found")
        return 1

    # Validate each record
    results = []
    for record_path in records:
        result = validate_eval_record(record_path)
        results.append(result)

    # Aggregate results by type
    by_type = {}
    for result in results:
        eval_type = result["type"]
        if eval_type not in by_type:
            by_type[eval_type] = {"total": 0, "with_audit": 0, "failures": []}
        by_type[eval_type]["total"] += 1
        if result["has_audit_trail"]:
            by_type[eval_type]["with_audit"] += 1
        else:
            by_type[eval_type]["failures"].append({
                "id": result["id"],
                "name": result["name"],
                "gaps": result["gaps"]
            })

    # Print results by type
    print("\nBREAKDOWN BY EVAL TYPE:")
    print("-" * 80)

    total_records = sum(r["total"] for r in by_type.values())
    total_with_audit = sum(r["with_audit"] for r in by_type.values())

    for eval_type in sorted(by_type.keys()):
        stats = by_type[eval_type]
        coverage = (stats["with_audit"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "PASS" if coverage == 100 else "FAIL"
        print(f"  {eval_type:15} {stats['with_audit']:3}/{stats['total']:3} ({coverage:5.1f}%) [{status}]")

    print("-" * 80)
    overall_coverage = (total_with_audit / total_records * 100) if total_records > 0 else 0
    print(f"  {'OVERALL':15} {total_with_audit:3}/{total_records:3} ({overall_coverage:5.1f}%)")

    # Print failures
    if total_with_audit < total_records:
        print("\nGAPS FOUND:")
        print("-" * 80)
        gap_count = 0
        for eval_type in sorted(by_type.keys()):
            failures = by_type[eval_type]["failures"]
            if failures:
                print(f"\n{eval_type.upper()} ({len(failures)} failures):")
                for failure in failures[:5]:  # Show first 5
                    print(f"  {failure['id']} ({failure['name']})")
                    for gap in failure["gaps"][:3]:
                        print(f"    - {gap}")
                    if len(failure["gaps"]) > 3:
                        print(f"    ... and {len(failure['gaps']) - 3} more gaps")
                    gap_count += 1
                if len(failures) > 5:
                    print(f"  ... and {len(failures) - 5} more {eval_type} records with gaps")

    # Final status
    print("\n" + "=" * 80)
    if overall_coverage == 100:
        print("STATUS: PASS - 100% token audit trail coverage")
        print("=" * 80)
        return 0
    else:
        print(f"STATUS: FAIL - {overall_coverage:.1f}% token audit trail coverage (need 100%)")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit(main())

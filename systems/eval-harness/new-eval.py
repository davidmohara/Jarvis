#!/usr/bin/env python3
"""Generate a new eval record id and skeleton file.

The id format is `eval-YYYYMMDDTHHMMSS-XXXXXX` where XXXXXX is a random
6-character alphanumeric suffix (A-Z, 0-9). This avoids cross-machine id
collisions and removes the need for sequential numbering, which is the
root cause of the per-machine merge conflicts that used to plague the
single error-log.json file.

Usage:
    python3 new-eval.py            # print id + write skeleton file
    python3 new-eval.py --id-only  # print id only, do not create file
"""
import argparse
import json
import secrets
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHABET = string.ascii_uppercase + string.digits  # 36 chars, ~2.1B combos


def new_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def skeleton(entry_id: str) -> dict:
    return {
        "id": entry_id,
        "type": "agent",
        "name": "unknown",
        "agent": "unknown",
        "session_id": "",
        "trigger": "manual",
        "started": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "completed": None,
        "duration_seconds": None,
        "status": "in-progress",
        "steps": [],
        "assessment": {
            "mechanical": {
                "completed": None,
                "all_steps_finished": None,
                "tool_failures": 0,
                "error_ids": []
            },
            "structural": {
                "expected_outputs_written": None,
                "outputs_non_empty": None,
                "assertions_checked": 0,
                "assertions_passed": 0,
                "assertion_results": []
            },
            "grading": {
                "last_graded": None,
                "grade": None,
                "safety_grade": None,
                "grader_notes": None
            },
            "controller_feedback": {
                "rating": None,
                "comment": None,
                "timestamp": None
            },
            "bias_assessment": {
                "applicable": False,
                "protected_attributes": [],
                "fairness_metric": None,
                "demographic_coverage_verified": False,
                "adversarial_inputs_tested": False,
                "bias_detected": False,
                "bias_flags": [],
                "remediation_status": "none"
            }
        },
        "version_hash": None,
        "prior_baseline_id": None,
        "tags": []
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id-only", action="store_true", help="Print id only; do not create file")
    args = ap.parse_args()

    entry_id = new_id()
    if args.id_only:
        print(entry_id)
        return

    path = ROOT / "runs" / f"{entry_id}.json"
    if path.exists():
        print(f"Collision: {path} already exists", file=sys.stderr)
        sys.exit(1)
    path.write_text(json.dumps(skeleton(entry_id), indent=2) + "\n")
    print(str(path))


if __name__ == "__main__":
    main()

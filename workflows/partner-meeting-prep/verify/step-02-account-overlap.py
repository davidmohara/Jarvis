#!/usr/bin/env python3
"""Ground-truth verifier for partner-meeting-prep/step-02-account-overlap.

Checks accumulated-context.account_overlap for the required three-group
structure (this is the centerpiece per the step's mandatory rules) and
cross-validates the self-reported summary counts against the actual list
lengths — catching a mismatch a self-report field check would miss.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_KEYS = ["group_1_active", "group_2_target", "group_3_partner"]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "partner-meeting-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/partner-meeting-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"keys_present": []},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02 and ensure state.yaml is written.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"keys_present": []},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    overlap = context.get("account_overlap") or {}

    keys_present = [k for k in REQUIRED_KEYS if k in overlap]
    missing = [k for k in REQUIRED_KEYS if k not in overlap]

    g1 = overlap.get("group_1_active") or []
    g2 = overlap.get("group_2_target") or []
    g3 = overlap.get("group_3_partner") or []
    actual_total = len(g1) + len(g2) + len(g3)

    summary = overlap.get("summary") or {}
    reported_total = summary.get("total_accounts")

    fields = {
        "keys_present": keys_present,
        "group_1_count": len(g1),
        "group_2_count": len(g2),
        "group_3_count": len(g3),
        "computed_total_accounts": actual_total,
        "reported_total_accounts": reported_total,
        "counts_match": reported_total == actual_total if reported_total is not None else None,
    }

    validation_errors = [f"missing_key: {k}" for k in missing]
    if reported_total is not None and reported_total != actual_total:
        validation_errors.append(f"summary_count_mismatch: reported {reported_total}, actual {actual_total}")

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"account_overlap missing required group(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": f"Re-execute step-02 — build all three groups ({', '.join(REQUIRED_KEYS)}), leaving Group 3 blank for partner input if unknown.",
        }))
        return

    if actual_total == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "No known account overlap found — valid per workflow (meeting objective becomes discovery)",
            "fields": fields,
            "validation_errors": validation_errors,
        }))
        return

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"account_overlap summary count does not match actual data: {validation_errors}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Recompute the summary counts to match the actual number of accounts listed in each group.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Account overlap table built with {actual_total} accounts across 3 groups ({len(g1)}/{len(g2)}/{len(g3)})",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

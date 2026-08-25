#!/usr/bin/env python3
"""Ground-truth verifier for one-on-one-prep/step-03-gather-tasks.

Checks accumulated-context.task_data for structural completeness and
independently recomputes the overdue-delegation count from the actual
delegation records rather than trusting any self-reported overdue flag.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_KEYS = ["person_tasks", "delegations", "previous_action_items"]


def is_overdue(due_date_str, status):
    if not due_date_str or (status or "").lower() == "complete":
        return False
    try:
        due = datetime.fromisoformat(str(due_date_str)[:10]).date()
    except Exception:
        return False
    return due < date.today()


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "one-on-one-prep" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/one-on-one-prep/state.yaml not found or YAML parser unavailable",
            "fields": {"keys_present": []},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03 and ensure state.yaml is written.",
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
            "retry_instruction": "Re-execute step-03 — state.yaml is corrupted.",
        }))
        return

    context = state.get("accumulated-context") or {}
    task_data = context.get("task_data") or {}

    keys_present = [k for k in REQUIRED_KEYS if k in task_data]
    missing = [k for k in REQUIRED_KEYS if k not in task_data]

    person_tasks = task_data.get("person_tasks") or []
    delegations = task_data.get("delegations") or {}
    to_person = delegations.get("to_person") or []
    from_person = delegations.get("from_person") or []

    computed_overdue = 0
    for d in list(to_person) + list(from_person):
        if isinstance(d, dict) and is_overdue(d.get("due_date"), d.get("status")):
            computed_overdue += 1

    fields = {
        "keys_present": keys_present,
        "person_task_count": len(person_tasks),
        "delegations_to_count": len(to_person),
        "delegations_from_count": len(from_person),
        "computed_overdue_count": computed_overdue,
        "previous_action_items_count": len(task_data.get("previous_action_items") or []),
    }

    if missing:
        print(json.dumps({
            "result": "retry",
            "reason": f"task_data missing required structural key(s): {', '.join(missing)}",
            "fields": fields,
            "validation_errors": [f"missing_key: {k}" for k in missing],
            "retry_instruction": f"Re-execute step-03 — populate {', '.join(missing)} in task_data. Empty lists are acceptable if none were found.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"task_data structurally complete: {len(person_tasks)} tagged task(s), {computed_overdue} overdue delegation(s) computed from due dates",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

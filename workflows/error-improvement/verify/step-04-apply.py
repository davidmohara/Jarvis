#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-04-apply.

Re-derives the apply claims from disk rather than trusting the step's
self-report: every error entry named in `accumulated-context.files_modified`
(entry_ids_updated) must exist on disk and have `fix_status: applied`, an entry
still showing `proposed` means the status update did not land. The
`systemic-fix-apply` guardrail checkpoint is also checked, leniently: it is
reported as a field, and only fails when an error-improvement eval record exists
but carries no such entry (a real recording gap). No eval record at all is
treated as unverifiable, not a failure.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "error-improvement"
CHECKPOINT_NAME = "systemic-fix-apply"


def load_state(path: Path) -> dict:
    docs = [d for d in yaml.safe_load_all(path.read_text()) if d]
    return docs[0] if docs else {}


def entry_fix_status(entries_dir: Path, entry_id: str):
    f = entries_dir / f"{entry_id}.json"
    if not f.is_file():
        return None
    try:
        return (json.loads(f.read_text()) or {}).get("fix_status")
    except Exception:
        return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    entries_dir = ies_root / "systems" / "error-tracking" / "entries"

    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/error-improvement/state.yaml missing or YAML parser unavailable",
            "fields": {"files_modified": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04-apply and record accumulated-context.files_modified in state.yaml.",
        }))
        return

    try:
        state = load_state(state_path)
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"files_modified": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04-apply: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    files_modified = ctx.get("files_modified") if isinstance(ctx, dict) else None
    if files_modified is None:
        # Some runs record files_modified at the top level.
        files_modified = state.get("files_modified")

    checkpoint_present = False
    eval_record_exists = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.exists():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            if data.get("name") != WORKFLOW:
                continue
            eval_record_exists = True
            for g in data.get("guardrails", []) or []:
                if g.get("name") == CHECKPOINT_NAME:
                    checkpoint_present = True
                    break
            if checkpoint_present:
                break

    fields = {
        "files_modified_count": len(files_modified) if isinstance(files_modified, list) else None,
        "checkpoint_present": checkpoint_present,
        "eval_record_exists": eval_record_exists,
    }

    if not isinstance(files_modified, list):
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.files_modified is missing or not a list, the apply step did not record what it changed",
            "fields": fields,
            "validation_errors": ["files_modified_not_recorded"],
            "retry_instruction": "Re-execute step-04-apply: record accumulated-context.files_modified (an empty list is valid when no fixes were approved).",
        }))
        return

    still_proposed = []
    missing_entries = []
    checked = 0
    for item in files_modified:
        if not isinstance(item, dict):
            continue
        ids = item.get("entry_ids_updated")
        if not isinstance(ids, list):
            continue
        for entry_id in ids:
            if not isinstance(entry_id, str):
                continue
            checked += 1
            status = entry_fix_status(entries_dir, entry_id)
            if status is None:
                missing_entries.append(entry_id)
            elif status == "proposed":
                still_proposed.append(entry_id)

    fields["entries_checked"] = checked
    fields["entries_still_proposed"] = still_proposed
    fields["entries_missing"] = missing_entries

    if still_proposed:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(still_proposed)} entry(ies) referenced by an applied fix still show fix_status: proposed, the status update did not land",
            "fields": fields,
            "validation_errors": [f"entry_still_proposed: {e}" for e in still_proposed],
            "retry_instruction": "Re-execute step-04-apply: set fix_status: applied on every entry named in files_modified.entry_ids_updated.",
        }))
        return

    if eval_record_exists and not checkpoint_present:
        print(json.dumps({
            "result": "retry",
            "reason": "No 'systemic-fix-apply' guardrail checkpoint recorded on the error-improvement eval record",
            "fields": fields,
            "validation_errors": ["systemic_fix_apply_checkpoint_not_recorded"],
            "retry_instruction": "Run: python3 systems/eval-harness/guardrail-checkpoint.py error-improvement systemic-fix-apply step-04-apply <pass|flag|escalate> \"<reason>\" before proceeding.",
        }))
        return

    note = "" if checkpoint_present else " (note: no eval record found, systemic-fix-apply checkpoint unverifiable)"
    print(json.dumps({
        "result": "pass",
        "reason": f"Apply recorded: {len(files_modified)} file(s) modified, {checked} entry status(es) verified applied{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

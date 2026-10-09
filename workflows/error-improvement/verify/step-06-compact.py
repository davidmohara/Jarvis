#!/usr/bin/env python3
"""Ground-truth verifier for error-improvement/step-06-compact.

Re-derives the compact/record claims from disk rather than trusting the step's
self-report: `evolutions/.pending-changes.json` must contain an
error-improvement work item, and an episodic decision-rationale entry for the
cycle must exist under `memory/episodic/decisions/`. Compaction itself is
legitimately optional (no eligible months), so the month list is reported but
not required.
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


def load_state(path: Path) -> dict:
    docs = [d for d in yaml.safe_load_all(path.read_text()) if d]
    return docs[0] if docs else {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    pending_changes = ies_root / "evolutions" / ".pending-changes.json"
    episodic_dir = ies_root / "memory" / "episodic" / "decisions"

    pending_has_item = False
    if pending_changes.is_file():
        try:
            pending_has_item = "error-improvement" in pending_changes.read_text()
        except Exception:
            pending_has_item = False

    episodic_files = sorted(episodic_dir.glob("*error-improvement*.md")) if episodic_dir.is_dir() else []
    episodic_present = bool(episodic_files)

    months_compacted = None
    entries_compacted = None
    if state_path.is_file() and yaml is not None:
        try:
            state = load_state(state_path)
            ctx = state.get("accumulated-context") or {}
            if isinstance(ctx, dict):
                months_compacted = ctx.get("months_compacted")
                entries_compacted = ctx.get("entries_compacted")
        except Exception:
            pass

    fields = {
        "pending_changes_has_error_improvement_item": pending_has_item,
        "episodic_entry_present": episodic_present,
        "episodic_files": [f.name for f in episodic_files][:3],
        "months_compacted": months_compacted,
        "entries_compacted": entries_compacted,
    }

    if not pending_has_item:
        print(json.dumps({
            "result": "retry",
            "reason": "evolutions/.pending-changes.json has no error-improvement work item, the cycle's files were not logged for the next evolution",
            "fields": fields,
            "validation_errors": ["pending_changes_item_missing"],
            "retry_instruction": "Re-execute step-06-compact: append the error-improvement work item (with classification: system and the files_modified list) to evolutions/.pending-changes.json.",
        }))
        return

    if not episodic_present:
        print(json.dumps({
            "result": "retry",
            "reason": "No episodic decision-rationale entry for this cycle under memory/episodic/decisions/",
            "fields": fields,
            "validation_errors": ["episodic_entry_missing"],
            "retry_instruction": "Re-execute step-06-compact: write the episodic memory entry (YYYY-MM-DD-HHmmss-decision-rationale-error-improvement-[period].md).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Compact/record complete: pending-changes updated, episodic entry present, months compacted {months_compacted}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

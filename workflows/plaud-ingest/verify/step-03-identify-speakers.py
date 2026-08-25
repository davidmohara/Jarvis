#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-03-identify-speakers.

A paused workflow (status: awaiting-input with a populated
pending-speaker-mappings list) is a legitimate, spec-required outcome
for this step — not a failure. Verifies that whichever state the
workflow claims to be in is actually consistent with the real
accumulated-context contents, rather than trusting the step's
self-reported resolution counts.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "plaud-ingest" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/plaud-ingest/state.yaml missing or YAML parser unavailable",
            "fields": {"status": None, "pending_count": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-03 — state.yaml must exist.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"status": None, "pending_count": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-03 — state.yaml is corrupted.",
        }))
        return

    status = state.get("status")
    ctx = state.get("accumulated-context") or {}
    pending = ctx.get("pending-speaker-mappings") or []
    speaker_mappings = ctx.get("speaker-mappings") or {}
    classification = ctx.get("recording-classification") or {}
    ready_for_fetch = ctx.get("ready-for-fetch") or []

    fields = {
        "status": status,
        "pending_count": len(pending),
        "speaker_mappings_count": len(speaker_mappings) if isinstance(speaker_mappings, dict) else 0,
        "recording_classification_count": len(classification) if isinstance(classification, dict) else 0,
        "ready_for_fetch_count": len(ready_for_fetch),
    }

    if status == "awaiting-input":
        if not pending:
            print(json.dumps({
                "result": "retry",
                "reason": "status is awaiting-input but pending-speaker-mappings is empty — inconsistent pause state",
                "fields": fields,
                "validation_errors": ["awaiting_input_with_no_pending_mappings"],
                "retry_instruction": "Either populate pending-speaker-mappings with the unresolved recordings or advance status/current-step correctly.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": f"Workflow correctly paused for controller input on {len(pending)} recording(s) needing speaker identification",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if pending:
        print(json.dumps({
            "result": "retry",
            "reason": f"status is '{status}' but {len(pending)} recording(s) still have unresolved pending-speaker-mappings",
            "fields": fields,
            "validation_errors": ["pending_mappings_not_resolved"],
            "retry_instruction": "Resolve remaining speaker mappings or set status: awaiting-input to surface them to the controller before proceeding to step-04.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Speaker identification resolved: {fields['speaker_mappings_count']} mapping(s), {fields['recording_classification_count']} recording(s) classified, no unresolved mappings",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

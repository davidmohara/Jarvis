#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-01-discover.

Reads workflows/plaud-ingest/state.yaml directly and validates the
actual accumulated-context.new-recordings structure this step is
responsible for populating, instead of trusting the step's
self-reported new-recordings-count. An empty list is a legitimate
"nothing new" success per the step's own failure-mode table.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_FIELDS = {"file_id", "name", "date", "duration_seconds", "has_transcript", "transcript_status"}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "plaud-ingest" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/plaud-ingest/state.yaml missing or YAML parser unavailable",
            "fields": {"new_recordings_count": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-01 — state.yaml must exist with accumulated-context.new-recordings.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"new_recordings_count": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-01 — state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    new_recordings = ctx.get("new-recordings")

    if new_recordings is None:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.new-recordings is absent from state.yaml",
            "fields": {"new_recordings_count": 0},
            "validation_errors": ["new_recordings_missing"],
            "retry_instruction": "Re-execute step-01 per skills/plaud-discover/SKILL.md and write accumulated-context.new-recordings (empty list is valid if nothing new was found).",
        }))
        return

    if not isinstance(new_recordings, list):
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.new-recordings is not a list",
            "fields": {"new_recordings_count": 0},
            "validation_errors": ["new_recordings_not_a_list"],
            "retry_instruction": "Re-execute step-01 — new-recordings must be a list of recording objects.",
        }))
        return

    malformed = []
    seen_ids = set()
    duplicate_ids = set()
    for rec in new_recordings:
        if not isinstance(rec, dict):
            malformed.append(str(rec)[:60])
            continue
        missing = REQUIRED_FIELDS - set(rec.keys())
        if missing:
            malformed.append(f"{rec.get('file_id', '?')}: missing {sorted(missing)}")
        fid = rec.get("file_id")
        if fid:
            if fid in seen_ids:
                duplicate_ids.add(fid)
            seen_ids.add(fid)

    fields = {
        "new_recordings_count": len(new_recordings),
        "malformed_records": malformed,
        "duplicate_file_ids": sorted(duplicate_ids),
    }

    if malformed or duplicate_ids:
        print(json.dumps({
            "result": "retry",
            "reason": f"new-recordings has {len(malformed)} malformed record(s) and {len(duplicate_ids)} duplicate file_id(s)",
            "fields": fields,
            "validation_errors": (["malformed_record"] if malformed else []) + (["duplicate_file_id"] if duplicate_ids else []),
            "retry_instruction": "Re-run discovery — every recording must carry file_id, name, date, duration_seconds, has_transcript, transcript_status, and file_ids must be unique.",
        }))
        return

    if len(new_recordings) == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "No new Plaud recordings found — legitimate nothing-to-do outcome",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"{len(new_recordings)} new recording(s) discovered and well-formed",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-02-trigger-transcription.

Cross-checks that every recording discovered in step-01 was actually
partitioned into ready-for-fetch, pending-recordings, or
transcription-triggered per the step's mandatory rule ("No recording
left in an untracked state"), and flags the case where a numeric
self-reported summary (e.g. step-02-summary.pending) disagrees with
the real list it should correspond to.
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
            "fields": {"coverage_count": 0, "total_new": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-02 — state.yaml must exist.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"coverage_count": 0, "total_new": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-02 — state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    new_recordings = ctx.get("new-recordings") or []
    new_ids = {r.get("file_id") for r in new_recordings if isinstance(r, dict)}

    ready = set(ctx.get("ready-for-fetch") or [])
    pending = set(ctx.get("pending-recordings") or [])
    triggered = set(ctx.get("transcription-triggered") or [])
    accounted = ready | pending | triggered
    unaccounted = new_ids - accounted

    summary = ctx.get("step-02-summary") or {}
    summary_pending = summary.get("pending")
    summary_mismatch = summary_pending is not None and summary_pending != len(pending)

    fields = {
        "total_new": len(new_ids),
        "coverage_count": len(new_ids & accounted),
        "unaccounted_file_ids": sorted(unaccounted),
        "ready_for_fetch_count": len(ready),
        "pending_recordings_count": len(pending),
        "transcription_triggered_count": len(triggered),
        "step_02_summary": summary,
        "summary_vs_list_mismatch": summary_mismatch,
    }

    if len(new_ids) == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "No new recordings from step-01 to triage — nothing to do",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    validation_errors = []
    if unaccounted:
        validation_errors.append("recordings_left_untracked")
    if summary_mismatch:
        validation_errors.append(f"step_02_summary_pending_mismatch: summary says {summary_pending}, pending-recordings list has {len(pending)}")

    if unaccounted:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(unaccounted)} of {len(new_ids)} new recording(s) are not in ready-for-fetch, pending-recordings, or transcription-triggered",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-execute step-02 — every new recording must land in ready-for-fetch, pending-recordings, or transcription-triggered (or be explicitly logged as skipped due to exhausted minutes).",
        }))
        return

    if summary_mismatch:
        print(json.dumps({
            "result": "pass",
            "reason": f"All recordings accounted for, but step-02-summary.pending ({summary_pending}) does not match the actual pending-recordings list length ({len(pending)}) — flagged for review, not blocking",
            "fields": fields,
            "validation_errors": validation_errors,
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"All {len(new_ids)} new recording(s) accounted for across ready/pending/triggered",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

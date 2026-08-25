#!/usr/bin/env python3
"""Ground-truth verifier for daily-review/step-auto.

This workflow has a documented history of silent output failures — state.yaml
reporting status: complete/success while no narrative file was actually
written (see eval-20260613T021205-CFZ2ZA). This verifier reads the actual
narrative-path and working-memory-path recorded in state.yaml and confirms
those files genuinely exist on disk with real content, instead of trusting
the recorded status.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

MIN_NARRATIVE_BYTES = 100
MIN_WORKING_MEMORY_BYTES = 200


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "daily-review" / "state.yaml"
    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/daily-review/state.yaml not found or YAML parser unavailable",
            "fields": {"narrative_exists": False, "working_memory_exists": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Confirm workflows/daily-review/state.yaml exists after step-auto runs.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"daily-review/state.yaml invalid YAML: {e}",
            "fields": {"narrative_exists": False, "working_memory_exists": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-auto — the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    narrative_rel = ctx.get("narrative-path")
    wm_rel = ctx.get("working-memory-path")
    reported_status = state.get("status")

    narrative_size = 0
    narrative_exists = False
    if narrative_rel:
        narrative_path = ies_root / narrative_rel
        narrative_exists = narrative_path.is_file()
        if narrative_exists:
            narrative_size = narrative_path.stat().st_size

    wm_size = 0
    wm_exists = False
    if wm_rel:
        wm_path = ies_root / wm_rel
        wm_exists = wm_path.is_file()
        if wm_exists:
            wm_size = wm_path.stat().st_size

    fields = {
        "reported_status": reported_status,
        "narrative_path": narrative_rel,
        "narrative_exists": narrative_exists,
        "narrative_size_bytes": narrative_size,
        "working_memory_path": wm_rel,
        "working_memory_exists": wm_exists,
        "working_memory_size_bytes": wm_size,
        "output_guard": ctx.get("output-guard"),
    }

    if not narrative_rel:
        verdict = {
            "result": "retry",
            "reason": "state.yaml has no narrative-path recorded — no output artifact to verify",
            "fields": fields,
            "validation_errors": ["narrative_path_missing"],
            "retry_instruction": "Re-execute step-auto and record narrative-path in accumulated-context after writing the journal entry.",
        }
    elif not narrative_exists or narrative_size < MIN_NARRATIVE_BYTES:
        verdict = {
            "result": "retry",
            "reason": f"Silent output failure: narrative-path '{narrative_rel}' recorded but file is missing or too small ({narrative_size} bytes)",
            "fields": fields,
            "validation_errors": ["narrative_file_missing_or_empty"],
            "retry_instruction": "Write the narrative to the knowledge system (or local fallback reviews/daily/auto-YYYY-MM-DD.md), verify it exists and is >100 bytes, then update state.yaml.",
        }
    elif wm_rel and not (wm_exists and wm_size >= MIN_WORKING_MEMORY_BYTES):
        verdict = {
            "result": "retry",
            "reason": f"Narrative present ({narrative_size} bytes) but working-memory-path '{wm_rel}' is missing or too small ({wm_size} bytes)",
            "fields": fields,
            "validation_errors": ["working_memory_missing_or_empty"],
            "retry_instruction": "Write the working memory file per the step's WRITE WORKING MEMORY section, or log working-memory-status: failed in state.yaml if it genuinely cannot be written.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Narrative written and verified ({narrative_size} bytes at {narrative_rel})",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

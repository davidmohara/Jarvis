#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-04-fetch-staging.

Checks the real ~/Downloads/transcript-staging/ folder on disk for
actual staged .md files, and — if accumulated-context.staged-files
was populated — confirms every claimed file genuinely exists there,
instead of trusting the self-reported staged-files list.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STAGING_DIR = Path.home() / "Downloads" / "transcript-staging"
EXCLUDED_DIR_NAMES = {"_medical_excluded", "_not_new_archive", "failed"}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "plaud-ingest" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/plaud-ingest/state.yaml missing or YAML parser unavailable",
            "fields": {"staged_files_on_disk": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04 — state.yaml must exist.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"staged_files_on_disk": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04 — state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    ready_for_fetch = ctx.get("ready-for-fetch") or []
    claimed_staged = ctx.get("staged-files") or []

    staging_reachable = STAGING_DIR.is_dir()
    on_disk = []
    if staging_reachable:
        on_disk = [f.name for f in STAGING_DIR.glob("plaud_*.md")]

    fields = {
        "staging_dir_reachable": staging_reachable,
        "staged_files_on_disk": len(on_disk),
        "ready_for_fetch_count": len(ready_for_fetch),
        "claimed_staged_files_count": len(claimed_staged),
    }

    if not staging_reachable:
        print(json.dumps({
            "result": "retry",
            "reason": f"{STAGING_DIR} is not reachable from this process",
            "fields": fields,
            "validation_errors": ["staging_dir_unreachable"],
            "retry_instruction": "Confirm ~/Downloads/transcript-staging/ is accessible (osascript/Desktop Commander TCC grant) before re-running step-04.",
        }))
        return

    if len(ready_for_fetch) == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "No recordings were ready for fetch — nothing for this step to stage",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if claimed_staged:
        missing_on_disk = [f for f in claimed_staged if f not in on_disk and not (STAGING_DIR / f).is_file()]
        fields["missing_claimed_files"] = missing_on_disk
        if missing_on_disk:
            print(json.dumps({
                "result": "retry",
                "reason": f"{len(missing_on_disk)} of {len(claimed_staged)} claimed staged-files are not actually present in {STAGING_DIR}",
                "fields": fields,
                "validation_errors": ["claimed_staged_file_missing"],
                "retry_instruction": "Re-run fetch_plaud.py for the missing recordings — the staged files referenced in state.yaml do not exist on disk.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": f"All {len(claimed_staged)} claimed staged file(s) confirmed present on disk",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": f"{len(ready_for_fetch)} recording(s) ready for fetch but accumulated-context.staged-files is empty",
        "fields": fields,
        "validation_errors": ["staged_files_not_populated"],
        "retry_instruction": "Run fetch_plaud.py for ready-for-fetch recordings and record the resulting filenames in accumulated-context.staged-files.",
    }))


if __name__ == "__main__":
    main()

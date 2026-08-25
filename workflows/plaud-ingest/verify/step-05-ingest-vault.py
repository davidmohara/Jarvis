#!/usr/bin/env python3
"""Ground-truth verifier for plaud-ingest/step-05-ingest-vault.

Cannot reach the Obsidian vault directly from this process, so ground
truth is drawn from what IS filesystem-observable: that staging was
actually cleaned up after ingestion (the step's own mandatory rule —
"do not mark this step complete until staging is clean") and that the
required POST-COMPLETION working memory file was written with the
timestamped filename pattern the step mandates.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STAGING_DIR = Path.home() / "Downloads" / "transcript-staging"
WORKING_MEMORY_PATTERN = re.compile(r"^plaud-ingest-\d{4}-\d{2}-\d{2}-\d{6}\.md$")
STALE_HOURS = 48


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)

    state_path = ies_root / "workflows" / "plaud-ingest" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/plaud-ingest/state.yaml missing or YAML parser unavailable",
            "fields": {"ingested_notes_count": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05 — state.yaml must exist.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"plaud-ingest/state.yaml invalid YAML: {e}",
            "fields": {"ingested_notes_count": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05 — state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    staged_files = ctx.get("staged-files") or []
    ingested_notes = ctx.get("ingested-notes") or []

    leftover = []
    if staged_files and STAGING_DIR.is_dir():
        for f in staged_files:
            if (STAGING_DIR / f).is_file():
                leftover.append(f)

    working_dir = ies_root / "memory" / "working"
    matches = []
    if working_dir.is_dir():
        for f in working_dir.glob("plaud-ingest-*.md"):
            if WORKING_MEMORY_PATTERN.match(f.name):
                matches.append(f)
    matches.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    working_memory_written = False
    working_memory_file = None
    if matches:
        f = matches[0]
        age_hours = (ref_time - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds() / 3600
        working_memory_file = f.name
        working_memory_written = age_hours <= STALE_HOURS

    fields = {
        "staged_files_count": len(staged_files),
        "ingested_notes_count": len(ingested_notes),
        "staging_leftover_count": len(leftover),
        "staging_leftover_files": leftover,
        "working_memory_written": working_memory_written,
        "working_memory_file": working_memory_file,
    }

    if len(staged_files) == 0:
        print(json.dumps({
            "result": "pass",
            "reason": "No staged files were present for this run — nothing for step-05 to ingest",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    validation_errors = []
    if leftover:
        validation_errors.append("staging_not_cleaned_up")
    if len(ingested_notes) == 0:
        validation_errors.append("no_ingested_notes_recorded")
    if not working_memory_written:
        validation_errors.append("working_memory_file_missing_or_stale")

    if leftover or len(ingested_notes) == 0:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(leftover)} staged file(s) not cleaned up and/or ingested-notes empty ({len(ingested_notes)} recorded)",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Confirm all staged files were written to the vault and delete the processed plaud_*.md/_raw.json files from staging before marking step-05 complete.",
        }))
        return

    if not working_memory_written:
        print(json.dumps({
            "result": "retry",
            "reason": "Ingestion looks complete but no matching plaud-ingest-YYYY-MM-DD-HHmmss.md working memory file found",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Write the POST-COMPLETION working memory file with the mandatory timestamped filename via Desktop Commander.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"{len(ingested_notes)} note(s) ingested, staging clean, working memory file {working_memory_file} present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

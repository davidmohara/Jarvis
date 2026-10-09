#!/usr/bin/env python3
"""Ground-truth verifier for dream-cycle/step-01-working-memory-cleanup.

Memory-conservation check. The step claims it archived N files (listed in
`archived_files`) from memory/working/ into memory/episodic/, deleted M trivial
files, and skipped the rest. This verifier re-derives the claim from the real
filesystem instead of trusting the frontmatter self-report:

  * every file listed in `archived_files` must be GONE from memory/working/
    (a listed-but-still-present file is a silent non-archival — the exact
    failure class dream-cycle's "preservation over aggression" rule exists to
    prevent);
  * `working_archived` must equal len(archived_files);
  * memory/working/ must exist.

Verdict: retry on a listed-but-still-in-working file or a count mismatch;
pass otherwise (including a genuinely light day with zero archives).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "dream-cycle" / "steps" / "step-01-working-memory-cleanup.md"


def extract_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm:
            fm_lines.append(line)
    try:
        return yaml.safe_load("\n".join(fm_lines)) or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / STEP_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "step-01-working-memory-cleanup.md not found or YAML parser unavailable",
            "fields": {"archived_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/dream-cycle/steps/step-01-working-memory-cleanup.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "step-01 outputs block is empty — no working-memory counts recorded",
            "fields": {"archived_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-01 and record working_archived/archived_files/skipped counts in the step frontmatter outputs.",
        }))
        return

    working_dir = ies_root / "memory" / "working"
    archived_files = outputs.get("archived_files") or []
    if not isinstance(archived_files, list):
        archived_files = []
    working_archived = outputs.get("working_archived")

    # Re-derive: none of the files claimed archived may still sit in working/.
    still_present = [f for f in archived_files if (working_dir / f).exists()]
    count_mismatch = (
        isinstance(working_archived, int) and working_archived != len(archived_files)
    )

    fields = {
        "working_dir_exists": working_dir.is_dir(),
        "archived_files_claimed": len(archived_files),
        "working_archived_reported": working_archived,
        "archived_still_in_working": still_present,
        "working_deleted": outputs.get("working_deleted"),
        "working_skipped": outputs.get("working_skipped"),
    }

    if not working_dir.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": "memory/working/ does not exist — the step's scope directory is missing",
            "fields": fields,
            "validation_errors": ["working_dir_missing"],
            "retry_instruction": "Confirm the IES root resolves and memory/working/ exists before re-running step-01.",
        }))
        return

    if still_present:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(still_present)} file(s) reported archived are still present in memory/working/ (silent non-archival): {still_present[:5]}",
            "fields": fields,
            "validation_errors": ["archived_file_still_in_working"],
            "retry_instruction": "Re-run the working->episodic mv for the files listed in fields.archived_still_in_working, or correct the archived_files list.",
        }))
        return

    if count_mismatch:
        print(json.dumps({
            "result": "retry",
            "reason": f"working_archived ({working_archived}) does not match len(archived_files) ({len(archived_files)})",
            "fields": fields,
            "validation_errors": ["archived_count_mismatch"],
            "retry_instruction": "Reconcile working_archived with the archived_files list in step-01 outputs.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-01 archive claims reconcile: {len(archived_files)} archived file(s) confirmed absent from memory/working/, counts consistent",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

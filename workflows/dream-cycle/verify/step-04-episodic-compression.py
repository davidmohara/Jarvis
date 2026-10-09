#!/usr/bin/env python3
"""Ground-truth verifier for dream-cycle/step-04-episodic-compression.

Compression-accounting check. The step claims it compressed N entries into
quarterly digests and skipped the rest. This verifier re-derives the claim
from the real filesystem rather than trusting the frontmatter self-report:

  * outputs must be present (candidates_count / entries_compressed /
    digests_updated / compression_skipped);
  * if entries_compressed > 0, memory/episodic/digests/ must exist with at
    least `digests_updated` digest files, and the digests must contain at
    least `entries_compressed` `### ` entry blocks in total (the step's
    ordering rule: never delete a source until its digest entry is written);
  * if compression_skipped is true, entries_compressed must be 0 (a skip that
    still deleted files is a contradiction).

Verdict: retry on any inconsistency; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "dream-cycle" / "steps" / "step-04-episodic-compression.md"


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
            "reason": "step-04-episodic-compression.md not found or YAML parser unavailable",
            "fields": {"compression_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/dream-cycle/steps/step-04-episodic-compression.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "step-04 outputs block is empty - no compression counts recorded",
            "fields": {"compression_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-04 and record entries_compressed/digests_updated/compression_skipped in the step frontmatter outputs.",
        }))
        return

    compressed = outputs.get("entries_compressed")
    digests_updated = outputs.get("digests_updated")
    skipped = outputs.get("compression_skipped")

    digests_dir = ies_root / "memory" / "episodic" / "digests"
    digest_files = list(digests_dir.glob("*-digest.md")) if digests_dir.is_dir() else []
    digest_entry_count = 0
    for d in digest_files:
        try:
            digest_entry_count += d.read_text(encoding="utf-8", errors="replace").count("\n### ")
        except Exception:
            continue

    fields = {
        "candidates_count_reported": outputs.get("candidates_count"),
        "entries_compressed_reported": compressed,
        "digests_updated_reported": digests_updated,
        "compression_skipped_reported": skipped,
        "digest_files_present": len(digest_files),
        "digest_entry_blocks": digest_entry_count,
    }

    if isinstance(compressed, int) and compressed > 0:
        if not digest_files:
            print(json.dumps({
                "result": "retry",
                "reason": f"entries_compressed={compressed} but no digest files exist - sources were deleted with no digest written",
                "fields": fields,
                "validation_errors": ["digest_missing_after_delete"],
                "retry_instruction": "Compression must write the digest entry before deleting the source. Re-run step-04 and restore any deleted-without-digest files from git history.",
            }))
            return
        if isinstance(digests_updated, int) and digests_updated > len(digest_files):
            print(json.dumps({
                "result": "retry",
                "reason": f"digests_updated={digests_updated} exceeds the {len(digest_files)} digest file(s) present",
                "fields": fields,
                "validation_errors": ["digests_updated_mismatch"],
                "retry_instruction": "Reconcile digests_updated with the digest files on disk.",
            }))
            return
        if digest_entry_count < compressed:
            print(json.dumps({
                "result": "retry",
                "reason": f"entries_compressed={compressed} but only {digest_entry_count} digest entry block(s) found - deleted entries are not all accounted for in the digests",
                "fields": fields,
                "validation_errors": ["digest_entries_short"],
                "retry_instruction": "Ensure each compressed source has a matching ### digest entry before deletion.",
            }))
            return

    if skipped is True and isinstance(compressed, int) and compressed > 0:
        print(json.dumps({
            "result": "retry",
            "reason": "compression_skipped is true but entries_compressed > 0 - contradictory outcome",
            "fields": fields,
            "validation_errors": ["skip_but_compressed"],
            "retry_instruction": "Reconcile compression_skipped with entries_compressed in step-04 outputs.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-04 compression claims reconcile: compressed={compressed}, skipped={skipped}, {len(digest_files)} digest file(s) with {digest_entry_count} entry block(s)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

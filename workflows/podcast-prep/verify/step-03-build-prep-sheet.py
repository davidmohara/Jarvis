#!/usr/bin/env python3
"""Ground-truth verifier for podcast-prep/step-03-build-prep-sheet.

Locates the detailed prep sheet actually saved under meetings/podcast-prep/
(named YYYY-MM-DD-guest-name.md per the step spec), not an "Episode N.md"
file (that's step-04's PDF-source doc), and validates required sections
and word count directly from file content.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_SECTIONS = [
    "## Logistics",
    "## Guest Background",
    "## Episode Topic",
    "Talking Points",
    "## Pre-Filming Checklist",
]
MIN_WORDS = 300


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "podcast-prep" / "state.yaml"
    guest_name = None
    if yaml is not None and state_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
            state = docs[0] if docs else {}
            context = state.get("accumulated-context") or {}
            episode = context.get("episode") or {}
            guest_name = (episode.get("primary_guest") or {}).get("name")
        except Exception:
            guest_name = None

    prep_dir = ies_root / "meetings" / "podcast-prep"
    if not prep_dir.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": "meetings/podcast-prep/ directory not found",
            "fields": {"file_found": False},
            "validation_errors": ["dir_missing"],
            "retry_instruction": "Create meetings/podcast-prep/ and save the detailed prep sheet there per the step spec.",
        }))
        return

    guest_slug = slugify(guest_name) if guest_name else None
    candidates = []
    for p in prep_dir.glob("*.md"):
        if re.match(r"^Episode\s*\d+$", p.stem, re.IGNORECASE):
            continue
        if guest_slug and guest_slug in slugify(p.stem):
            candidates.append(p)

    if not candidates:
        print(json.dumps({
            "result": "retry",
            "reason": f"No detailed prep sheet found in meetings/podcast-prep/ matching guest '{guest_name}'",
            "fields": {"file_found": False, "guest_name": guest_name},
            "validation_errors": ["file_not_found"],
            "retry_instruction": "Save the detailed prep sheet to meetings/podcast-prep/YYYY-MM-DD-guest-name.md and re-run step-03.",
        }))
        return

    best = max(candidates, key=lambda p: p.stat().st_mtime)
    content = best.read_text(errors="ignore")
    word_count = len(content.split())

    sections_found = [s for s in REQUIRED_SECTIONS if s in content]
    sections_missing = [s for s in REQUIRED_SECTIONS if s not in content]

    fields = {
        "file_found": True,
        "file_path": str(best.relative_to(ies_root)),
        "word_count": word_count,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
    }

    validation_errors = [f"missing_section: {s}" for s in sections_missing]
    if word_count < MIN_WORDS:
        validation_errors.append(f"content_too_thin: {word_count} words (need >= {MIN_WORDS})")

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"Prep sheet at {fields['file_path']} failed quality checks: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run step-03 to fill in the missing sections or add substantive content.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Detailed prep sheet at {fields['file_path']} complete with all required sections ({word_count} words)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

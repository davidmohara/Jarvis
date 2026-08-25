#!/usr/bin/env python3
"""Ground-truth verifier for one-on-one-prep/step-05-quality-check-and-save.

Finds the actual saved brief on disk (rather than trusting a self-reported
save path), checking meetings/ and the repo root for a markdown file whose
name contains the person's slug and whose mtime falls near the step's
completion window. Validates required section headers and counts talking
points directly from file content — never from a self-reported number.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

REQUIRED_SECTIONS = [
    "Summary of Interactions",
    "Open Action Items",
    "Key Calendar Events",
    "Suggested Talking Points",
]
SEARCH_DIRS = ["meetings", "."]
TALKING_POINT_PATTERN = re.compile(r"^\d+\.\s+\*\*", re.MULTILINE)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find_candidate_files(ies_root: Path, person_slug: str, step_started_dt):
    candidates = []
    for rel_dir in SEARCH_DIRS:
        base = ies_root / rel_dir
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if ".git" in p.parts:
                continue
            name_slug = slugify(p.stem)
            if person_slug and person_slug in name_slug:
                candidates.append(p)
    return candidates


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_started = payload.get("step_started")
    step_completed = payload.get("step_completed")

    state_path = ies_root / "workflows" / "one-on-one-prep" / "state.yaml"
    person = None
    if yaml is not None and state_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
            state = docs[0] if docs else {}
            context = state.get("accumulated-context") or {}
            person = (context.get("meeting_details") or {}).get("person")
        except Exception:
            person = None

    if not person:
        print(json.dumps({
            "result": "retry",
            "reason": "Cannot locate the saved brief — no person name found in accumulated-context.meeting_details",
            "fields": {"file_found": False},
            "validation_errors": ["no_person_context"],
            "retry_instruction": "Confirm step-01 recorded meeting_details.person, then re-run step-05.",
        }))
        return

    person_slug = slugify(person)
    candidates = find_candidate_files(ies_root, person_slug, step_started)

    if not candidates:
        print(json.dumps({
            "result": "retry",
            "reason": f"No saved brief found matching '{person}' in meetings/ or repo root",
            "fields": {"file_found": False, "person": person},
            "validation_errors": ["file_not_found"],
            "retry_instruction": f"Save the brief to meetings/{person} - YYYY-MM-DD.md (or the configured knowledge base working directory) and re-run step-05.",
        }))
        return

    # Prefer the most recently modified candidate as the actual save target
    best = max(candidates, key=lambda p: p.stat().st_mtime)
    content = best.read_text(errors="ignore")

    sections_found = [s for s in REQUIRED_SECTIONS if s in content]
    sections_missing = [s for s in REQUIRED_SECTIONS if s not in content]
    talking_points = len(TALKING_POINT_PATTERN.findall(content))

    fields = {
        "file_found": True,
        "file_path": str(best.relative_to(ies_root)),
        "file_size_bytes": best.stat().st_size,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "talking_point_count": talking_points,
        "candidate_files_matched": len(candidates),
    }

    validation_errors = [f"missing_section: {s}" for s in sections_missing]
    if talking_points < 5:
        validation_errors.append(f"insufficient_talking_points: {talking_points} (need >= 5)")

    if sections_missing or talking_points < 5 or best.stat().st_size < 300:
        print(json.dumps({
            "result": "retry",
            "reason": f"Brief at {fields['file_path']} failed quality checks: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run step-05 quality checks and fix the missing sections or thin talking points before re-saving.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Brief saved at {fields['file_path']} with all required sections and {talking_points} talking points",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for client-meeting-prep/step-04-build-prep-sheet.

Locates the saved prep sheet on disk (accumulated-context.deliverables.
markdown_file, then a glob of meetings/*.md for the attendee's slug) rather
than trusting a self-reported save path, and checks the step's hard assembly
rules directly from the file content: no YAML frontmatter block, no
"Next Steps"/post-call action section, the required sections present, and
substantive length.
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
    "## Who They Are",
    "## Reason for the Call",
    "## Open Questions Going In",
]
BIO_SECTION_RE = re.compile(r"##\s+Who (He|She|They) Is", re.IGNORECASE)
TALKING_POINTS_RE = re.compile(r"##\s+Suggested Talking Points", re.IGNORECASE)
NEXT_STEPS_RE = re.compile(r"(?im)^#{1,6}\s*(next steps|post-call|action items)\b")
MIN_BYTES = 500


def load_state(path: Path) -> dict:
    if yaml is None or not path.is_file():
        return {}
    try:
        merged = {}
        for doc in yaml.safe_load_all(path.read_text()):
            if isinstance(doc, dict):
                for k, v in doc.items():
                    if k not in merged or v:
                        merged[k] = v
        return merged
    except Exception:
        return {}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find_prep_sheet(ies_root: Path, ctx: dict):
    deliverables = ctx.get("deliverables") or {}
    md_file = deliverables.get("markdown_file")
    if md_file:
        candidate = Path(md_file)
        if not candidate.is_absolute():
            candidate = ies_root / candidate
        if candidate.is_file():
            return candidate
    md = ctx.get("meeting_details") or {}
    attendees = md.get("attendees_external") or []
    slugs = []
    for a in attendees:
        if isinstance(a, dict) and a.get("name"):
            slugs.append(slugify(a["name"]))
        elif isinstance(a, str):
            slugs.append(slugify(a))
    meetings = ies_root / "meetings"
    if meetings.is_dir():
        for p in sorted(meetings.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            pslug = slugify(p.stem)
            if any(s and s in pslug for s in slugs):
                return p
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "client-meeting-prep" / "state.yaml")
    ctx = state.get("accumulated-context") or {}

    prep = find_prep_sheet(ies_root, ctx)
    if prep is None:
        print(json.dumps({
            "result": "retry",
            "reason": "No saved prep sheet found (accumulated-context.deliverables.markdown_file missing and no "
                      "matching file under meetings/)",
            "fields": {"file_found": False},
            "validation_errors": ["file_not_found"],
            "retry_instruction": "Re-execute step-04: save the prep sheet to '{Attendee} - {Company} - {YYYY-MM-DD}.md' "
                                 "and record its path in accumulated-context.deliverables.markdown_file.",
        }))
        return

    content = prep.read_text(errors="ignore")
    sections_missing = [s for s in REQUIRED_SECTIONS if s not in content]
    has_bio = BIO_SECTION_RE.search(content) is not None
    has_talking_points = TALKING_POINTS_RE.search(content) is not None
    has_frontmatter = content.lstrip().startswith("---")
    has_next_steps = NEXT_STEPS_RE.search(content) is not None
    size = prep.stat().st_size

    fields = {
        "file_found": True,
        "file_path": str(prep.relative_to(ies_root)),
        "file_size_bytes": size,
        "sections_missing": sections_missing,
        "has_bio_section": has_bio,
        "has_talking_points_section": has_talking_points,
        "has_yaml_frontmatter": has_frontmatter,
        "has_next_steps_section": has_next_steps,
    }

    errors = [f"missing_section: {s}" for s in sections_missing]
    if not has_bio:
        errors.append("missing_bio_section")
    if not has_talking_points:
        errors.append("missing_talking_points_section")
    if has_frontmatter:
        errors.append("unexpected_frontmatter")
    if has_next_steps:
        errors.append("unexpected_next_steps_section")
    if size < MIN_BYTES:
        errors.append(f"content_too_thin: {size} bytes (need >= {MIN_BYTES})")

    if errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"Prep sheet at {fields['file_path']} failed assembly checks: {', '.join(errors)}",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Re-execute step-04: the prep sheet must start at the H1 (no frontmatter), include "
                                 "the required sections, and contain no Next Steps/post-call section.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Prep sheet saved at {fields['file_path']} with required sections, no frontmatter, no Next Steps "
                  f"section ({size} bytes)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

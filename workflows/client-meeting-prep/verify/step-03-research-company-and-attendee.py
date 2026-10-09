#!/usr/bin/env python3
"""Ground-truth verifier for client-meeting-prep/step-03-research-company-and-attendee.

Re-derives the research output from real records: it reads
accumulated-context for company_profile / company_overview / attendee_bio /
company_disambiguation, and, as a fallback, checks the saved prep sheet's
section headers ("## Who They Are", "## Who He/She/They Is") so a run that
recorded the research in the deliverable rather than in structured state
still verifies. Company identity must not be left silently ambiguous: if
company_disambiguation.ambiguous is true, a resolution note (or an explicit
"unresolved" flag, which is a legitimate recorded outcome) must be present.
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


def find_prep_sheet(ies_root: Path, ctx: dict):
    deliverables = ctx.get("deliverables") or {}
    md_file = deliverables.get("markdown_file")
    if md_file:
        candidate = Path(md_file)
        if not candidate.is_absolute():
            candidate = ies_root / candidate
        if candidate.is_file():
            return candidate
    meetings = ies_root / "meetings"
    if meetings.is_dir():
        matches = sorted(meetings.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in matches:
            if "prep" in p.stem.lower() or "\u2014" in p.stem or " - " in p.stem:
                return p
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "client-meeting-prep" / "state.yaml")
    ctx = state.get("accumulated-context") or {}

    company_profile = ctx.get("company_profile") or {}
    company_overview = ctx.get("company_overview") or {}
    attendee_bio = ctx.get("attendee_bio") or {}
    disambiguation = ctx.get("company_disambiguation") or {}

    prep = find_prep_sheet(ies_root, ctx)
    prep_content = prep.read_text(errors="ignore") if prep else ""
    has_company_section = "## Who They Are" in prep_content
    has_bio_section = re.search(r"##\s+Who (He|She|They) Is", prep_content) is not None

    ambiguous = bool(disambiguation.get("ambiguous"))
    resolution = disambiguation.get("resolution_method")
    resolution_ok = (not ambiguous) or bool(disambiguation.get("note")) or resolution == "unresolved"

    fields = {
        "company_profile_present": bool(company_profile),
        "company_overview_present": bool(company_overview),
        "attendee_bio_present": bool(attendee_bio),
        "disambiguation_ambiguous": ambiguous,
        "disambiguation_resolution_method": resolution,
        "prep_sheet": str(prep.relative_to(ies_root)) if prep else None,
        "prep_sheet_has_company_section": has_company_section,
        "prep_sheet_has_bio_section": has_bio_section,
    }

    structured = bool(company_profile or company_overview or attendee_bio)
    in_deliverable = has_company_section and has_bio_section

    if not structured and not in_deliverable:
        print(json.dumps({
            "result": "retry",
            "reason": "No company/attendee research found in accumulated-context (company_profile/company_overview/"
                      "attendee_bio) and the saved prep sheet has no company/bio sections",
            "fields": fields,
            "validation_errors": ["missing_research"],
            "retry_instruction": "Re-execute step-03: disambiguate the company, then record company_profile, "
                                 "company_overview, and attendee_bio in accumulated-context.",
        }))
        return

    if not resolution_ok:
        print(json.dumps({
            "result": "retry",
            "reason": "company_disambiguation.ambiguous is true but no resolution note was recorded: an "
                      "unresolved ambiguity must be flagged explicitly, not left silent",
            "fields": fields,
            "validation_errors": ["ambiguous_company_unresolved_silently"],
            "retry_instruction": "Re-execute step-03 and record company_disambiguation.note (or set "
                                 "resolution_method: unresolved) so the ambiguity surfaces in the prep sheet's Open Questions.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": "Company and attendee research recorded"
        + (" (structured in accumulated-context)" if structured else " (captured in the prep sheet sections)")
        + (" with a disambiguation note" if ambiguous else ""),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

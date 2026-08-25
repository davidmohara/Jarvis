#!/usr/bin/env python3
"""Ground-truth verifier for partner-meeting-prep/step-04-build-document.

Locates the actual saved prep document on disk rather than trusting a
self-reported save path. Checks accumulated-context for an explicit
output_file first, then falls back to searching common knowledge-base
locations (outputs/, meetings/, accounts/<partner>/, repo root) for a file
matching the partner's slug. Validates required sections and counts
intentional partner-fill blanks directly from content. A documented
"presented inline because knowledge base save failed" fallback (noted in
accumulated-context) is accepted per the step's failure modes — a claimed
save with no file anywhere and no inline-fallback note is not.
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
    "## Meeting Details",
    "## Priority Accounts",
    "## Discussion Topics",
]
SEARCH_DIRS = ["outputs", "meetings", "accounts", "."]
BLANK_MARKER = "TBD - partner to fill"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find_candidates(ies_root: Path, partner_slug: str):
    candidates = []
    for rel_dir in SEARCH_DIRS:
        base = ies_root / rel_dir
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            if ".git" in p.parts:
                continue
            if partner_slug in slugify(p.stem):
                candidates.append(p)
    return candidates


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "partner-meeting-prep" / "state.yaml"
    partner = None
    context = {}
    if yaml is not None and state_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
            state = docs[0] if docs else {}
            context = state.get("accumulated-context") or {}
            partner = (context.get("partner_details") or {}).get("company") or context.get("partner")
        except Exception:
            partner = None

    if not partner:
        print(json.dumps({
            "result": "retry",
            "reason": "Cannot locate the saved prep document — no partner company found in accumulated-context",
            "fields": {"file_found": False},
            "validation_errors": ["no_partner_context"],
            "retry_instruction": "Confirm step-01 recorded partner_details.company, then re-run step-04.",
        }))
        return

    partner_slug = slugify(partner)

    target = None
    reported_path = context.get("output_file")
    if reported_path:
        candidate = ies_root / reported_path
        if candidate.is_file():
            target = candidate

    candidates = find_candidates(ies_root, partner_slug)
    if target is None and candidates:
        target = max(candidates, key=lambda p: p.stat().st_mtime)

    if target is None:
        inline_note = str(context.get("delivery_note") or context.get("inline_fallback") or "")
        if "inline" in inline_note.lower():
            print(json.dumps({
                "result": "pass",
                "reason": "No saved file found, but an inline-delivery fallback is documented (knowledge base save failure) per the step's failure modes",
                "fields": {"file_found": False, "inline_fallback_documented": True, "partner": partner},
                "validation_errors": [],
            }))
            return
        print(json.dumps({
            "result": "retry",
            "reason": f"No saved prep document found for '{partner}' in outputs/, meetings/, accounts/, or repo root"
            + (f" (reported path {reported_path} does not exist)" if reported_path else ""),
            "fields": {"file_found": False, "partner": partner, "reported_path": reported_path},
            "validation_errors": ["file_not_found"],
            "retry_instruction": f"Save the document to the knowledge base at 'working directory/{partner} - YYYY-MM-DD.md' (or document an inline-delivery fallback) and re-run step-04.",
        }))
        return

    content = target.read_text(errors="ignore")
    sections_found = [s for s in REQUIRED_SECTIONS if s in content]
    sections_missing = [s for s in REQUIRED_SECTIONS if s not in content]
    blanks_count = content.count(BLANK_MARKER)

    fields = {
        "file_found": True,
        "file_path": str(target.relative_to(ies_root)),
        "file_size_bytes": target.stat().st_size,
        "sections_found": sections_found,
        "sections_missing": sections_missing,
        "intentional_blanks_count": blanks_count,
        "candidate_files_matched": len(candidates),
    }

    validation_errors = [f"missing_section: {s}" for s in sections_missing]
    if target.stat().st_size < 300:
        validation_errors.append("content_too_thin")

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"Document at {fields['file_path']} failed quality checks: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run step-04 to fill in missing sections before re-saving.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Partner prep document saved at {fields['file_path']} with all required sections ({blanks_count} intentional partner-fill blank(s))",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for client-meeting-prep/step-05-remarkable-delivery.

Checks the two real outputs of this step: the generated PDF (valid %PDF-
header + minimum size, located from accumulated-context.deliverables.pdf_file
or a glob of meetings/*.pdf) and the recorded reMarkable upload result. A
recorded failure is a legitimate outcome (the step's failure modes require it
to be surfaced, not hidden); a missing upload status is not.
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

MIN_PDF_BYTES = 5000


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


def find_pdf(ies_root: Path, ctx: dict):
    deliverables = ctx.get("deliverables") or {}
    pdf_file = deliverables.get("pdf_file")
    if pdf_file:
        candidate = Path(pdf_file)
        if not candidate.is_absolute():
            candidate = ies_root / candidate
        if candidate.is_file():
            return candidate
    md = ctx.get("meeting_details") or {}
    attendees = md.get("attendees_external") or []
    slugs = [slugify(a["name"]) for a in attendees if isinstance(a, dict) and a.get("name")]
    slugs += [slugify(a) for a in attendees if isinstance(a, str)]
    meetings = ies_root / "meetings"
    if meetings.is_dir():
        for p in sorted(meetings.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True):
            pslug = slugify(p.stem)
            if any(s and s in pslug for s in slugs):
                return p
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "client-meeting-prep" / "state.yaml")
    ctx = state.get("accumulated-context") or {}
    deliverables = ctx.get("deliverables") or {}
    upload = deliverables.get("remarkable_upload")

    pdf = find_pdf(ies_root, ctx)

    fields = {
        "pdf_found": pdf is not None,
        "pdf_path": str(pdf.relative_to(ies_root)) if pdf else None,
        "remarkable_display_name": deliverables.get("remarkable_display_name"),
        "remarkable_destination": deliverables.get("remarkable_destination"),
        "remarkable_upload": upload,
    }

    errors = []
    if pdf is None:
        errors.append("pdf_not_found")
    else:
        size = pdf.stat().st_size
        header = pdf.read_bytes()[:5]
        fields["pdf_size_bytes"] = size
        fields["valid_pdf_header"] = header == b"%PDF-"
        if header != b"%PDF-":
            errors.append("invalid_pdf_header")
        if size < MIN_PDF_BYTES:
            errors.append(f"pdf_too_small: {size} bytes (need >= {MIN_PDF_BYTES})")

    if not upload:
        errors.append("remarkable_upload_status_missing")

    if errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"Delivery step incomplete: {', '.join(errors)}",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Re-execute step-05: render the PDF from step-04's markdown, then record the "
                                 "reMarkable upload result (success or an explicitly flagged failure) in "
                                 "accumulated-context.deliverables.remarkable_upload.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"PDF delivered: {fields['pdf_path']} ({fields['pdf_size_bytes']} bytes); reMarkable upload "
                  f"recorded as '{upload}'",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for podcast-prep/step-05-generate-pdf.

Checks that meetings/podcast-prep/Episode {N}.pdf actually exists and is a
real, non-trivial single-file PDF (magic bytes + minimum size), since the
step's own success criteria require it to pass a 15-point visual checklist
before being presented — a missing or tiny file means that never happened.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

MIN_PDF_BYTES = 5000


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "podcast-prep" / "state.yaml"
    episode_number = None
    if yaml is not None and state_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
            state = docs[0] if docs else {}
            episode_number = ((state.get("accumulated-context") or {}).get("episode") or {}).get("number")
        except Exception:
            episode_number = None

    prep_dir = ies_root / "meetings" / "podcast-prep"
    target = None
    if episode_number is not None:
        candidate = prep_dir / f"Episode {episode_number}.pdf"
        if candidate.is_file():
            target = candidate

    if target is None and prep_dir.is_dir():
        matches = sorted(prep_dir.glob("Episode *.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        target = matches[0] if matches else None

    if target is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"No 'Episode {episode_number}.pdf' found in meetings/podcast-prep/",
            "fields": {"pdf_found": False, "episode_number": episode_number},
            "validation_errors": ["pdf_not_found"],
            "retry_instruction": f"Generate the PDF via weasyprint, verify it visually, and save it to meetings/podcast-prep/Episode {episode_number}.pdf.",
        }))
        return

    size = target.stat().st_size
    header = target.read_bytes()[:5]
    is_pdf = header == b"%PDF-"

    fields = {
        "pdf_found": True,
        "file_path": str(target.relative_to(ies_root)),
        "file_size_bytes": size,
        "valid_pdf_header": is_pdf,
    }

    validation_errors = []
    if not is_pdf:
        validation_errors.append("invalid_pdf_header")
    if size < MIN_PDF_BYTES:
        validation_errors.append(f"pdf_too_small: {size} bytes (need >= {MIN_PDF_BYTES})")

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"{fields['file_path']} exists but failed validity checks: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-render the PDF with weasyprint — the current file is missing, corrupted, or truncated.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Valid PDF at {fields['file_path']} ({size} bytes)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

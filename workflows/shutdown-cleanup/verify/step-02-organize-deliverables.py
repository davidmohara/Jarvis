#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-02-organize-deliverables.

Re-derives the build-artifact rule (a PDF with a corresponding markdown
source anywhere in the repo should have been deleted) by scanning the
real working tree, rather than trusting the model's organize_results
self-report. Slug-normalized filename matching is a proxy for the
content-matching rule in step-02.md — it can only catch matches where the
PDF and markdown share a recognizable stem, so this check is best-effort
and only blocks on positive matches, never on absence of a match.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def normalize(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", stem.lower())


def git_changed_files(ies_root: Path) -> list:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ies_root, capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return []
    files = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ")[-1]
        files.append(path)
    return files


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    if not ies_root.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": f"ies_root does not exist: {ies_root}",
            "fields": {},
            "validation_errors": ["ies_root_missing"],
        }))
        return

    changed = git_changed_files(ies_root)
    changed_pdfs = [f for f in changed if f.lower().endswith(".pdf")]

    all_md_stems = {}
    for p in ies_root.rglob("*.md"):
        if ".git" in p.parts:
            continue
        all_md_stems.setdefault(normalize(p.stem), []).append(str(p.relative_to(ies_root)))

    violations = []
    for pdf_rel in changed_pdfs:
        pdf_path = ies_root / pdf_rel
        stem_norm = normalize(pdf_path.stem)
        matches = all_md_stems.get(stem_norm, [])
        if matches:
            violations.append({"pdf": pdf_rel, "matching_markdown": matches})

    changed_deliverables = [
        f for f in changed
        if f.lower().endswith((".pdf", ".docx", ".pptx", ".epub"))
    ]

    fields = {
        "deliverables_changed": len(changed_deliverables),
        "pdfs_changed": len(changed_pdfs),
        "build_artifact_violations": violations,
    }

    if violations:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(violations)} PDF(s) with a filename-matching markdown source should have been deleted as build artifacts",
            "fields": fields,
            "validation_errors": [f"build_artifact_not_deleted: {v['pdf']}" for v in violations],
            "retry_instruction": "Delete the PDFs listed in build_artifact_violations — each has a corresponding markdown source and is a build artifact, not a deliverable.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"No build-artifact violations found among {len(changed_deliverables)} changed deliverable(s)" if changed_deliverables else "No deliverable files changed this session — nothing to organize",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

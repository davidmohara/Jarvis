#!/usr/bin/env python3
"""Ground-truth verifier for podcast-prep/step-04-build-pdf-sheet.

Checks that meetings/podcast-prep/Episode {N}.md exists and follows the
required condensation rules: exactly 5 numbered prompting questions plus
a wrap-up (6 total), and the mandatory HTML structural elements the CSS
stylesheet depends on. Counts are computed from the file, not self-reported.
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

REQUIRED_HTML_MARKERS = [
    'class="banner"',
    '<h4>INTRO SCRIPT</h4>',
    'class="remember"',
]
QUESTION_PATTERN = re.compile(r"^\*\*\d+\.\s", re.MULTILINE)


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
        candidate = prep_dir / f"Episode {episode_number}.md"
        if candidate.is_file():
            target = candidate

    if target is None and prep_dir.is_dir():
        matches = sorted(prep_dir.glob("Episode *.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        target = matches[0] if matches else None

    if target is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"No 'Episode {episode_number}.md' file found in meetings/podcast-prep/",
            "fields": {"file_found": False, "episode_number": episode_number},
            "validation_errors": ["file_not_found"],
            "retry_instruction": f"Save the PDF-format markdown to meetings/podcast-prep/Episode {episode_number}.md and re-run step-04.",
        }))
        return

    content = target.read_text(errors="ignore")
    question_count = len(QUESTION_PATTERN.findall(content))
    markers_found = [m for m in REQUIRED_HTML_MARKERS if m in content]
    markers_missing = [m for m in REQUIRED_HTML_MARKERS if m not in content]

    fields = {
        "file_found": True,
        "file_path": str(target.relative_to(ies_root)),
        "question_count": question_count,
        "markers_found": markers_found,
        "markers_missing": markers_missing,
    }

    validation_errors = [f"missing_marker: {m}" for m in markers_missing]
    if question_count != 6:
        validation_errors.append(f"unexpected_question_count: {question_count} (need exactly 6 — 5 prompts + wrap-up)")

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"{fields['file_path']} failed structural checks: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run step-04 — condense to exactly 5 questions + wrap-up, and use the exact required HTML markers per the template.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"{fields['file_path']} valid: {question_count} questions, all required HTML markers present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

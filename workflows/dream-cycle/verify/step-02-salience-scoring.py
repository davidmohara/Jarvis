#!/usr/bin/env python3
"""Ground-truth verifier for dream-cycle/step-02-salience-scoring.

The step claims it scanned and re-scored every episodic entry
(`episodic_scanned`, `score_updates`). This verifier re-derives the claim from
the real filesystem rather than trusting the frontmatter self-report:

  * memory/episodic/ must exist and contain at least one .md file;
  * `episodic_scanned` and `score_updates` must be positive ints and equal
    (salience-score.py writes a score for every file it scans);
  * the step's write must be observable: at least one episodic file must carry
    a `salience:` frontmatter block.

Verdict: retry if the directory is empty/missing, the counts are absent or
inconsistent, or no scored entry is observable; pass otherwise. Exact equality
against the historical file count is deliberately NOT required (files age into
digests after the run), so this does not produce false retries.
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

STEP_REL = Path("workflows") / "dream-cycle" / "steps" / "step-02-salience-scoring.md"


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
            "reason": "step-02-salience-scoring.md not found or YAML parser unavailable",
            "fields": {"scoring_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/dream-cycle/steps/step-02-salience-scoring.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "step-02 outputs block is empty - no scoring counts recorded",
            "fields": {"scoring_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-02 (salience-score.py) and record episodic_scanned/score_updates in the step frontmatter outputs.",
        }))
        return

    episodic_dir = ies_root / "memory" / "episodic"
    episodic_files = []
    if episodic_dir.is_dir():
        episodic_files = [
            p for p in episodic_dir.glob("*.md")
            if p.is_file() and p.name != "README.md"
        ]

    scanned = outputs.get("episodic_scanned")
    updates = outputs.get("score_updates")

    scored_observable = False
    for p in episodic_files[:50]:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if re.search(r"^salience:", text, re.MULTILINE):
            scored_observable = True
            break

    fields = {
        "episodic_dir_exists": episodic_dir.is_dir(),
        "episodic_files_present": len(episodic_files),
        "episodic_scanned_reported": scanned,
        "score_updates_reported": updates,
        "scored_entry_observable": scored_observable,
    }

    if not episodic_dir.is_dir() or not episodic_files:
        print(json.dumps({
            "result": "retry",
            "reason": "memory/episodic/ is missing or contains no entries - nothing could have been scored",
            "fields": fields,
            "validation_errors": ["episodic_dir_empty"],
            "retry_instruction": "Confirm memory/episodic/ exists and is populated before re-running step-02.",
        }))
        return

    if not isinstance(scanned, int) or not isinstance(updates, int) or scanned <= 0:
        print(json.dumps({
            "result": "retry",
            "reason": "episodic_scanned/score_updates are absent or not positive integers",
            "fields": fields,
            "validation_errors": ["invalid_counts"],
            "retry_instruction": "Record positive integer episodic_scanned and score_updates in step-02 outputs.",
        }))
        return

    if scanned != updates:
        print(json.dumps({
            "result": "retry",
            "reason": f"score_updates ({updates}) != episodic_scanned ({scanned}) - every scanned file must receive a score",
            "fields": fields,
            "validation_errors": ["scanned_updates_mismatch"],
            "retry_instruction": "salience-score.py must write a score for every scanned file; re-run step-02 and reconcile the counts.",
        }))
        return

    if not scored_observable:
        print(json.dumps({
            "result": "retry",
            "reason": "no episodic entry carries a salience: frontmatter block - the scoring write is not observable",
            "fields": fields,
            "validation_errors": ["no_scored_entry"],
            "retry_instruction": "Re-run step-02; confirm salience blocks are written to the episodic files.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-02 scoring reconciled: {scanned} files scored, salience blocks observable on disk",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

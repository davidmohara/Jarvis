#!/usr/bin/env python3
"""Ground-truth verifier for weekly-review/step-08-eval-summary.

Confirms the workflow actually closed: workflows/weekly-review/state.yaml
shows status: complete, the weekly review file has an Eval Health section
(or a documented "not installed"/"no data" note per the step's Failure
Modes table), and a working memory file was written — all read from real
files on disk, not from a self-reported closing summary.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

EVAL_SECTION = re.compile(r'##\s+Eval Health', re.IGNORECASE)


def iso_week_candidates(payload: dict) -> list:
    candidates = []
    for key in ("step_completed", "step_started"):
        raw = payload.get(key)
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            year, week, _ = dt.isocalendar()
            candidates.append(f"{year}-W{week:02d}")
        except Exception:
            continue
    return sorted(set(candidates))


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "weekly-review" / "state.yaml"
    weekly_dir = ies_root / "reviews" / "weekly"
    working_dir = ies_root / "memory" / "working"

    state_status = None
    if yaml is not None and state_path.is_file():
        try:
            docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
            state = docs[0] if docs else {}
            state_status = state.get("status")
        except Exception:
            state_status = None

    candidates = iso_week_candidates(payload)
    review_path = None
    review_content = ""
    for wk in candidates:
        p = weekly_dir / f"{wk}.md"
        if p.is_file():
            review_path = p
            review_content = p.read_text()
            break

    working_files = []
    if working_dir.is_dir():
        working_files = [f.name for f in working_dir.glob("weekly-review-*.md")]

    fields = {
        "state_status": state_status,
        "review_path": str(review_path.relative_to(ies_root)) if review_path else None,
        "eval_health_section_found": bool(EVAL_SECTION.search(review_content)),
        "working_memory_files_found": working_files,
        "working_memory_found_count": len(working_files),
    }

    if state_status != "complete":
        verdict = {
            "result": "retry",
            "reason": f"workflows/weekly-review/state.yaml status is '{state_status}', expected 'complete'",
            "fields": fields,
            "validation_errors": ["state_not_complete"],
            "retry_instruction": "Write status: complete to workflows/weekly-review/state.yaml after closing the review.",
        }
    elif review_path is None:
        verdict = {
            "result": "retry",
            "reason": "state.yaml reports complete but no reviews/weekly/YYYY-Wxx.md file exists for this week",
            "fields": fields,
            "validation_errors": ["review_file_missing"],
            "retry_instruction": "Confirm the weekly review file from step-06 exists before marking the workflow complete.",
        }
    elif not fields["eval_health_section_found"]:
        verdict = {
            "result": "retry",
            "reason": "Weekly review file exists but has no '## Eval Health' section",
            "fields": fields,
            "validation_errors": ["eval_health_section_missing"],
            "retry_instruction": "Append a '## Eval Health' section to the weekly review file, even if it just notes 'Eval harness not installed' or 'No eval data this week'.",
        }
    elif not working_files:
        verdict = {
            "result": "pass",
            "reason": "Workflow closed and Eval Health section present, but no weekly-review working memory file found — non-blocking",
            "fields": fields,
            "validation_errors": ["working_memory_missing"],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Weekly review closed, Eval Health section present, working memory recorded ({len(working_files)} file(s))",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

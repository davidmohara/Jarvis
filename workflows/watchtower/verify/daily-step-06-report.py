#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-06-report.

Terminal-report check. The step claims `total_gathered` items were collected,
`total_surfaced` surfaced, and `content_queue_additions` added. This verifier
re-derives the claim from the upstream step outputs rather than trusting the
frontmatter self-report:

  * total_gathered must equal step-02's `kept_count`;
  * total_surfaced must equal step-03's `awareness_items`;
  * content_queue_additions must equal step-03's `content_worthy_items`;
  * obsidian_note_path must be recorded.

Verdict: retry on any mismatch; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-06-report.md"
DEDUPE_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-02-dedupe.md"
SCORE_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-03-score.md"


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
            "reason": "daily-step-06-report.md not found or YAML parser unavailable",
            "fields": {"report_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-06-report.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-06 outputs block is empty - no report counts recorded",
            "fields": {"report_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-06 and record total_gathered/total_surfaced/content_queue_additions/obsidian_note_path in the step frontmatter outputs.",
        }))
        return

    def upstream_outputs(rel):
        p = ies_root / rel
        if p.is_file():
            o = extract_frontmatter(p.read_text()).get("outputs") or {}
            return o if isinstance(o, dict) else {}
        return {}

    d = upstream_outputs(DEDUPE_REL)
    s = upstream_outputs(SCORE_REL)

    gathered = outputs.get("total_gathered")
    surfaced = outputs.get("total_surfaced")
    queue_adds = outputs.get("content_queue_additions")

    fields = {
        "total_gathered_reported": gathered,
        "total_surfaced_reported": surfaced,
        "content_queue_additions_reported": queue_adds,
        "upstream_kept_count": d.get("kept_count"),
        "upstream_awareness_items": s.get("awareness_items"),
        "upstream_content_worthy": s.get("content_worthy_items"),
        "obsidian_note_path": outputs.get("obsidian_note_path"),
    }

    mismatches = []
    if isinstance(gathered, int) and isinstance(d.get("kept_count"), int) and gathered != d["kept_count"]:
        mismatches.append(f"total_gathered ({gathered}) != step-02 kept_count ({d['kept_count']})")
    if isinstance(surfaced, int) and isinstance(s.get("awareness_items"), int) and surfaced != s["awareness_items"]:
        mismatches.append(f"total_surfaced ({surfaced}) != step-03 awareness_items ({s['awareness_items']})")
    if isinstance(queue_adds, int) and isinstance(s.get("content_worthy_items"), int) and queue_adds != s["content_worthy_items"]:
        mismatches.append(f"content_queue_additions ({queue_adds}) != step-03 content_worthy_items ({s['content_worthy_items']})")

    if mismatches:
        print(json.dumps({
            "result": "retry",
            "reason": "step-06 report counts do not reconcile with upstream steps: " + "; ".join(mismatches),
            "fields": fields,
            "validation_errors": ["report_counts_mismatch"],
            "retry_instruction": "Recompute the terminal report counts from the step-02/03 outputs.",
        }))
        return

    if not (isinstance(outputs.get("obsidian_note_path"), str) and outputs.get("obsidian_note_path").strip()):
        print(json.dumps({
            "result": "retry",
            "reason": "obsidian_note_path is missing from step-06 outputs",
            "fields": fields,
            "validation_errors": ["note_path_missing"],
            "retry_instruction": "Record the Obsidian daily-note path in step-06 outputs.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-06 report reconciled: {gathered} gathered, {surfaced} surfaced, {queue_adds} queued",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

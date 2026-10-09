#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-03-score.

Scoring check. The step claims `deduped_count` items entered, `dropped_below_floor`
were dropped, `awareness_items` survived, and `content_worthy_items` were
flagged. This verifier re-derives the claim from the arithmetic and the
activity ledger rather than trusting the frontmatter self-report:

  * deduped_count must equal dropped_below_floor + awareness_items;
  * content_worthy_items must be <= awareness_items;
  * workflows/watchtower/source-activity.json must exist (the step updates it).

Verdict: retry on a non-conserving count, an impossible flag count, or a
missing ledger; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-03-score.md"
LEDGER_REL = Path("workflows") / "watchtower" / "source-activity.json"


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
    ledger_path = ies_root / LEDGER_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-03-score.md not found or YAML parser unavailable",
            "fields": {"scoring_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-03-score.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-03 outputs block is empty - no scoring counts recorded",
            "fields": {"scoring_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-03 and record deduped_count/dropped_below_floor/awareness_items/content_worthy_items in the step frontmatter outputs.",
        }))
        return

    deduped = outputs.get("deduped_count")
    dropped = outputs.get("dropped_below_floor")
    awareness = outputs.get("awareness_items")
    worthy = outputs.get("content_worthy_items")

    fields = {
        "source_activity_ledger_exists": ledger_path.is_file(),
        "deduped_count": deduped,
        "dropped_below_floor": dropped,
        "awareness_items": awareness,
        "content_worthy_items": worthy,
    }

    if not all(isinstance(v, int) for v in (deduped, dropped, awareness, worthy)):
        print(json.dumps({
            "result": "retry",
            "reason": "one or more scoring counts are missing or not integers",
            "fields": fields,
            "validation_errors": ["invalid_counts"],
            "retry_instruction": "Record integer deduped_count/dropped_below_floor/awareness_items/content_worthy_items in step-03 outputs.",
        }))
        return

    if deduped != dropped + awareness:
        print(json.dumps({
            "result": "retry",
            "reason": f"deduped_count ({deduped}) != dropped_below_floor ({dropped}) + awareness_items ({awareness}) - items are unaccounted for",
            "fields": fields,
            "validation_errors": ["counts_not_conserved"],
            "retry_instruction": "Reconcile the scoring counts: every deduped item is either dropped or kept.",
        }))
        return

    if worthy > awareness:
        print(json.dumps({
            "result": "retry",
            "reason": f"content_worthy_items ({worthy}) exceeds awareness_items ({awareness})",
            "fields": fields,
            "validation_errors": ["worthy_exceeds_awareness"],
            "retry_instruction": "content_worthy is a subset of awareness items; reconcile the counts.",
        }))
        return

    if not ledger_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/source-activity.json not found - the step's dormancy ledger was not updated",
            "fields": fields,
            "validation_errors": ["ledger_missing"],
            "retry_instruction": "Re-execute step-03; it must update source-activity.json for every kept item's source.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-03 scoring reconciled: {deduped} deduped = {dropped} dropped + {awareness} awareness ({worthy} content-worthy); ledger present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

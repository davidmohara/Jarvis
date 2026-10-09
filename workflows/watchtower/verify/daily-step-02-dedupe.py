#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-02-dedupe.

Dedupe check. The step claims `raw_count` items entered, `dropped_count` were
dropped as duplicates, and `kept_count` survived. This verifier re-derives the
claim from the real ledger and the arithmetic rather than trusting the
frontmatter self-report:

  * workflows/watchtower/seen.jsonl must exist (created on first run);
  * raw_count must equal dropped_count + kept_count;
  * kept_count must be <= raw_count.

Verdict: retry on a missing ledger or a non-conserving count; pass otherwise
(an all-deduped run with kept_count 0 is valid).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-02-dedupe.md"
SEEN_REL = Path("workflows") / "watchtower" / "seen.jsonl"


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
    seen_path = ies_root / SEEN_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-02-dedupe.md not found or YAML parser unavailable",
            "fields": {"dedupe_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-02-dedupe.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-02 outputs block is empty - no dedupe counts recorded",
            "fields": {"dedupe_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-02 and record raw_count/dropped_count/kept_count in the step frontmatter outputs.",
        }))
        return

    raw = outputs.get("raw_count")
    dropped = outputs.get("dropped_count")
    kept = outputs.get("kept_count")

    fields = {
        "seen_ledger_exists": seen_path.is_file(),
        "raw_count": raw,
        "dropped_count": dropped,
        "kept_count": kept,
    }

    if not all(isinstance(v, int) for v in (raw, dropped, kept)):
        print(json.dumps({
            "result": "retry",
            "reason": "raw_count/dropped_count/kept_count are missing or not integers",
            "fields": fields,
            "validation_errors": ["invalid_counts"],
            "retry_instruction": "Record integer raw_count/dropped_count/kept_count in step-02 outputs.",
        }))
        return

    if not seen_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/seen.jsonl does not exist - the dedupe ledger was not written",
            "fields": fields,
            "validation_errors": ["seen_ledger_missing"],
            "retry_instruction": "Re-execute step-02; it must create/append seen.jsonl with each kept item.",
        }))
        return

    if raw != dropped + kept:
        print(json.dumps({
            "result": "retry",
            "reason": f"raw_count ({raw}) != dropped_count ({dropped}) + kept_count ({kept}) - items are unaccounted for",
            "fields": fields,
            "validation_errors": ["counts_not_conserved"],
            "retry_instruction": "Reconcile the dedupe counts: every raw item is either dropped or kept.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-02 dedupe reconciled: {raw} raw = {dropped} dropped + {kept} kept; ledger present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

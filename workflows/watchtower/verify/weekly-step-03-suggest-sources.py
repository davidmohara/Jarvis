#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-03-suggest-sources.

Source-proposal check. The step claims it appended `proposed_count` proposals
(batch `batch_number`). This verifier re-derives the claim from the real
config and proposal file rather than trusting the frontmatter self-report:

  * workflows/watchtower/proposed-sources.md must exist;
  * when `source_suggestions.enabled` is true, `proposed_count` must not
    exceed `source_suggestions.max_per_week`;
  * `batch_number` must be a positive integer.

Verdict: retry on a missing proposal file or a cap violation; pass otherwise
(including the kill-switch path where the step is skipped with 0 proposals).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-03-suggest-sources.md"
PROPOSED_REL = Path("workflows") / "watchtower" / "proposed-sources.md"
CONFIG_REL = Path("workflows") / "watchtower" / "config.yaml"


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
    proposed_path = ies_root / PROPOSED_REL
    config_path = ies_root / CONFIG_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-03-suggest-sources.md not found or YAML parser unavailable",
            "fields": {"sources_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-03-suggest-sources.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-03 outputs block is empty - no proposal counts recorded",
            "fields": {"sources_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-03 and record proposed_count/excluded_count/batch_number in the step frontmatter outputs.",
        }))
        return

    enabled = None
    max_per_week = None
    if config_path.is_file():
        try:
            cfg = yaml.safe_load(config_path.read_text()) or {}
            ss = cfg.get("source_suggestions") if isinstance(cfg, dict) else None
            if isinstance(ss, dict):
                enabled = ss.get("enabled")
                max_per_week = ss.get("max_per_week")
        except Exception:
            pass

    proposed = outputs.get("proposed_count")
    batch_number = outputs.get("batch_number")

    fields = {
        "proposed_count_reported": proposed,
        "batch_number_reported": batch_number,
        "proposed_sources_file_exists": proposed_path.is_file(),
        "source_suggestions_enabled": enabled,
        "max_per_week": max_per_week,
    }

    if not proposed_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/proposed-sources.md not found - proposals had nowhere to be appended",
            "fields": fields,
            "validation_errors": ["proposed_file_missing"],
            "retry_instruction": "Restore proposed-sources.md before re-running step-03.",
        }))
        return

    if not isinstance(proposed, int) or proposed < 0:
        print(json.dumps({
            "result": "retry",
            "reason": "proposed_count is missing or not a non-negative integer",
            "fields": fields,
            "validation_errors": ["invalid_proposed_count"],
            "retry_instruction": "Record a non-negative integer proposed_count in step-03 outputs.",
        }))
        return

    if enabled is True and isinstance(max_per_week, int) and proposed > max_per_week:
        print(json.dumps({
            "result": "retry",
            "reason": f"proposed_count ({proposed}) exceeds source_suggestions.max_per_week ({max_per_week})",
            "fields": fields,
            "validation_errors": ["proposal_cap_exceeded"],
            "retry_instruction": "Limit proposals to max_per_week and reconcile proposed_count.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-03 proposals verified: {proposed} proposal(s), batch {batch_number}, within cap",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

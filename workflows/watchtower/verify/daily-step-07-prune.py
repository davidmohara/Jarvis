#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-07-prune.

Dormancy-prune check. The step claims it evaluated `sources_evaluated`
sources, retired `sources_retired`, and updated the activity ledger. This
verifier re-derives the claim from the real registries rather than trusting
the frontmatter self-report:

  * workflows/watchtower/source-activity.json must exist (the ledger was
    updated);
  * `retired_names` must be a list whose length equals `sources_retired`;
  * if sources were retired, each retired name must appear in
    dormant-sources.yaml (never deleted, only moved).

Verdict: retry on a missing ledger or an unaccounted retirement; pass
otherwise (zero retirements is a valid outcome).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-07-prune.md"
LEDGER_REL = Path("workflows") / "watchtower" / "source-activity.json"
DORMANT_REL = Path("workflows") / "watchtower" / "dormant-sources.yaml"


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
    dormant_path = ies_root / DORMANT_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-07-prune.md not found or YAML parser unavailable",
            "fields": {"prune_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-07-prune.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-07 outputs block is empty - no prune results recorded",
            "fields": {"prune_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-07 and record sources_evaluated/sources_retired/retired_names/ledger_updated in the step frontmatter outputs.",
        }))
        return

    retired = outputs.get("sources_retired")
    retired_names = outputs.get("retired_names")

    dormant_text = dormant_path.read_text(encoding="utf-8", errors="replace") if dormant_path.is_file() else ""
    missing_from_dormant = []
    if isinstance(retired_names, list):
        for name in retired_names:
            if isinstance(name, str) and name and name not in dormant_text:
                missing_from_dormant.append(name)

    fields = {
        "ledger_exists": ledger_path.is_file(),
        "sources_evaluated_reported": outputs.get("sources_evaluated"),
        "sources_retired_reported": retired,
        "retired_names_reported": retired_names if isinstance(retired_names, list) else None,
        "dormant_registry_exists": dormant_path.is_file(),
        "retired_missing_from_dormant": missing_from_dormant,
    }

    if not ledger_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/source-activity.json not found - the ledger was not updated",
            "fields": fields,
            "validation_errors": ["ledger_missing"],
            "retry_instruction": "Re-execute step-07; it must update source-activity.json.",
        }))
        return

    if not isinstance(retired, int) or not isinstance(retired_names, list):
        print(json.dumps({
            "result": "retry",
            "reason": "sources_retired is not an integer or retired_names is not a list",
            "fields": fields,
            "validation_errors": ["invalid_retire_fields"],
            "retry_instruction": "Record integer sources_retired and a retired_names list in step-07 outputs.",
        }))
        return

    if retired != len(retired_names):
        print(json.dumps({
            "result": "retry",
            "reason": f"sources_retired ({retired}) != len(retired_names) ({len(retired_names)})",
            "fields": fields,
            "validation_errors": ["retired_count_mismatch"],
            "retry_instruction": "Reconcile sources_retired with the retired_names list.",
        }))
        return

    if missing_from_dormant:
        print(json.dumps({
            "result": "retry",
            "reason": f"retired source(s) not found in dormant-sources.yaml: {missing_from_dormant[:5]} - a retired source must never be deleted",
            "fields": fields,
            "validation_errors": ["retired_source_lost"],
            "retry_instruction": "Move every retired source into dormant-sources.yaml (record kept for revival and audit).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-07 prune verified: {retired} source(s) retired, all accounted for in dormant-sources.yaml; ledger present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-01-gather.

Gather check. The step claims it fetched `sources_fetched` sources and
collected `item_count` candidate items. This verifier re-derives the claim
from the real registry rather than trusting the frontmatter self-report:

  * workflows/watchtower/sources.yaml must exist and list active sources;
  * `sources_fetched` must not exceed the number of active sources;
  * `item_count` must be a non-negative int and `failed_sources` a list.

Verdict: retry if the registry is missing or the counts are impossible; pass
otherwise (a genuine zero-item day is valid).
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

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-01-gather.md"
SOURCES_REL = Path("workflows") / "watchtower" / "sources.yaml"


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
    sources_path = ies_root / SOURCES_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-01-gather.md not found or YAML parser unavailable",
            "fields": {"gather_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-01-gather.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-01 outputs block is empty - no gather counts recorded",
            "fields": {"gather_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-01 and record item_count/sources_fetched/failed_sources in the step frontmatter outputs.",
        }))
        return

    active_sources = 0
    if sources_path.is_file():
        try:
            data = yaml.safe_load(sources_path.read_text()) or {}
            entries = data.get("sources") if isinstance(data, dict) else None
            if isinstance(entries, list):
                active_sources = sum(
                    1 for e in entries
                    if isinstance(e, dict) and e.get("status") == "active"
                )
        except Exception:
            active_sources = 0
    else:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/sources.yaml not found - the step's source registry is missing",
            "fields": {"gather_verified": False},
            "validation_errors": ["sources_registry_missing"],
            "retry_instruction": "Restore sources.yaml before re-running step-01.",
        }))
        return

    item_count = outputs.get("item_count")
    sources_fetched = outputs.get("sources_fetched")
    failed = outputs.get("failed_sources")

    fields = {
        "active_sources": active_sources,
        "item_count_reported": item_count,
        "sources_fetched_reported": sources_fetched,
        "failed_sources_reported": failed if isinstance(failed, list) else None,
    }

    if not isinstance(item_count, int) or item_count < 0:
        print(json.dumps({
            "result": "retry",
            "reason": "item_count is missing or not a non-negative integer",
            "fields": fields,
            "validation_errors": ["invalid_item_count"],
            "retry_instruction": "Record a non-negative integer item_count in step-01 outputs.",
        }))
        return

    if isinstance(sources_fetched, int) and active_sources and sources_fetched > active_sources:
        print(json.dumps({
            "result": "retry",
            "reason": f"sources_fetched ({sources_fetched}) exceeds the {active_sources} active source(s) in sources.yaml",
            "fields": fields,
            "validation_errors": ["sources_fetched_impossible"],
            "retry_instruction": "Reconcile sources_fetched with the active sources in sources.yaml.",
        }))
        return

    if not isinstance(failed, list):
        print(json.dumps({
            "result": "retry",
            "reason": "failed_sources is missing or not a list",
            "fields": fields,
            "validation_errors": ["invalid_failed_sources"],
            "retry_instruction": "Record failed_sources as a list (empty if none) in step-01 outputs.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-01 gather reconciled: {item_count} item(s) collected from {sources_fetched} of {active_sources} active source(s)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

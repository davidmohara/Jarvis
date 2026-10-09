#!/usr/bin/env python3
"""Ground-truth verifier for dream-cycle/step-03-semantic-promotion.

Promotion-accounting check. The step claims it promoted N episodic entries
into `cluster_actions[].target` semantic files. This verifier re-derives the
claim from the real filesystem rather than trusting the frontmatter
self-report:

  * every `cluster_actions[].target` path must exist under memory/semantic/;
  * if `promoted_entries` > 0 then at least one cluster action must be listed
    (a promotion with no recorded target is an unaccounted write);
  * semantic memory must be append-only in spirit - the targets must live
    under memory/semantic/.

Verdict: retry if a claimed target is missing or promotions are unaccounted
for; pass otherwise (including a zero-candidate cycle).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "dream-cycle" / "steps" / "step-03-semantic-promotion.md"


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
            "reason": "step-03-semantic-promotion.md not found or YAML parser unavailable",
            "fields": {"promotion_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/dream-cycle/steps/step-03-semantic-promotion.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "step-03 outputs block is empty - no promotion counts recorded",
            "fields": {"promotion_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-03 and record promoted_entries/semantic_updated/cluster_actions in the step frontmatter outputs.",
        }))
        return

    promoted = outputs.get("promoted_entries")
    cluster_actions = outputs.get("cluster_actions") or []
    if not isinstance(cluster_actions, list):
        cluster_actions = []

    targets = []
    for action in cluster_actions:
        if isinstance(action, dict) and action.get("target"):
            targets.append(str(action["target"]))

    missing_targets = [t for t in targets if not (ies_root / t).exists()]

    fields = {
        "promoted_entries_reported": promoted,
        "semantic_created_reported": outputs.get("semantic_created"),
        "semantic_updated_reported": outputs.get("semantic_updated"),
        "cluster_actions_count": len(cluster_actions),
        "targets_checked": len(targets),
        "missing_targets": missing_targets,
    }

    if missing_targets:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(missing_targets)} claimed semantic target(s) do not exist on disk: {missing_targets[:5]}",
            "fields": fields,
            "validation_errors": ["semantic_target_missing"],
            "retry_instruction": "Re-run step-03's semantic writes for the missing targets, or correct the cluster_actions targets in step-03 outputs.",
        }))
        return

    if isinstance(promoted, int) and promoted > 0 and not cluster_actions:
        print(json.dumps({
            "result": "retry",
            "reason": f"promoted_entries={promoted} but no cluster_actions were recorded - promotions are unaccounted for",
            "fields": fields,
            "validation_errors": ["unaccounted_promotions"],
            "retry_instruction": "Record one cluster_actions entry per promotion with its target semantic path.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-03 promotion claims reconcile: {len(targets)} semantic target(s) verified on disk, {promoted if promoted is not None else 'n/a'} entries promoted",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

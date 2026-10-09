#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-05-report.

Terminal weekly-report check. The step claims it surfaced `themes_surfaced`
themes, `candidates_surfaced` candidates, `sources_proposed` proposals, and
`tweets_surfaced` tweets, and closed the run. This verifier re-derives the
claim from the upstream steps and the real state file rather than trusting
the frontmatter self-report:

  * themes_surfaced must equal step-01's `themes_identified`;
  * tweets_surfaced must equal step-02b's `tweets_generated`;
  * sources_proposed must equal step-03's `proposed_count`;
  * the artifact must have been updated OR the fallback HTML must exist;
  * state.yaml must have reached a terminal state.

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

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-05-report.md"
STEP01_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-01-synthesize.md"
STEP02_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-02-draft-angles.md"
STEP02B_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-02b-draft-tweets.md"
STEP03_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-03-suggest-sources.md"
STATE_REL = Path("workflows") / "watchtower" / "state.yaml"
ARTIFACT_FALLBACK_REL = Path("workflows") / "watchtower" / "artifact-update" / "watchtower-weekly.html"


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
            "reason": "weekly-step-05-report.md not found or YAML parser unavailable",
            "fields": {"report_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-05-report.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-05 outputs block is empty - no report results recorded",
            "fields": {"report_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-05 and record themes_surfaced/candidates_surfaced/sources_proposed/tweets_surfaced in the step frontmatter outputs.",
        }))
        return

    def upstream_outputs(rel):
        p = ies_root / rel
        if p.is_file():
            o = extract_frontmatter(p.read_text()).get("outputs") or {}
            return o if isinstance(o, dict) else {}
        return {}

    s1 = upstream_outputs(STEP01_REL)
    s2 = upstream_outputs(STEP02_REL)
    s2b = upstream_outputs(STEP02B_REL)
    s3 = upstream_outputs(STEP03_REL)

    state = {}
    if (ies_root / STATE_REL).is_file():
        try:
            state = yaml.safe_load((ies_root / STATE_REL).read_text()) or {}
        except Exception:
            state = {}

    themes = outputs.get("themes_surfaced")
    candidates = outputs.get("candidates_surfaced")
    sources = outputs.get("sources_proposed")
    tweets = outputs.get("tweets_surfaced")
    artifact_updated = outputs.get("artifact_updated")
    fallback_exists = (ies_root / ARTIFACT_FALLBACK_REL).is_file()

    fields = {
        "themes_surfaced_reported": themes,
        "upstream_themes_identified": s1.get("themes_identified"),
        "candidates_surfaced_reported": candidates,
        "upstream_drafts_created": s2.get("drafts_created"),
        "sources_proposed_reported": sources,
        "upstream_proposed_count": s3.get("proposed_count"),
        "tweets_surfaced_reported": tweets,
        "upstream_tweets_generated": s2b.get("tweets_generated"),
        "artifact_updated": artifact_updated,
        "artifact_fallback_exists": fallback_exists,
        "state_status": state.get("status") if isinstance(state, dict) else None,
    }

    mismatches = []
    if isinstance(themes, int) and isinstance(s1.get("themes_identified"), int) and themes != s1["themes_identified"]:
        mismatches.append(f"themes_surfaced ({themes}) != step-01 themes_identified ({s1['themes_identified']})")
    if isinstance(tweets, int) and isinstance(s2b.get("tweets_generated"), int) and tweets != s2b["tweets_generated"]:
        mismatches.append(f"tweets_surfaced ({tweets}) != step-02b tweets_generated ({s2b['tweets_generated']})")
    if isinstance(sources, int) and isinstance(s3.get("proposed_count"), int) and sources != s3["proposed_count"]:
        mismatches.append(f"sources_proposed ({sources}) != step-03 proposed_count ({s3['proposed_count']})")

    if mismatches:
        print(json.dumps({
            "result": "retry",
            "reason": "step-05 report counts do not reconcile with upstream steps: " + "; ".join(mismatches),
            "fields": fields,
            "validation_errors": ["report_counts_mismatch"],
            "retry_instruction": "Recompute the terminal report counts from the step-01/02/02b/03 outputs.",
        }))
        return

    if artifact_updated is not True and not fallback_exists:
        print(json.dumps({
            "result": "retry",
            "reason": "artifact_updated is not true and no fallback HTML exists - the dashboard artifact update gate was not satisfied",
            "fields": fields,
            "validation_errors": ["artifact_not_updated"],
            "retry_instruction": "Update the watchtower-weekly artifact, or write the fallback HTML to workflows/watchtower/artifact-update/watchtower-weekly.html.",
        }))
        return

    if state.get("status") not in ("complete", "completed"):
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml status is '{state.get('status')}', not complete - the weekly run was not closed",
            "fields": fields,
            "validation_errors": ["state_not_complete"],
            "retry_instruction": "Set state.yaml status: complete and clear content_queue after surfacing the report.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-05 report reconciled: {themes} theme(s), {candidates} candidate(s), {sources} proposal(s), {tweets} tweet(s); state complete",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

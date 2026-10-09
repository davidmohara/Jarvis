#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-02-draft-angles.

Draft check. The step claims it created `drafts_created` draft files (listed
in `draft_paths`) and appended `blog_ideas_appended` candidate rows. This
verifier re-derives the claim from the real files rather than trusting the
frontmatter self-report:

  * `draft_paths` must be a list whose length equals `drafts_created`;
  * each draft path must be a Mind/Posts/ underscore-prefixed markdown path
    (or a fallback path under workflows/watchtower/fallback/drafts/);
  * reference/blog-ideas.md must exist (the candidate rows' destination).

Verdict: retry on a path/count mismatch or a missing blog-ideas register;
pass otherwise (a zero-theme week with zero drafts is valid).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-02-draft-angles.md"
BLOG_IDEAS_REL = Path("reference") / "blog-ideas.md"


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
    blog_ideas = ies_root / BLOG_IDEAS_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-02-draft-angles.md not found or YAML parser unavailable",
            "fields": {"drafts_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-02-draft-angles.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-02 outputs block is empty - no draft counts recorded",
            "fields": {"drafts_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-02 and record drafts_created/draft_paths/blog_ideas_appended in the step frontmatter outputs.",
        }))
        return

    drafts_created = outputs.get("drafts_created")
    draft_paths = outputs.get("draft_paths") or []
    if not isinstance(draft_paths, list):
        draft_paths = []

    malformed = [
        p for p in draft_paths
        if not (isinstance(p, str) and ("Mind/Posts/" in p or "fallback" in p))
    ]

    fields = {
        "drafts_created_reported": drafts_created,
        "draft_paths_count": len(draft_paths),
        "malformed_paths": malformed,
        "blog_ideas_exists": blog_ideas.is_file(),
        "blog_ideas_appended_reported": outputs.get("blog_ideas_appended"),
    }

    if not isinstance(drafts_created, int):
        print(json.dumps({
            "result": "retry",
            "reason": "drafts_created is missing or not an integer",
            "fields": fields,
            "validation_errors": ["invalid_drafts_created"],
            "retry_instruction": "Record an integer drafts_created in step-02 outputs.",
        }))
        return

    if drafts_created != len(draft_paths):
        print(json.dumps({
            "result": "retry",
            "reason": f"drafts_created ({drafts_created}) != len(draft_paths) ({len(draft_paths)})",
            "fields": fields,
            "validation_errors": ["draft_count_mismatch"],
            "retry_instruction": "Reconcile drafts_created with the draft_paths list.",
        }))
        return

    if malformed:
        print(json.dumps({
            "result": "retry",
            "reason": f"draft path(s) are neither Mind/Posts/ nor fallback paths: {malformed[:5]}",
            "fields": fields,
            "validation_errors": ["draft_path_malformed"],
            "retry_instruction": "Write drafts to Mind/Posts/_<slug>.md (or workflows/watchtower/fallback/drafts/ when Obsidian is unavailable).",
        }))
        return

    if drafts_created > 0 and not blog_ideas.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "reference/blog-ideas.md not found - candidate rows had nowhere to be appended",
            "fields": fields,
            "validation_errors": ["blog_ideas_missing"],
            "retry_instruction": "Restore reference/blog-ideas.md and append the candidate rows.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-02 drafts verified: {drafts_created} draft path(s) well-formed, blog-ideas register present",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

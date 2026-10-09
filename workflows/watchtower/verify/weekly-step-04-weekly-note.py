#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-04-weekly-note.

Weekly-note check. The step claims it wrote the Obsidian weekly note and
updated the artifact. This verifier re-derives the claim from the upstream
step outputs and the step's own path contract rather than trusting the
frontmatter self-report:

  * `weekly_note_path` must be a non-empty YYYY-Www.md (or fallback) path;
  * `themes_in_note` must equal step-01's `themes_identified`;
  * `tweets_in_note` must equal step-02b's `tweets_generated`;
  * the artifact must have been updated OR the mandatory fallback HTML must
    exist on disk (workflows/watchtower/artifact-update/watchtower-weekly.html).

Verdict: retry on a malformed path, a count mismatch, or a missing artifact
with no fallback; pass otherwise.
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

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-04-weekly-note.md"
STEP01_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-01-synthesize.md"
STEP02B_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-02b-draft-tweets.md"
ARTIFACT_FALLBACK_REL = Path("workflows") / "watchtower" / "artifact-update" / "watchtower-weekly.html"
WEEK_RE = re.compile(r"\d{4}-W\d{2}")


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
            "reason": "weekly-step-04-weekly-note.md not found or YAML parser unavailable",
            "fields": {"note_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-04-weekly-note.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-04 outputs block is empty - no note results recorded",
            "fields": {"note_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-04 and record weekly_note_path/themes_in_note/tweets_in_note/artifact_updated in the step frontmatter outputs.",
        }))
        return

    def upstream_outputs(rel):
        p = ies_root / rel
        if p.is_file():
            o = extract_frontmatter(p.read_text()).get("outputs") or {}
            return o if isinstance(o, dict) else {}
        return {}

    s1 = upstream_outputs(STEP01_REL)
    s2b = upstream_outputs(STEP02B_REL)

    note_path = outputs.get("weekly_note_path")
    themes_in_note = outputs.get("themes_in_note")
    tweets_in_note = outputs.get("tweets_in_note")
    artifact_updated = outputs.get("artifact_updated")
    fallback_exists = (ies_root / ARTIFACT_FALLBACK_REL).is_file()

    fields = {
        "weekly_note_path": note_path,
        "themes_in_note_reported": themes_in_note,
        "upstream_themes_identified": s1.get("themes_identified"),
        "tweets_in_note_reported": tweets_in_note,
        "upstream_tweets_generated": s2b.get("tweets_generated"),
        "artifact_updated": artifact_updated,
        "artifact_fallback_exists": fallback_exists,
    }

    if not (isinstance(note_path, str) and note_path.strip()):
        print(json.dumps({
            "result": "retry",
            "reason": "weekly_note_path is missing or empty",
            "fields": fields,
            "validation_errors": ["note_path_missing"],
            "retry_instruction": "Record the weekly note path in step-04 outputs.",
        }))
        return

    if not WEEK_RE.search(note_path) and "fallback" not in note_path:
        print(json.dumps({
            "result": "retry",
            "reason": f"weekly_note_path '{note_path}' is not a YYYY-Www weekly note path",
            "fields": fields,
            "validation_errors": ["note_path_malformed"],
            "retry_instruction": "Write the note to Watchtower/Weekly/YYYY-Www.md.",
        }))
        return

    if isinstance(themes_in_note, int) and isinstance(s1.get("themes_identified"), int) and themes_in_note != s1["themes_identified"]:
        print(json.dumps({
            "result": "retry",
            "reason": f"themes_in_note ({themes_in_note}) != step-01 themes_identified ({s1['themes_identified']})",
            "fields": fields,
            "validation_errors": ["themes_mismatch"],
            "retry_instruction": "Include every theme from step-01 in the weekly note.",
        }))
        return

    if isinstance(tweets_in_note, int) and isinstance(s2b.get("tweets_generated"), int) and tweets_in_note != s2b["tweets_generated"]:
        print(json.dumps({
            "result": "retry",
            "reason": f"tweets_in_note ({tweets_in_note}) != step-02b tweets_generated ({s2b['tweets_generated']})",
            "fields": fields,
            "validation_errors": ["tweets_mismatch"],
            "retry_instruction": "Render every tweet from step-02b in the weekly note.",
        }))
        return

    if artifact_updated is not True and not fallback_exists:
        print(json.dumps({
            "result": "retry",
            "reason": "artifact_updated is not true and no fallback HTML exists - the dashboard artifact update was skipped",
            "fields": fields,
            "validation_errors": ["artifact_not_updated"],
            "retry_instruction": "Update the watchtower-weekly artifact, or write the fallback HTML to workflows/watchtower/artifact-update/watchtower-weekly.html.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-04 weekly note verified: {note_path}, {themes_in_note} theme(s), {tweets_in_note} tweet(s), artifact {'updated' if artifact_updated else 'fallback written'}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

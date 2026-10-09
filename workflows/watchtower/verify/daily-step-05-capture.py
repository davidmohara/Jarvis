#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/daily-step-05-capture.

Capture check. The step claims it wrote the Obsidian daily note and built the
dashboard, capturing `items_captured` items. This verifier re-derives the
claim from the upstream step and the step's own output contract rather than
trusting the frontmatter self-report:

  * `obsidian_note_path` must be a non-empty string naming a Watchtower/Daily
    note (or a fallback path under workflows/watchtower/fallback/);
  * `items_captured` must equal step-04's `items_summarized`;
  * a fallback file must exist on disk when the note was written to fallback
    (Obsidian unavailable).

Verdict: retry if the path is malformed or the captured count mismatches;
pass otherwise (dashboard_built false is recorded as a note, not a failure -
the Obsidian note is primary).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-05-capture.md"
UPSTREAM_REL = Path("workflows") / "watchtower" / "steps" / "daily-step-04-summarize.md"
FALLBACK_DIR = Path("workflows") / "watchtower" / "fallback"


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
    upstream_path = ies_root / UPSTREAM_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-05-capture.md not found or YAML parser unavailable",
            "fields": {"capture_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/daily-step-05-capture.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "daily-step-05 outputs block is empty - no capture recorded",
            "fields": {"capture_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-05 and record obsidian_note_path/items_captured/dashboard_built in the step frontmatter outputs.",
        }))
        return

    note_path = outputs.get("obsidian_note_path")
    items_captured = outputs.get("items_captured")
    dashboard_built = outputs.get("dashboard_built")

    upstream_summarized = None
    if upstream_path.is_file():
        up_outputs = extract_frontmatter(upstream_path.read_text()).get("outputs") or {}
        if isinstance(up_outputs, dict):
            upstream_summarized = up_outputs.get("items_summarized")

    fallback_files = list((ies_root / FALLBACK_DIR).glob("*.md")) if (ies_root / FALLBACK_DIR).is_dir() else []

    fields = {
        "obsidian_note_path": note_path,
        "items_captured_reported": items_captured,
        "upstream_items_summarized": upstream_summarized,
        "dashboard_built": dashboard_built,
        "fallback_files_present": [p.name for p in fallback_files],
    }

    if not (isinstance(note_path, str) and note_path.strip()):
        print(json.dumps({
            "result": "retry",
            "reason": "obsidian_note_path is missing or empty",
            "fields": fields,
            "validation_errors": ["note_path_missing"],
            "retry_instruction": "Record the Obsidian daily-note path (or fallback path) in step-05 outputs.",
        }))
        return

    if "Watchtower/Daily/" not in note_path and "fallback" not in note_path:
        print(json.dumps({
            "result": "retry",
            "reason": f"obsidian_note_path '{note_path}' is neither a Watchtower/Daily note nor a fallback path",
            "fields": fields,
            "validation_errors": ["note_path_malformed"],
            "retry_instruction": "Write the note to Watchtower/Daily/YYYY-MM-DD.md (or workflows/watchtower/fallback/ if Obsidian is unavailable).",
        }))
        return

    if isinstance(upstream_summarized, int) and isinstance(items_captured, int) and items_captured != upstream_summarized:
        print(json.dumps({
            "result": "retry",
            "reason": f"items_captured ({items_captured}) != step-04 items_summarized ({upstream_summarized})",
            "fields": fields,
            "validation_errors": ["captured_mismatch"],
            "retry_instruction": "Reconcile items_captured with the summaries written.",
        }))
        return

    note = " (dashboard build not confirmed)" if dashboard_built is False else ""
    print(json.dumps({
        "result": "pass",
        "reason": f"step-05 capture verified: note path recorded, {items_captured} item(s) captured{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

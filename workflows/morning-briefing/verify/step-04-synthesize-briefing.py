#!/usr/bin/env python3
"""Ground-truth verifier for morning-briefing/step-04-synthesize-briefing.

Checks workflows/morning-briefing/state.yaml for an actual delivered
briefing (status: complete, last-run-notes content) and looks for the
mandatory POST-COMPLETION working memory file with the required
timestamped filename pattern (morning-briefing-YYYY-MM-DD-HHmmss.md) —
a date-only filename is explicitly called out in the step spec as a
failure, so it is checked here rather than trusted from a self-report.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

MIN_CONTENT_LENGTH = 200
WORKING_MEMORY_PATTERN = re.compile(r"^morning-briefing-\d{4}-\d{2}-\d{2}-\d{6}\.md$")
STALE_HOURS = 30


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    try:
        ref_time = datetime.fromisoformat(step_completed.replace("Z", "+00:00")) if step_completed else datetime.now(timezone.utc)
    except Exception:
        ref_time = datetime.now(timezone.utc)

    state_path = ies_root / "workflows" / "morning-briefing" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/morning-briefing/state.yaml missing or YAML parser unavailable",
            "fields": {"briefing_delivered": False, "working_memory_written": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04 — state.yaml must be updated with status: complete.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"morning-briefing/state.yaml invalid YAML: {e}",
            "fields": {"briefing_delivered": False, "working_memory_written": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04 — state.yaml is corrupted.",
        }))
        return

    notes = state.get("last-run-notes") or ""
    briefing_delivered = bool(notes) and len(notes) >= MIN_CONTENT_LENGTH
    status_ok = state.get("status") == "complete" and state.get("current-step") == "step-04"

    working_dir = ies_root / "memory" / "working"
    matches = []
    if working_dir.is_dir():
        for f in working_dir.glob("morning-briefing-*.md"):
            if WORKING_MEMORY_PATTERN.match(f.name):
                matches.append(f)
    matches.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    working_memory_written = False
    working_memory_file = None
    working_memory_age_hours = None
    if matches:
        f = matches[0]
        age_hours = (ref_time - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds() / 3600
        working_memory_file = f.name
        working_memory_age_hours = round(age_hours, 1)
        working_memory_written = age_hours <= STALE_HOURS

    validation_errors = []
    if not briefing_delivered:
        validation_errors.append("briefing_content_too_short")
    if not status_ok:
        validation_errors.append("state_status_or_step_mismatch")
    if not working_memory_written:
        validation_errors.append("working_memory_file_missing_or_stale")

    fields = {
        "briefing_delivered": briefing_delivered,
        "briefing_content_length": len(notes),
        "state_status": state.get("status"),
        "state_current_step": state.get("current-step"),
        "working_memory_written": working_memory_written,
        "working_memory_file": working_memory_file,
        "working_memory_age_hours": working_memory_age_hours,
    }

    if not briefing_delivered or not status_ok:
        print(json.dumps({
            "result": "retry",
            "reason": f"Briefing not properly delivered (content_len={len(notes)}, status={state.get('status')}, current-step={state.get('current-step')})",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-execute step-04 to synthesize and deliver the briefing, then update state.yaml to status: complete, current-step: step-04.",
        }))
        return

    if not working_memory_written:
        print(json.dumps({
            "result": "retry",
            "reason": "Briefing delivered but no matching morning-briefing-YYYY-MM-DD-HHmmss.md working memory file found within the freshness window",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Write the POST-COMPLETION working memory file with the mandatory timestamped filename pattern per reference/post-step-protocol.md.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Briefing delivered ({len(notes)} chars) and working memory file {working_memory_file} written",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

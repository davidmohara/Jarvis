#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-05-synthesize-briefing.

Checks workflows/morning-briefing/state.yaml for an actual delivered
briefing (last-run-notes content) near the step's time window, and
derives `briefing_sections` by counting labeled sections in that
content instead of trusting a self-reported count.
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
SECTION_PATTERN = re.compile(r'(?:^|[;.]\s+)([A-Z][A-Za-z0-9 /]{2,30}):')


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "morning-briefing" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/morning-briefing/state.yaml not found or YAML parser unavailable",
            "fields": {"briefing_delivered": False, "briefing_sections": 0},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05 — morning-briefing step-04 must run and update its state.yaml.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"morning-briefing/state.yaml invalid YAML: {e}",
            "fields": {"briefing_delivered": False, "briefing_sections": 0},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05 — the morning-briefing state file is corrupted.",
        }))
        return

    notes = state.get("last-run-notes") or ""
    sections = SECTION_PATTERN.findall(notes)
    fields = {
        "briefing_delivered": bool(notes) and len(notes) >= MIN_CONTENT_LENGTH,
        "briefing_sections": len(sections),
        "briefing_section_labels": sections,
        "briefing_content_length": len(notes),
        "last_run_status": state.get("last-run-status"),
    }

    if not notes or len(notes) < MIN_CONTENT_LENGTH:
        verdict = {
            "result": "retry",
            "reason": f"Briefing content is missing or too short ({len(notes)} chars, need >= {MIN_CONTENT_LENGTH}) in morning-briefing state",
            "fields": fields,
            "validation_errors": ["briefing_content_too_short"],
            "retry_instruction": "Re-execute morning-briefing step-04 to synthesize and deliver a real briefing.",
        }
    elif len(sections) == 0:
        verdict = {
            "result": "pass",
            "reason": f"Briefing content present ({len(notes)} chars) but no labeled sections detected — may be free-form prose",
            "fields": fields,
            "validation_errors": [],
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"Briefing delivered with {len(sections)} sections ({len(notes)} chars)",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

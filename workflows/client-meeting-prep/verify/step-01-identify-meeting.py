#!/usr/bin/env python3
"""Ground-truth verifier for client-meeting-prep/step-01-identify-meeting.

Re-derives the meeting identity from real records rather than trusting a
self-reported completion: it reads workflows/client-meeting-prep/state.yaml
accumulated-context, the step's own frontmatter outputs, and (as a last
resort) parses the saved prep-sheet filename, which encodes the attendee and
company. The step's hard requirement is an external attendee/company
identity; a missing calendar meeting is a valid state per the step's failure
modes, so only the identity is required here.
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


def load_state(path: Path) -> dict:
    if yaml is None or not path.is_file():
        return {}
    try:
        merged = {}
        for doc in yaml.safe_load_all(path.read_text()):
            if isinstance(doc, dict):
                for k, v in doc.items():
                    if k not in merged or v:
                        merged[k] = v
        return merged
    except Exception:
        return {}


def step_outputs(ies_root: Path) -> dict:
    p = ies_root / "workflows" / "client-meeting-prep" / "steps" / "step-01-identify-meeting.md"
    if yaml is None or not p.is_file():
        return {}
    lines = p.read_text().split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    inside = False
    for line in lines:
        if line.strip() == "---":
            inside = not inside
            if not inside:
                break
            continue
        if inside:
            fm_lines.append(line)
    try:
        return (yaml.safe_load("\n".join(fm_lines)) or {}).get("outputs") or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "client-meeting-prep" / "state.yaml")
    ctx = state.get("accumulated-context") or {}
    md = ctx.get("meeting_details") or {}
    attendees = md.get("attendees_external") or []
    outputs = step_outputs(ies_root)
    deliverables = ctx.get("deliverables") or {}
    md_file = deliverables.get("markdown_file") or ""

    attendee_names = []
    for a in attendees:
        if isinstance(a, dict) and a.get("name"):
            attendee_names.append(a["name"])
        elif isinstance(a, str) and a.strip():
            attendee_names.append(a.strip())

    # Filename fallback: "{Attendee} - {Company} - {date}.md" (separator may be
    # an em-dash, en-dash, or hyphen depending on the run).
    filename_attendee = None
    if md_file:
        parts = re.split(r"\s+[\u2014\u2013-]\s+", Path(md_file).stem)
        if parts and parts[0].strip():
            filename_attendee = parts[0].strip()

    fields = {
        "attendees_external_count": len(attendee_names),
        "attendee_names": attendee_names,
        "meeting_date": md.get("meeting_date"),
        "meeting_time_verified": md.get("meeting_time_verified"),
        "format_confirmed": md.get("format_confirmed"),
        "step_output_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
        "deliverable_attendee_from_filename": filename_attendee,
    }

    if not attendee_names and not filename_attendee and not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "No external attendee/company identity found in accumulated-context.meeting_details, "
                      "the step outputs, or the saved prep-sheet filename",
            "fields": fields,
            "validation_errors": ["missing_attendee_identity"],
            "retry_instruction": "Re-execute step-01: confirm the external attendee(s) and company and store "
                                 "them in accumulated-context.meeting_details.attendees_external before proceeding.",
        }))
        return

    label = ", ".join(attendee_names) or filename_attendee
    print(json.dumps({
        "result": "pass",
        "reason": f"Meeting identity confirmed: {label}"
        + (f" ({fields['meeting_date']})" if fields["meeting_date"] else " (no calendar date recorded)"),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

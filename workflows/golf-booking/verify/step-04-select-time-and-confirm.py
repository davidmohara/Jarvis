#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-04-select-time-and-confirm (Gate 3).

Re-derives the confirmation outcome and re-checks the two hard time limits that
Gate 3 success does not itself enforce: a round is never booked before 1:00 PM,
and never before 2:30 PM on a Sunday. The booked time/date is read from the step
frontmatter outputs and state.yaml, not trusted as a "success" flag. The
`booking-confirmation` guardrail checkpoint is reported leniently (a recording
gap is flagged only when an eval record exists without the entry). A documented
abort is a legitimate terminal state.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-booking"
CHECKPOINT_NAME = "booking-confirmation"


def parse_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm = []
    inside = False
    for line in lines:
        if line.strip() == "---":
            inside = not inside
            if not inside:
                break
            continue
        if inside:
            fm.append(line)
    try:
        return yaml.safe_load("\n".join(fm)) or {}
    except Exception:
        return {}


def parse_time_to_minutes(value):
    if not value:
        return None
    s = str(value).strip().upper()
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", s)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    meridiem = m.group(3)
    if meridiem == "PM" and hour != 12:
        hour += 12
    elif meridiem == "AM" and hour == 12:
        hour = 0
    return hour * 60 + minute


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    step_path = ies_root / "workflows" / WORKFLOW / "steps" / "step-04-select-time-and-confirm.md"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"booked_time": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-04 and record the booking outcome in state.yaml.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"booked_time": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-04: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    step_outputs = parse_frontmatter(step_path.read_text()) if step_path.is_file() else {}
    step_outputs = step_outputs.get("outputs") or {}

    def pick(key):
        if isinstance(step_outputs, dict) and step_outputs.get(key):
            return step_outputs.get(key)
        if isinstance(ctx, dict) and ctx.get(key):
            return ctx.get(key)
        return None

    booked_time = pick("booked_time") or pick("booking-time")
    booked_date = pick("booked_date") or pick("booking-date")
    status = state.get("status")
    resolution_note = (state.get("resolution-note") or "").strip()

    checkpoint_present = False
    eval_record_exists = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.exists():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            if data.get("name") != WORKFLOW:
                continue
            eval_record_exists = True
            for g in data.get("guardrails", []) or []:
                if g.get("name") == CHECKPOINT_NAME:
                    checkpoint_present = True
                    break
            if checkpoint_present:
                break

    fields = {
        "booked_date": booked_date,
        "booked_time": booked_time,
        "status": status,
        "resolution_note_length": len(resolution_note),
        "booking_confirmation_checkpoint_present": checkpoint_present,
    }

    if not booked_time:
        if status in ("aborted", "awaiting-window", "verification-failed") and len(resolution_note) >= 20:
            print(json.dumps({
                "result": "pass",
                "reason": f"No booking made (status {status}) with a documented reason, legitimate terminal state",
                "fields": fields,
                "validation_errors": [],
            }))
            return
        print(json.dumps({
            "result": "retry",
            "reason": "No booked_time recorded and no documented abort, Gate 3 confirmation is unproven",
            "fields": fields,
            "validation_errors": ["booking_not_confirmed"],
            "retry_instruction": "Re-execute step-04: only treat the exact BOOKING-SUCCESS string as success and record booked_date/booked_time, or abort with a documented resolution-note.",
        }))
        return

    minutes = parse_time_to_minutes(booked_time)
    if minutes is None:
        print(json.dumps({
            "result": "retry",
            "reason": f"booked_time '{booked_time}' is not parseable, cannot verify the hard time limits",
            "fields": fields,
            "validation_errors": ["booked_time_unparseable"],
            "retry_instruction": "Re-execute step-04: record booked_time in a parseable form (HH:MM or H:MM AM/PM).",
        }))
        return

    is_sunday = False
    if booked_date:
        try:
            is_sunday = datetime.strptime(str(booked_date), "%Y-%m-%d").weekday() == 6
        except Exception:
            is_sunday = False

    floor = (14 * 60 + 30) if is_sunday else (13 * 60)
    fields["booked_minutes"] = minutes
    fields["hard_floor_minutes"] = floor
    fields["is_sunday"] = is_sunday

    if minutes < floor:
        limit = "2:30 PM (Sunday church buffer)" if is_sunday else "1:00 PM (cost threshold)"
        print(json.dumps({
            "result": "retry",
            "reason": f"Booked time {booked_time} is before the hard limit {limit}",
            "fields": fields,
            "validation_errors": ["hard_time_limit_violated"],
            "retry_instruction": "Re-execute step-04: the booked time violates a hard rule from MANDATORY EXECUTION RULES 2-3. Move to a compliant option or abort.",
        }))
        return

    note = "" if checkpoint_present else (" (note: no booking-confirmation checkpoint recorded)" if eval_record_exists else " (note: no eval record found, checkpoint unverifiable)")
    print(json.dumps({
        "result": "pass",
        "reason": f"Booking confirmed at {booked_time} on {booked_date}, within hard limits{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

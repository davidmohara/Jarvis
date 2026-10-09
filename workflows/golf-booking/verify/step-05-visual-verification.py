#!/usr/bin/env python3
"""Ground-truth verifier for golf-booking/step-05-visual-verification (Gate 4).

Gate 4 is the second, independent confirmation that ChronoGolf's own
confirmation screen did not lie. This verifier re-derives the outcome from the
step outputs and state.yaml: a Gate 4 pass (approval true) is accepted, and a
recorded `verification-failed` abort with a documented reason is a legitimate
terminal state. A run that claims to have proceeded past step-05 without either
is the failure this catches.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

WORKFLOW = "golf-booking"


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


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    state_path = ies_root / "workflows" / WORKFLOW / "state.yaml"
    step_path = ies_root / "workflows" / WORKFLOW / "steps" / "step-05-visual-verification.md"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/golf-booking/state.yaml missing or YAML parser unavailable",
            "fields": {"gate_4_result": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-05 and record the Gate 4 outcome.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"gate_4_result": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-05: state.yaml is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    outputs = (parse_frontmatter(step_path.read_text()).get("outputs") or {}) if step_path.is_file() else {}

    gate_4 = None
    if isinstance(outputs, dict):
        gate_4 = outputs.get("gate_4_result") or outputs.get("approval") or outputs.get("booking_visible")
    if gate_4 is None and isinstance(ctx, dict):
        gate_4 = ctx.get("gate_4_result")

    status = state.get("status")
    resolution_note = (state.get("resolution-note") or "").strip()

    fields = {
        "gate_4_result": gate_4,
        "status": status,
        "resolution_note_length": len(resolution_note),
    }

    gate_4_str = str(gate_4).lower() if gate_4 is not None else ""
    if gate_4 is True or "pass" in gate_4_str or "approv" in gate_4_str or gate_4_str == "true":
        print(json.dumps({
            "result": "pass",
            "reason": f"Gate 4 visual verification recorded as passed ({gate_4})",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if status == "verification-failed" and len(resolution_note) >= 20:
        print(json.dumps({
            "result": "pass",
            "reason": "Gate 4 failed, but the run aborted with status verification-failed and a documented reason (correct escalation)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if status in ("aborted", "awaiting-window") and len(resolution_note) >= 20:
        print(json.dumps({
            "result": "pass",
            "reason": f"Run did not reach Gate 4 (status {status}) with a documented reason",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": "No Gate 4 pass recorded and no documented verification-failed abort, the visual verification outcome is unresolved",
        "fields": fields,
        "validation_errors": ["gate_4_unresolved"],
        "retry_instruction": "Re-execute step-05: run the visual-verification skill and record the approval decision, or set status: verification-failed with a resolution-note.",
    }))


if __name__ == "__main__":
    main()

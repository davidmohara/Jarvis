#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-07-verify-completion.

Confirms workflows/boot/state.yaml actually shows status: complete,
independently re-checks every prior step file's frontmatter status,
and derives `session_index_path` from the real existence of
memory/sessions/index.json rather than a self-reported path.
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

PRIOR_STEPS = [
    "step-01-load-context",
    "step-01.2-unified-data-pull",
    "step-01.5-unified-calendar-pull",
    "step-02-gather-data",
    "step-02.5-measure-phase2",
    "step-03-verify-phase2",
    "step-04-gather-meeting-context",
    "step-05-synthesize-briefing",
    "step-06-scan-workflows",
    "step-06.5-guardrail-checkpoint",
]


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

    state_path = ies_root / "workflows" / "boot" / "state.yaml"
    steps_dir = ies_root / "workflows" / "boot" / "steps"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/boot/state.yaml missing or YAML parser unavailable",
            "fields": {"state_status": None, "session_index_path": None},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Confirm workflows/boot/state.yaml exists and step-07 wrote status: complete to it.",
        }))
        return

    try:
        docs = [d for d in yaml.safe_load_all(state_path.read_text()) if d]
        state = docs[0] if docs else {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"workflows/boot/state.yaml invalid YAML: {e}",
            "fields": {"state_status": None, "session_index_path": None},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-07 — the boot state file is corrupted.",
        }))
        return

    state_status = state.get("status")

    not_complete = []
    for step_name in PRIOR_STEPS:
        step_file = steps_dir / f"{step_name}.md"
        if not step_file.is_file():
            not_complete.append(f"{step_name}: file missing")
            continue
        fm = extract_frontmatter(step_file.read_text())
        status = fm.get("status")
        if status != "complete":
            not_complete.append(f"{step_name}: status={status}")

    session_index_path = ies_root / "memory" / "sessions" / "index.json"
    session_index_exists = session_index_path.is_file()

    fields = {
        "state_status": state_status,
        "steps_verified": len(PRIOR_STEPS) - len(not_complete),
        "failed_steps": not_complete,
        "session_index_path": str(session_index_path.relative_to(ies_root)) if session_index_exists else None,
        "session_index_exists": session_index_exists,
    }

    validation_errors = [] if not not_complete else [f"step_not_complete: {n}" for n in not_complete]
    if not session_index_exists:
        validation_errors.append("session_index_missing")

    if not_complete or state_status != "complete":
        verdict = {
            "result": "retry",
            "reason": f"Boot not fully complete — state.yaml status={state_status}, {len(not_complete)} prior step(s) not complete",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-execute step-07 after ensuring all prior steps show status: complete and state.yaml is updated.",
        }
    elif not session_index_exists:
        verdict = {
            "result": "retry",
            "reason": "All steps complete but memory/sessions/index.json does not exist",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Write/update memory/sessions/index.json for this session before marking boot complete.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": f"All {len(PRIOR_STEPS)} prior steps complete, state.yaml status=complete, session index present",
            "fields": fields,
            "validation_errors": [],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

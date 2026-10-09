#!/usr/bin/env python3
"""Ground-truth verifier for system-eval/step-06-dashboard.

Finalization check. The step claims it regenerated the dashboard, wrote a
working-memory file, and closed this run's eval record. This verifier
re-derives the claim from the real files rather than trusting a self-report:

  * systems/eval-harness/dashboard.html must exist and be substantive
    (>1000 bytes);
  * a `memory/working/system-eval-*.md` file must exist (the working-memory
    write) and be substantive (>200 bytes);
  * this run's eval record (state.yaml `eval-record-id`) must not still be
    `status: in-progress` - it must have been closed.

Verdict: retry if the dashboard, the working-memory file, or the record
closure is missing; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STATE_REL = Path("workflows") / "system-eval" / "state.yaml"
DASHBOARD_REL = Path("systems") / "eval-harness" / "dashboard.html"


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / STATE_REL
    dashboard_path = ies_root / DASHBOARD_REL
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/system-eval/state.yaml not found or YAML parser unavailable",
            "fields": {"finalization_verified": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute step-06: the workflow state file must exist before finalization.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"system-eval/state.yaml invalid YAML: {e}",
            "fields": {"finalization_verified": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step-06: the workflow state file is corrupted.",
        }))
        return

    dashboard_ok = dashboard_path.is_file() and dashboard_path.stat().st_size > 1000

    wm_files = list((ies_root / "memory" / "working").glob("system-eval-*.md")) if (ies_root / "memory" / "working").is_dir() else []
    wm_substantive = [p for p in wm_files if p.stat().st_size > 200]

    eval_id = state.get("eval-record-id")
    record_status = None
    record_closed = False
    if eval_id and runs_dir.is_dir():
        rec = runs_dir / f"{eval_id}.json"
        if rec.is_file():
            try:
                record_status = json.loads(rec.read_text()).get("status")
                record_closed = record_status not in (None, "in-progress")
            except Exception:
                pass

    fields = {
        "dashboard_exists": dashboard_path.is_file(),
        "dashboard_substantive": dashboard_ok,
        "working_memory_files": [p.name for p in wm_files],
        "working_memory_substantive_count": len(wm_substantive),
        "eval_record_id": eval_id,
        "eval_record_status": record_status,
        "eval_record_closed": record_closed,
    }

    if not dashboard_ok:
        print(json.dumps({
            "result": "retry",
            "reason": "systems/eval-harness/dashboard.html is missing or under 1000 bytes",
            "fields": fields,
            "validation_errors": ["dashboard_missing"],
            "retry_instruction": "Re-execute step-06's generate-dashboard.py run.",
        }))
        return

    if not wm_substantive:
        print(json.dumps({
            "result": "retry",
            "reason": "no substantive (>200 byte) memory/working/system-eval-*.md file was written",
            "fields": fields,
            "validation_errors": ["working_memory_missing"],
            "retry_instruction": "Re-execute step-06's working-memory write.",
        }))
        return

    if eval_id and not record_closed:
        print(json.dumps({
            "result": "retry",
            "reason": f"this run's eval record ({eval_id}) is not closed (status: {record_status})",
            "fields": fields,
            "validation_errors": ["eval_record_open"],
            "retry_instruction": "Close this run's eval record via close-eval-record.py (or write the final fields directly if the script creates a spurious record).",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-06 finalization verified: dashboard present, {len(wm_substantive)} working-memory file(s), eval record closed",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

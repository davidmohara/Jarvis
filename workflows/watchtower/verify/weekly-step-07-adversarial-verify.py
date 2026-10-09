#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-07-adversarial-verify.

Stage 5 Phase 4A: the terminal adversarial verification step must have actually
run and recorded its verdict. This verifier reads the real
workflows/watchtower/state.yaml and confirms that
accumulated-context.adversarial-verification exists with a valid result, and
(cross-check) that an 'adversarial-verification' entry landed in a watchtower
eval record's guardrails array.

Verdict:
  * retry - the verification block is absent or malformed.
  * pass  - the verdict is recorded and valid. A 'flag' or 'escalate' verdict is
            a legitimate recorded outcome (a finding, not a step failure).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

VALID_RESULTS = ("pass", "flag", "escalate")


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "watchtower" / "state.yaml"
    if not state_path.is_file() or yaml is None:
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/watchtower/state.yaml missing or YAML parser unavailable",
            "fields": {"adversarial_verification_recorded": False},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Re-execute weekly-step-07-adversarial-verify and write accumulated-context.adversarial-verification to state.yaml.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"watchtower/state.yaml invalid YAML: {e}",
            "fields": {"adversarial_verification_recorded": False},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute weekly-step-07-adversarial-verify: the workflow state file is corrupted.",
        }))
        return

    ctx = state.get("accumulated-context") or {}
    block = ctx.get("adversarial-verification") if isinstance(ctx, dict) else None

    recorded = isinstance(block, dict)
    result_value = block.get("result") if recorded else None
    findings = block.get("findings") if recorded else None

    guardrail_present = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.exists():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            if data.get("name") != "watchtower":
                continue
            for g in data.get("guardrails", []) or []:
                if g.get("name") == "adversarial-verification":
                    guardrail_present = True
                    break
            if guardrail_present:
                break

    fields = {
        "adversarial_verification_recorded": recorded,
        "verification_result": result_value,
        "findings_count": len(findings) if isinstance(findings, list) else None,
        "guardrail_entry_present": guardrail_present,
    }

    if not recorded or result_value not in VALID_RESULTS:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.adversarial-verification is missing or has no valid result "
                      "(expected one of pass|flag|escalate): the adversarial verification step must run and record its verdict",
            "fields": fields,
            "validation_errors": ["adversarial_verification_not_recorded"],
            "retry_instruction": "Spawn Ralph with workflows/watchtower-verification/workflow.md, "
                                 "then write accumulated-context.adversarial-verification (verdict, result, findings) to state.yaml.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Adversarial verification recorded with result '{result_value}'"
        + (f" ({len(findings)} finding(s))" if isinstance(findings, list) and findings else "")
        + ("" if guardrail_present else " (note: no guardrail entry found in eval record)"),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

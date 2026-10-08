#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-05-verify-cleanup.

Stage 5 Phase 4A pattern: the adversarial verification step must have
actually run and recorded its verdict. This verifier reads the real
workflows/shutdown-cleanup/state.yaml and confirms that
accumulated-context.adversarial-verification exists with a valid result,
and (cross-check) that an 'adversarial-verification' entry landed in a
shutdown-cleanup eval record's guardrails array.

Verdict:
  * retry - the verification block is absent or malformed.
  * pass  - the verdict is recorded and valid. A 'flag' or 'escalate' verdict is a
            legitimate recorded outcome (a finding, not a step failure).
"""

import json
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[3]
STATE = Path(__file__).resolve().parents[1] / "state.yaml"
RUNS = IES_ROOT / "systems" / "eval-harness" / "runs"

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

VALID_RESULTS = ("pass", "flag", "escalate")


def load_state(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        # shutdown-cleanup's state.yaml carries multiple documents (--- separators);
        # search every document for accumulated-context rather than assuming one.
        merged = {}
        try:
            for doc in yaml.safe_load_all(text):
                if isinstance(doc, dict):
                    for k, v in doc.items():
                        if k not in merged or v:
                            merged[k] = v
            return merged
        except Exception:
            pass
    # minimal fallback parse of the flat accumulated-context field
    for line in text.splitlines():
        if line.strip().startswith("adversarial-verification:"):
            return {"accumulated-context": {"adversarial-verification": line.split(":", 1)[1].strip().strip('"')}}
    return {}


def main():
    fields = {}
    validation_errors = []

    state = load_state(STATE)
    acc = state.get("accumulated-context") or {}
    recorded = acc.get("adversarial-verification")
    fields["adversarial_verification_recorded"] = bool(recorded)

    result_value = None
    if isinstance(recorded, str):
        for v in VALID_RESULTS:
            if v in recorded.lower():
                result_value = v
                break
    elif isinstance(recorded, dict):
        result_value = recorded.get("result")
    fields["result"] = result_value

    # cross-check: guardrails array of the most recent shutdown-cleanup eval record
    guardrail_present = False
    candidates = sorted(RUNS.glob("eval-*.json"))
    for rec in reversed(candidates[-50:]):
        try:
            d = json.loads(rec.read_text())
        except Exception:
            continue
        name = d.get("workflow") or d.get("name") or ""
        if name != "shutdown-cleanup":
            continue
        for g in d.get("guardrails") or []:
            if g.get("name") == "adversarial-verification" or g.get("checkpoint_name") == "adversarial-verification":
                guardrail_present = True
                break
        if guardrail_present:
            break
    fields["guardrail_entry_in_eval_record"] = guardrail_present

    if not recorded or result_value not in VALID_RESULTS:
        print(json.dumps({
            "result": "retry",
            "reason": "accumulated-context.adversarial-verification is missing or has no valid result "
                      "(expected one of pass|flag|escalate): the adversarial verification step must run and record its verdict",
            "fields": fields,
            "validation_errors": ["adversarial_verification_not_recorded"],
            "retry_instruction": "Spawn Ralph with workflows/shutdown-cleanup-verification/workflow.md, "
                                 "then write accumulated-context.adversarial-verification (verdict, result, findings) to state.yaml.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Adversarial verification recorded with result '{result_value}'"
        + ("" if guardrail_present else " (note: no guardrail entry found in eval record)"),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

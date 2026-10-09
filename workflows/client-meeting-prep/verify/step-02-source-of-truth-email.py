#!/usr/bin/env python3
"""Ground-truth verifier for client-meeting-prep/step-02-source-of-truth-email.

The step's job is to classify why the meeting exists from first-party email
evidence and record it. This verifier re-derives that from
accumulated-context rather than trusting a completion flag: it requires a
recorded meeting_classification (a valid enum value) plus either a
reason_for_call statement or an evidence citation. A classification of
"unclear-insufficient-evidence" is a legitimate recorded outcome (an honest
statement that no evidence was found), not a failure.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

VALID_CLASSIFICATIONS = (
    "sales-sourced",
    "sales/prospect-sourced",
    "peer-relationship-referral",
    "peer/relationship/referral",
    "internal-review",
    "unclear-insufficient-evidence",
)


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


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "client-meeting-prep" / "state.yaml")
    ctx = state.get("accumulated-context") or {}

    classification = ctx.get("meeting_classification")
    reason = ctx.get("reason_for_call")
    evidence = ctx.get("evidence_cited") or []
    do_not_assume = ctx.get("do_not_assume") or []

    fields = {
        "meeting_classification": classification,
        "classification_is_known_enum": bool(classification)
        and any(str(classification).strip().lower().startswith(v) for v in VALID_CLASSIFICATIONS),
        "reason_for_call_present": bool(reason),
        "evidence_cited_count": len(evidence) if isinstance(evidence, list) else 0,
        "do_not_assume_count": len(do_not_assume) if isinstance(do_not_assume, list) else 0,
        "contact_depth": ctx.get("contact_depth"),
    }

    if not classification and not reason:
        print(json.dumps({
            "result": "retry",
            "reason": "No meeting_classification or reason_for_call recorded in accumulated-context: "
                      "step-02 must classify why the meeting exists from email evidence",
            "fields": fields,
            "validation_errors": ["missing_classification_and_reason"],
            "retry_instruction": "Re-execute step-02: query the email/calendar tool first, then record "
                                 "meeting_classification (and reason_for_call with an evidence citation) in accumulated-context.",
        }))
        return

    if not classification:
        print(json.dumps({
            "result": "retry",
            "reason": "reason_for_call recorded but meeting_classification is missing: the classification gates "
                      "step-03/04 tone and must be set from evidence",
            "fields": fields,
            "validation_errors": ["missing_classification"],
            "retry_instruction": "Re-execute step-02 and set accumulated-context.meeting_classification to one of "
                                 "sales-sourced | peer-relationship-referral | internal-review | unclear-insufficient-evidence.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Meeting classified as '{classification}'"
        + (f" with {fields['evidence_cited_count']} evidence citation(s)" if fields["evidence_cited_count"] else "")
        + (" (no email evidence found, honestly flagged)" if "unclear" in str(classification).lower() else ""),
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

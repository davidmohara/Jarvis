#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-03-verify-phase2.

Derives `critical_failures` from the actual presence/validity of the
core Phase 2 data sources (calendar, email, omnifocus) rather than
trusting Ralph's or the model's self-reported verification text.
"""

import json
import sys
from pathlib import Path

CRITICAL_SOURCES = {
    "calendar": "data/calendar-unified.json",
    "email": "data/email-unified.json",
    "omnifocus": "data/omnifocus-unified.json",
}


def file_ready(p: Path) -> bool:
    if not p.is_file():
        return False
    try:
        json.loads(p.read_text())
    except Exception:
        return False
    return True


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    critical_failures = []
    for name, rel in CRITICAL_SOURCES.items():
        if not file_ready(ies_root / rel):
            critical_failures.append(f"{name}: {rel} missing or invalid")

    fields = {
        "critical_failures": critical_failures,
        "critical_failure_count": len(critical_failures),
        "verification_results": "pass" if not critical_failures else f"fail — {len(critical_failures)} critical source(s) unavailable",
    }

    # Calendar and OmniFocus are the two sources boot cannot meaningfully
    # proceed without (email degradation is tolerated elsewhere in boot).
    hard_blockers = [f for f in critical_failures if f.startswith("calendar") or f.startswith("omnifocus")]

    if hard_blockers:
        verdict = {
            "result": "retry",
            "reason": f"Critical data source(s) unavailable: {'; '.join(hard_blockers)}",
            "fields": fields,
            "validation_errors": [f"critical_source_missing: {f}" for f in critical_failures],
            "retry_instruction": "Re-run the upstream pull steps to restore calendar/omnifocus data before proceeding.",
        }
    else:
        verdict = {
            "result": "pass",
            "reason": "0 critical data source failures" if not critical_failures else f"Non-blocking source degraded: {'; '.join(critical_failures)}",
            "fields": fields,
            "validation_errors": [f"degraded_source: {f}" for f in critical_failures],
        }

    print(json.dumps(verdict))


if __name__ == "__main__":
    main()

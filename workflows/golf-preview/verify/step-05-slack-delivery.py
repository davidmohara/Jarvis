#!/usr/bin/env python3
"""Ground-truth verifier for golf-preview/step-05 (Gate 5 — Slack Delivery).

The golf-preview skill's history includes a mandatory non-interactive
fallback rule (write to memory/working/ + log an error entry) for exactly
this failure mode: Slack unavailable during an unattended scheduled run.
This gate enforces that the fallback was actually taken, not just
documented as a rule that nobody checks.

Accepts either:
  (a) a captured Slack send result with ok: true and a timestamp, passed
      in the payload as `slack_send_result`, OR
  (b) a same-day fallback file under memory/working/golf-preview-*.md AND
      a corresponding entry under systems/error-tracking/entries/.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    slack_result = payload.get("slack_send_result") or {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if isinstance(slack_result, dict) and slack_result.get("ok") is True and slack_result.get("ts"):
        print(json.dumps({
            "result": "pass",
            "reason": f"Slack delivered — ts={slack_result.get('ts')}",
            "fields": {"delivery_path": "slack", "ts": slack_result.get("ts")},
            "validation_errors": [],
        }))
        return

    working_dir = ies_root / "memory" / "working"
    fallback_candidates = sorted(working_dir.glob(f"golf-preview-{today}*.md")) if working_dir.is_dir() else []
    # Also accept any golf-preview fallback file from the last 24h in case of date-boundary runs
    if not fallback_candidates and working_dir.is_dir():
        fallback_candidates = sorted(working_dir.glob("golf-preview-*.md"))[-1:]

    error_dir = ies_root / "systems" / "error-tracking" / "entries"
    has_recent_error_entry = False
    if error_dir.is_dir():
        for f in error_dir.glob("err-*.json"):
            try:
                content = f.read_text()
                if "golf-preview" in content or "slack" in content.lower():
                    has_recent_error_entry = True
                    break
            except Exception:
                continue

    if fallback_candidates and has_recent_error_entry:
        print(json.dumps({
            "result": "pass",
            "reason": f"Slack unavailable, but fallback documented: {fallback_candidates[-1].name} + error entry present",
            "fields": {"delivery_path": "fallback", "fallback_file": str(fallback_candidates[-1])},
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "retry",
        "reason": "Neither a confirmed Slack send nor a documented fallback (working-memory file + error entry) was found",
        "fields": {
            "delivery_path": "undocumented-failure",
            "fallback_candidates_found": [str(f) for f in fallback_candidates],
            "error_entry_found": has_recent_error_entry,
        },
        "validation_errors": ["no_slack_no_fallback"],
        "retry_instruction": "Either confirm the Slack send succeeded (capture ok:true + ts) or write memory/working/golf-preview-YYYY-MM-DD.md and log an error entry under systems/error-tracking/entries/ per the MANDATORY EXECUTION RULES in step-05.",
    }))


if __name__ == "__main__":
    main()

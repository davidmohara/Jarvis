#!/usr/bin/env python3
"""Ground-truth verifier for content-approval/step-01-approve.

Adapted from the retired workflows/content-pipeline/verify/step-02-approve.py.
Re-checks the cleanup rules step-01 is required to enforce on every run
(MANDATORY EXECUTION RULES 7-8, and the CLEANUP section of step-01-approve.md):
published entries must be removed, scheduled entries past their scheduled_at
must be removed, and rejected/deleted_externally entries older than 30 days
must be removed. Reads pending-drafts.json directly (now at
workflows/content-approval/pending-drafts.json) — does not trust the step's
self-reported outputs. An empty array, or an array with only compliant
pending/stalled entries, is a legitimate pass.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    drafts_path = ies_root / "workflows" / "content-approval" / "pending-drafts.json"

    if not drafts_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "pending-drafts.json does not exist",
            "fields": {"entries_total": 0},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Ensure pending-drafts.json exists — reset to [] if it was deleted.",
        }))
        return

    try:
        drafts = json.loads(drafts_path.read_text())
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"pending-drafts.json is not valid JSON: {e}",
            "fields": {"entries_total": 0},
            "validation_errors": ["invalid_json"],
            "retry_instruction": "pending-drafts.json is corrupted. Reset it to [] and re-run approval.",
        }))
        return

    if not isinstance(drafts, list):
        print(json.dumps({
            "result": "retry",
            "reason": "pending-drafts.json root is not a JSON array",
            "fields": {"entries_total": 0},
            "validation_errors": ["not_a_list"],
        }))
        return

    now = datetime.now(timezone.utc)
    cutoff_30d = now - timedelta(days=30)

    stale_published = []
    stale_scheduled = []
    stale_rejected = []
    stale_deleted_externally = []

    for entry in drafts:
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        gid = entry.get("ghost_post_id", "unknown")

        if status == "published":
            stale_published.append(gid)

        elif status == "scheduled":
            scheduled_at = parse_ts(entry.get("scheduled_at"))
            if scheduled_at and scheduled_at < now:
                stale_scheduled.append(gid)

        elif status == "rejected":
            created = parse_ts(entry.get("created_at"))
            if created and created < cutoff_30d:
                stale_rejected.append(gid)

        elif status == "deleted_externally":
            created = parse_ts(entry.get("created_at"))
            if created and created < cutoff_30d:
                stale_deleted_externally.append(gid)

    pending_count = sum(1 for e in drafts if isinstance(e, dict) and e.get("status") == "pending")

    fields = {
        "entries_total": len(drafts),
        "pending_count": pending_count,
        "stale_published_not_removed": stale_published,
        "stale_scheduled_not_removed": stale_scheduled,
        "stale_rejected_not_removed": stale_rejected,
        "stale_deleted_externally_not_removed": stale_deleted_externally,
    }

    validation_errors = []
    if stale_published:
        validation_errors.append(f"published_entries_not_cleaned: {len(stale_published)}")
    if stale_scheduled:
        validation_errors.append(f"past_scheduled_entries_not_cleaned: {len(stale_scheduled)}")
    if stale_rejected:
        validation_errors.append(f"old_rejected_entries_not_cleaned: {len(stale_rejected)}")
    if stale_deleted_externally:
        validation_errors.append(f"old_deleted_externally_entries_not_cleaned: {len(stale_deleted_externally)}")

    if validation_errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"pending-drafts.json cleanup was not applied: {', '.join(validation_errors)}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Run the CLEANUP rules from step-01-approve.md: remove published entries, past-scheduled entries, and rejected/deleted_externally entries older than 30 days.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Cleanup rules satisfied — {len(drafts)} entr(y/ies) total, {pending_count} pending, no stale published/scheduled/rejected entries",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

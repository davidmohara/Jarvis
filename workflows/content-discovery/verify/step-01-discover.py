#!/usr/bin/env python3
"""Ground-truth verifier for content-discovery/step-01-discover.

Adapted from the retired workflows/content-pipeline/verify/step-01-discover.py.
Confirms pending-drafts.json (now at workflows/content-approval/pending-drafts.json,
the shared file both split workflows read/write — see content-discovery/workflow.md
STATE TRACKING) is valid and internally consistent — every entry has the fields
step-01 is required to set (content_type is mandatory per MANDATORY EXECUTION RULE 8),
no duplicate ghost_post_id or duplicate pending source_url entries exist (the dedup
rule), and any entries created during this step's time window are well-formed. A run
that adds zero new entries (no new URLs/digests in the last 24h) is a legitimate pass —
this only fails on structural corruption or a broken mandatory-field rule, never on
"nothing to do."
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_FIELDS = ["ghost_post_id", "slack_channel", "title", "created_at", "status", "source_type", "content_type"]
VALID_CONTENT_TYPES = {"post", "article"}
VALID_STATUSES = {"pending", "published", "rejected", "scheduled", "approved_pending_publish", "deleted_externally", "stalled"}


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
    step_started = payload.get("step_started")
    step_completed = payload.get("step_completed")

    drafts_path = ies_root / "workflows" / "content-approval" / "pending-drafts.json"

    if not drafts_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "pending-drafts.json does not exist at workflows/content-approval/pending-drafts.json",
            "fields": {"entries_total": 0},
            "validation_errors": ["file_missing"],
            "retry_instruction": "Ensure workflows/content-approval/pending-drafts.json exists — reset to [] if it was deleted.",
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
            "retry_instruction": "pending-drafts.json is corrupted. Reset it to [] and re-run discovery.",
        }))
        return

    if not isinstance(drafts, list):
        print(json.dumps({
            "result": "retry",
            "reason": "pending-drafts.json root is not a JSON array",
            "fields": {"entries_total": 0},
            "validation_errors": ["not_a_list"],
            "retry_instruction": "pending-drafts.json must be a JSON array. Reset it to [] and re-run discovery.",
        }))
        return

    validation_errors = []
    missing_field_entries = []
    for i, entry in enumerate(drafts):
        if not isinstance(entry, dict):
            missing_field_entries.append(f"index_{i}_not_object")
            continue
        for field in REQUIRED_FIELDS:
            if field not in entry or entry.get(field) in (None, ""):
                missing_field_entries.append(f"{entry.get('ghost_post_id', f'index_{i}')}:missing_{field}")
        content_type = entry.get("content_type")
        if content_type is not None and content_type not in VALID_CONTENT_TYPES:
            missing_field_entries.append(f"{entry.get('ghost_post_id', f'index_{i}')}:invalid_content_type_{content_type}")
        status = entry.get("status")
        if status is not None and status not in VALID_STATUSES:
            missing_field_entries.append(f"{entry.get('ghost_post_id', f'index_{i}')}:invalid_status_{status}")

    ids_seen = {}
    for entry in drafts:
        if not isinstance(entry, dict):
            continue
        gid = entry.get("ghost_post_id")
        if gid:
            ids_seen[gid] = ids_seen.get(gid, 0) + 1
    duplicate_ids = [gid for gid, count in ids_seen.items() if count > 1]

    pending_urls = {}
    for entry in drafts:
        if not isinstance(entry, dict) or entry.get("status") != "pending":
            continue
        url = entry.get("source_url")
        if url:
            pending_urls[url] = pending_urls.get(url, 0) + 1
    duplicate_pending_urls = [u for u, count in pending_urls.items() if count > 1]

    window_start = parse_ts(step_started)
    window_end = parse_ts(step_completed)
    entries_created_this_run = 0
    if window_start and window_end:
        for entry in drafts:
            if not isinstance(entry, dict):
                continue
            created = parse_ts(entry.get("created_at"))
            if created and window_start <= created <= window_end:
                entries_created_this_run += 1

    if missing_field_entries:
        validation_errors.extend([f"malformed_entry: {m}" for m in missing_field_entries])
    if duplicate_ids:
        validation_errors.append(f"duplicate_ghost_post_id: {duplicate_ids}")
    if duplicate_pending_urls:
        validation_errors.append(f"duplicate_pending_source_url: {duplicate_pending_urls}")

    fields = {
        "entries_total": len(drafts),
        "entries_created_this_run": entries_created_this_run,
        "malformed_entries": missing_field_entries,
        "duplicate_ghost_post_ids": duplicate_ids,
        "duplicate_pending_source_urls": duplicate_pending_urls,
    }

    if missing_field_entries or duplicate_ids or duplicate_pending_urls:
        print(json.dumps({
            "result": "retry",
            "reason": f"pending-drafts.json has {len(missing_field_entries)} malformed entr(y/ies), {len(duplicate_ids)} duplicate id(s), {len(duplicate_pending_urls)} duplicate pending url(s)",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Fix the flagged pending-drafts.json entries — every entry needs content_type, a valid status, and no duplicate ghost_post_id or duplicate pending source_url.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"pending-drafts.json is well-formed with {len(drafts)} entr(y/ies), {entries_created_this_run} created this run",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()

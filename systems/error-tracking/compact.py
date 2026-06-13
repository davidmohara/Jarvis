#!/usr/bin/env python3
"""
Compact resolved error log entries into monthly digest files.

Usage:
    python3 compact.py                        # dry run — shows what would be compacted
    python3 compact.py --execute              # actually compact and delete source files
    python3 compact.py --month 2026-03        # compact a specific month only
    python3 compact.py --execute --month 2026-03
    python3 compact.py --status               # show current log state and compaction history

Safety:
    - Never compacts entries with fix_status=proposed or in-progress
    - Never compacts the current calendar month
    - Verifies digest completeness before deleting source files
    - Writes digest before deleting source files (digest first, delete second)
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRIES_DIR = ROOT / "entries"
DIGESTS_DIR = ROOT / "digests"
META_FILE = ROOT / "_meta.json"

# fix_status values that block compaction
OPEN_STATUSES = {"proposed", "in-progress"}

# fix_status values eligible for compaction
CLOSED_STATUSES = {"applied", "deferred", "not-applicable"}


def load_entries():
    """Load all entries from the entries directory."""
    entries = []
    for p in sorted(ENTRIES_DIR.glob("err-*.json")):
        try:
            e = json.loads(p.read_text())
            e["_path"] = str(p)
            entries.append(e)
        except Exception as ex:
            print(f"WARN: could not parse {p}: {ex}", file=sys.stderr)
    return entries


def get_entry_month(entry):
    """Extract YYYY-MM from an entry's timestamp or id."""
    ts = entry.get("timestamp") or entry.get("date") or ""
    if ts:
        # ISO 8601: 2026-03-21T... or 2026-03-21
        if len(ts) >= 7:
            return ts[:7]
    # Fall back to id prefix: err-20260321-001 or err-20260321T...
    eid = entry.get("id", "")
    if eid.startswith("err-"):
        raw = eid[4:]  # 20260321-001 or 20260321T...
        if len(raw) >= 6:
            return f"{raw[:4]}-{raw[4:6]}"
    return "unknown"


def get_fix_status(entry):
    """Get fix_status, normalizing camelCase variants."""
    return entry.get("fix_status") or entry.get("fixStatus") or "none"


def truncate_to_sentence(text):
    """Return the first sentence of text (truncate at first . ? ! or 150 chars)."""
    if not text:
        return ""
    text = text.strip()
    for i, ch in enumerate(text):
        if ch in ".?!" and i > 10:
            return text[: i + 1]
    # No sentence boundary — return first 150 chars
    if len(text) > 150:
        return text[:147] + "..."
    return text


def build_digest_entry(e):
    """Build a compact entry for the digest."""
    return {
        "id": e.get("id", "unknown"),
        "date": get_entry_month(e) + "-" + (e.get("timestamp", e.get("id", "")))[8:10]
        if len(e.get("timestamp", e.get("id", ""))) >= 10
        else get_entry_month(e),
        "category": e.get("category", "unknown"),
        "failure_mode": e.get("failure_mode", "unknown"),
        "severity": e.get("severity", "unknown"),
        "agent": e.get("agent", "unknown"),
        "source": e.get("source", "unknown"),
        "description": truncate_to_sentence(e.get("description", "")),
        "correction": truncate_to_sentence(e.get("correction", "")),
        "systemic_fix": truncate_to_sentence(e.get("systemic_fix", "")),
        "fix_status": get_fix_status(e),
    }


def build_month_digest(month_str, entries, existing_digest=None):
    """Build or merge a digest object for a given month."""
    now = datetime.now(timezone.utc).isoformat()

    # If merging into an existing digest, start from existing entries
    if existing_digest:
        existing_ids = {e["id"] for e in existing_digest.get("entries", [])}
        new_entries = [e for e in entries if e.get("id") not in existing_ids]
        all_digest_entries = existing_digest["entries"] + [
            build_digest_entry(e) for e in new_entries
        ]
    else:
        all_digest_entries = [build_digest_entry(e) for e in entries]

    # Sort by id for stability
    all_digest_entries.sort(key=lambda e: e["id"])

    # Aggregate stats over all entries (including previously compacted ones in this month)
    source_counts = Counter(e.get("source", "unknown") for e in all_digest_entries)
    severity_counts = Counter(e.get("severity", "unknown") for e in all_digest_entries)
    category_counts = Counter(e.get("category", "unknown") for e in all_digest_entries)
    fm_counts = Counter(e.get("failure_mode", "unknown") for e in all_digest_entries)
    agent_counts = Counter(e.get("agent", "unknown") for e in all_digest_entries)
    status_counts = Counter(e.get("fix_status", "unknown") for e in all_digest_entries)

    # Parse period label
    try:
        dt = datetime.strptime(month_str, "%Y-%m")
        period_label = dt.strftime("%B %Y")
    except ValueError:
        period_label = month_str

    digest = {
        "period": month_str,
        "period_label": period_label,
        "compacted_at": now,
        "entry_count": len(all_digest_entries),
        "source_breakdown": dict(source_counts),
        "severity_breakdown": dict(severity_counts),
        "category_breakdown": dict(
            sorted(category_counts.items(), key=lambda x: -x[1])
        ),
        "failure_mode_breakdown": dict(
            sorted(fm_counts.items(), key=lambda x: -x[1])
        ),
        "agent_breakdown": dict(sorted(agent_counts.items(), key=lambda x: -x[1])),
        "fix_status_breakdown": dict(status_counts),
        "patterns_identified": existing_digest.get("patterns_identified", [])
        if existing_digest
        else [],
        "entries": all_digest_entries,
    }

    return digest


def verify_digest(digest, source_entries):
    """Verify all source entry IDs appear in the digest."""
    source_ids = {e.get("id") for e in source_entries}
    digest_ids = {e["id"] for e in digest.get("entries", [])}
    missing = source_ids - digest_ids
    if missing:
        return False, missing
    return True, set()


def load_meta():
    try:
        return json.loads(META_FILE.read_text())
    except Exception:
        return {}


def save_meta(meta):
    META_FILE.write_text(json.dumps(meta, indent=2) + "\n")


def status_report(entries):
    """Print current log state."""
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")

    by_status = Counter(get_fix_status(e) for e in entries)
    by_month = defaultdict(list)
    for e in entries:
        by_month[get_entry_month(e)].append(e)

    print(f"\n=== Error Log Status ===")
    print(f"Total active entries: {len(entries)}")
    print(f"Current month (not eligible): {current_month}")
    print()
    print("Fix status breakdown:")
    for s, c in sorted(by_status.items()):
        flag = " (blocks compaction for any month containing these)" if s in OPEN_STATUSES else ""
        print(f"  {s}: {c}{flag}")
    print()

    # Show compaction eligibility by month
    print("By month:")
    for month in sorted(by_month.keys()):
        month_entries = by_month[month]
        open_in_month = [e for e in month_entries if get_fix_status(e) in OPEN_STATUSES]
        is_current = month == current_month
        eligible = not is_current and len(open_in_month) == 0
        flag = ""
        if is_current:
            flag = " (current month — not eligible)"
        elif open_in_month:
            flag = f" ({len(open_in_month)} open entries — not eligible)"
        else:
            flag = " ✓ eligible"
        print(f"  {month}: {len(month_entries)} entries{flag}")

    # Show existing digests
    if DIGESTS_DIR.exists():
        digests = sorted(DIGESTS_DIR.glob("compact-*.json"))
        if digests:
            print()
            print("Existing digests:")
            for d in digests:
                try:
                    ddata = json.loads(d.read_text())
                    print(
                        f"  {d.name}: {ddata.get('entry_count', '?')} entries "
                        f"({ddata.get('period_label', ddata.get('period', '?'))}), "
                        f"compacted {ddata.get('compacted_at', '?')[:10]}"
                    )
                except Exception:
                    print(f"  {d.name}: (could not parse)")

    # Show compaction history from meta
    meta = load_meta()
    history = meta.get("compaction_history", [])
    if history:
        print()
        print("Compaction history:")
        for h in history:
            print(
                f"  {h.get('period', '?')}: {h.get('entries_compacted', '?')} entries "
                f"on {h.get('compacted_at', '?')[:10]}"
            )


def main():
    ap = argparse.ArgumentParser(
        description="Compact resolved error log entries into monthly digests."
    )
    ap.add_argument(
        "--execute", action="store_true", help="Actually compact (default is dry run)"
    )
    ap.add_argument("--month", help="Compact a specific month only (YYYY-MM)")
    ap.add_argument(
        "--status", action="store_true", help="Show current log state and exit"
    )
    args = ap.parse_args()

    os.chdir(ROOT.parent.parent)  # Run from IES root

    entries = load_entries()

    if args.status:
        status_report(entries)
        return

    current_month = datetime.now(timezone.utc).strftime("%Y-%m")

    # Group by month first
    by_month = defaultdict(list)
    for e in entries:
        by_month[get_entry_month(e)].append(e)

    # Determine eligible months — a month is eligible only if ALL its entries are closed
    eligible_months = []
    ineligible_months = {}
    for month in sorted(by_month.keys()):
        if month == current_month:
            continue  # Never compact current month
        if args.month and month != args.month:
            continue  # Specific month filter
        month_open = [e for e in by_month[month] if get_fix_status(e) in OPEN_STATUSES]
        if month_open:
            ineligible_months[month] = month_open
        else:
            eligible_months.append(month)

    if ineligible_months:
        print("Note: the following months have open entries and cannot be compacted yet:")
        for month, open_list in sorted(ineligible_months.items()):
            print(f"  {month}: {len(open_list)} open entries")
            for e in open_list:
                print(f"    {e.get('id')}: fix_status={get_fix_status(e)}")
        print()

    if not eligible_months:
        if args.month:
            print(f"No eligible entries for month {args.month}.")
        else:
            print(f"No closed months with fully resolved entries to compact.")
        return

    total_to_compact = sum(len(by_month[m]) for m in eligible_months)
    print(
        f"{'DRY RUN — ' if not args.execute else ''}Compacting {total_to_compact} entries "
        f"across {len(eligible_months)} month(s): {', '.join(eligible_months)}"
    )

    if not args.execute:
        print()
        print("Run with --execute to perform compaction.")
        print()
        for month in eligible_months:
            month_entries = by_month[month]
            cats = Counter(e.get("category", "unknown") for e in month_entries)
            print(f"  {month}: {len(month_entries)} entries")
            for cat, cnt in cats.most_common(3):
                print(f"    {cat}: {cnt}")
        return

    # Execute compaction
    DIGESTS_DIR.mkdir(exist_ok=True)
    meta = load_meta()
    if "compaction_history" not in meta:
        meta["compaction_history"] = []

    compacted_total = 0
    now = datetime.now(timezone.utc).isoformat()

    for month in eligible_months:
        month_entries = by_month[month]
        digest_path = DIGESTS_DIR / f"compact-{month}.json"

        # Load existing digest if re-compacting
        existing_digest = None
        if digest_path.exists():
            try:
                existing_digest = json.loads(digest_path.read_text())
                print(
                    f"  {month}: merging into existing digest ({existing_digest.get('entry_count', '?')} existing entries)"
                )
            except Exception as ex:
                print(
                    f"  WARN: could not load existing digest for {month}: {ex}",
                    file=sys.stderr,
                )

        # Build digest
        digest = build_month_digest(month, month_entries, existing_digest)

        # Verify digest completeness
        ok, missing = verify_digest(digest, month_entries)
        if not ok:
            print(
                f"  ERROR: digest verification failed for {month} — missing IDs: {missing}",
                file=sys.stderr,
            )
            print(f"  Skipping {month} — source files NOT deleted.", file=sys.stderr)
            continue

        # Write digest
        digest_path.write_text(json.dumps(digest, indent=2) + "\n")
        print(
            f"  {month}: wrote digest → {digest_path} ({digest['entry_count']} entries)"
        )

        # Delete source files
        deleted = 0
        failed = []
        for e in month_entries:
            src = Path(e["_path"])
            try:
                src.unlink()
                deleted += 1
            except Exception as ex:
                failed.append((src, ex))

        if failed:
            print(
                f"  WARN: could not delete {len(failed)} source files:", file=sys.stderr
            )
            for src, ex in failed:
                print(f"    {src}: {ex}", file=sys.stderr)

        print(f"  {month}: deleted {deleted}/{len(month_entries)} source files")
        compacted_total += deleted

        # Update meta
        meta["last_compacted"] = now
        meta["compaction_history"].append(
            {
                "compacted_at": now,
                "period": month,
                "entries_compacted": deleted,
                "digest_path": str(digest_path.relative_to(ROOT.parent.parent)),
            }
        )

    save_meta(meta)

    # Final count
    remaining = list(ENTRIES_DIR.glob("err-*.json"))
    print()
    print(f"Compaction complete.")
    print(f"  Entries archived:  {compacted_total}")
    print(f"  Entries remaining: {len(remaining)}")


if __name__ == "__main__":
    main()

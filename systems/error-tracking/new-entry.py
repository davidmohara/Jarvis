#!/usr/bin/env python3
"""Generate a new error-log entry id and skeleton file.

The id format is `err-YYYYMMDDTHHMMSS-XXXXXX` where XXXXXX is a random
6-character alphanumeric suffix (A-Z, 0-9). This avoids cross-machine id
collisions and removes the need for sequential numbering, which is the
root cause of the per-machine merge conflicts that used to plague the
single error-log.json file.

Usage:
    python3 new-entry.py            # print id + write skeleton file
    python3 new-entry.py --id-only  # print id only, do not create file
"""
import argparse
import json
import secrets
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHABET = string.ascii_uppercase + string.digits  # 36 chars, ~2.1B combos


def new_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"err-{ts}-{suffix}"


def skeleton(entry_id: str) -> dict:
    return {
        "id": entry_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "session": "",
        "source": "explicit",
        "agent": "",
        "category": "",
        "description": "",
        "correction": "",
        "failure_mode": "",
        "systemic_fix": None,
        "fix_status": "proposed",
        "severity": "minor",
        "related_entries": [],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id-only", action="store_true", help="Print id only; do not create file")
    args = ap.parse_args()

    entry_id = new_id()
    if args.id_only:
        print(entry_id)
        return

    path = ROOT / "entries" / f"{entry_id}.json"
    if path.exists():
        print(f"Collision: {path} already exists", file=sys.stderr)
        sys.exit(1)
    path.write_text(json.dumps(skeleton(entry_id), indent=2) + "\n")
    print(str(path))


if __name__ == "__main__":
    main()

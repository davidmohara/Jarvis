#!/usr/bin/env python3
"""Generate a new error-log entry id and skeleton file, with schema validation.

The id format is `err-YYYYMMDDTHHMMSS-XXXXXX` where XXXXXX is a random
6-character alphanumeric suffix (A-Z, 0-9). This avoids cross-machine id
collisions and removes the need for sequential numbering, which is the
root cause of the per-machine merge conflicts that used to plague the
single error-log.json file.

Identity and classification values are validated at write time against the
canonical sets in schema.md, so a non-canonical entry can never land in
entries/ (the schema-enforcement gap behind the Tier 1 fix batch of
2026-09-17). Invalid severity/category fail loudly with the allowed set —
they are never silently coerced.

Usage:
    python3 new-entry.py --id-only                          # print id only, no file
    python3 new-entry.py --category <cat> [options]         # print id + write skeleton

    --category      REQUIRED. One of the 10 canonical categories (schema.md).
    --severity      minor (default) | moderate | major
    --agent         agent active when the error occurred (lowercase-normalized)
    --failure-mode  optional. Known labels validated; unknown labels warn but pass
    --session       optional session identifier
    --source        explicit (default) | self-detected
"""
import argparse
import json
import secrets
import string
import sys
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHABET = string.ascii_uppercase + string.digits  # 36 chars, ~2.1B combos

# Canonical sets — must stay in sync with systems/error-tracking/schema.md
SEVERITIES = ("minor", "moderate", "major")
CATEGORIES = (
    "data-accuracy",
    "tool-misuse",
    "routing-error",
    "format-violation",
    "missed-context",
    "assumption-error",
    "process-skip",
    "hallucination",
    "over-engineering",
    "under-delivery",
)
FAILURE_MODES = (
    "lazy-search",
    "stale-cache",
    "wrong-assumption",
    "sloppy-read",
    "bad-conversion",
    "tool-ignorance",
    "context-blindness",
    "pattern-mismatch",
    "scope-creep",
    "protocol-skip",
)
SOURCES = ("explicit", "self-detected")


def new_id(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"err-{ts}-{suffix}"


def skeleton(entry_id: str, category: str, severity: str, agent: str,
             failure_mode: str, session: str, source: str) -> dict:
    return {
        "id": entry_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "session": session,
        "source": source,
        "agent": agent,
        "category": category,
        "description": "",
        "correction": "",
        "failure_mode": failure_mode,
        "systemic_fix": None,
        "fix_status": "proposed",
        "severity": severity,
        "related_entries": [],
    }


def fail(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(
        description="Generate a validated error-log entry skeleton.",
        epilog=f"Categories: {', '.join(CATEGORIES)}",
    )
    ap.add_argument("--id-only", action="store_true", help="Print id only; do not create file")
    ap.add_argument("--category", default=None,
                    help=f"REQUIRED (unless --id-only). One of: {', '.join(CATEGORIES)}")
    ap.add_argument("--severity", default="minor",
                    help=f"Severity level (default: minor). One of: {', '.join(SEVERITIES)}")
    ap.add_argument("--agent", default="",
                    help="Agent active when the error occurred (lowercase-normalized)")
    ap.add_argument("--failure-mode", default="",
                    help=f"Optional root-cause label. Known: {', '.join(FAILURE_MODES)} "
                         "(unknown values warn but are kept)")
    ap.add_argument("--session", default="", help="Optional session identifier")
    ap.add_argument("--source", default="explicit",
                    help=f"explicit (default) or self-detected. One of: {', '.join(SOURCES)}")
    args = ap.parse_args()

    entry_id = new_id()
    if args.id_only:
        print(entry_id)
        return

    # --- Schema enforcement at write time (fail loudly, never silently coerce) ---

    if not args.category or not args.category.strip():
        fail("category is required and must be non-empty. "
             f"Allowed categories: {', '.join(CATEGORIES)}")

    category = args.category.strip().lower()
    if category not in CATEGORIES:
        fail(f"non-canonical category '{args.category}'. "
             f"Allowed categories: {', '.join(CATEGORIES)}")

    severity = args.severity.strip().lower()
    if severity not in SEVERITIES:
        fail(f"non-canonical severity '{args.severity}'. "
             f"Allowed severity levels: {', '.join(SEVERITIES)}")

    source = args.source.strip().lower()
    if source not in SOURCES:
        fail(f"non-canonical source '{args.source}'. Allowed sources: {', '.join(SOURCES)}")

    # Lowercase-normalize the agent field (e.g. "Jarvis" -> "jarvis", "Knox" -> "knox").
    agent = args.agent.strip().lower()

    failure_mode = args.failure_mode.strip().lower()
    if failure_mode and failure_mode not in FAILURE_MODES:
        # Unknown failure modes warn but do not block — legitimate self-detected
        # entries sometimes need a novel root-cause label; the warning keeps the
        # drift visible so schema.md can absorb genuinely recurring new labels.
        print(f"Warning: failure_mode '{args.failure_mode}' is not a known label "
              f"(known: {', '.join(FAILURE_MODES)}). Entry created with the value "
              f"as supplied — consider adding it to schema.md if it recurs.",
              file=sys.stderr)

    path = ROOT / "entries" / f"{entry_id}.json"
    if path.exists():
        print(f"Collision: {path} already exists", file=sys.stderr)
        sys.exit(1)
    path.write_text(json.dumps(skeleton(entry_id, category=category, severity=severity,
                                        agent=agent, failure_mode=failure_mode,
                                        session=args.session, source=source),
                               indent=2) + "\n")
    print(str(path))


if __name__ == "__main__":
    main()

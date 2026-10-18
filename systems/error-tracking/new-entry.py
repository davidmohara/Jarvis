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

The agent field is normalized through AGENT_ALIASES (jarvis -> master) plus
lowercase (pat-030, the agent-label-drift pattern); a label that is still not a
canonical manifest agent warns rather than blocks. validate_entry() is the
shared schema-conformance check: the write path runs it on every skeleton as a
self-check, and rebuild-log.py runs it over the whole log as a read-side
conformance report (pat-029). Neither path rewrites historical entries.

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
import re
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
FIX_STATUSES = ("proposed", "applied", "deferred", "not-applicable", "in-progress")

# Canonical IES agent names (agents/manifest.md), lowercase.
MANIFEST_AGENTS = (
    "master", "chief", "chase", "knox", "shep", "quinn",
    "harper", "rigby", "sterling", "galen", "ralph",
)

# Raw agent labels that normalize onto a canonical manifest agent. "Jarvis" is
# the name of the whole IES system, not an agent; the coordinator agent is
# `master`, so every `jarvis*` label canonicalizes to `master` (David's
# correction, 2026-10-16, err-20261016T123345-KNNL1T; pattern pat-030).
AGENT_ALIASES = {
    "jarvis": "master",
}

# Fields every conforming entry carries (schema.md "Entry Structure"). Presence
# is required; a couple of them may legitimately be null (session, systemic_fix)
# but the KEY must exist so the entry aggregates cleanly.
REQUIRED_FIELDS = (
    "id", "timestamp", "session", "source", "agent", "category",
    "description", "correction", "failure_mode", "systemic_fix",
    "fix_status", "severity", "related_entries", "related_skill",
)

# Alternate field names seen in hand-written entries that bypassed this script
# (pat-029). Their presence is the tell that an entry is invisible to
# category/failure_mode/severity aggregation — the whole point of the log.
ALTERNATE_FIELD_NAMES = ("error_type", "summary", "status", "proposed_fix")


def new_id(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"err-{ts}-{suffix}"


def canonical_agent(raw) -> str:
    """Normalize a raw agent label onto a canonical manifest agent name.

    Applies lowercase, drops a trailing parenthetical qualifier
    ('Jarvis (Master)' -> 'Jarvis'), takes the leading token, then maps through
    AGENT_ALIASES (jarvis -> master). An unknown label is returned lowercased
    and unchanged so the drift stays visible rather than being silently
    swallowed. Empty input returns ''.
    """
    if raw is None:
        return ""
    s = str(raw).strip().lower()
    s = s.split("(")[0].strip()
    s = re.split(r"[ /]", s)[0].strip()
    return AGENT_ALIASES.get(s, s)


def validate_entry(entry: dict, entry_id: Optional[str] = None) -> list:
    """Schema-conformance check for one entry. Returns a list of issues, each a
    dict {level, field, message}; empty list means conforming.

    Two levels:
      - "error": the entry breaks schema.md or is invisible to aggregation
        (missing required field, non-canonical category/severity/source/
        fix_status, an alternate field name shadowing a canonical one, or an
        id/filename mismatch).
      - "warning": drift that still parses (non-canonical failure_mode, which
        schema.md says warns rather than blocks; non-canonical agent label).

    Never mutates or rewrites the entry — this is the shared read-side check
    used by rebuild-log.py's conformance report, and the write-side self-check
    new-entry.py runs before writing a skeleton.
    """
    issues = []
    if not isinstance(entry, dict):
        return [{"level": "error", "field": "-", "message": "entry is not a JSON object"}]

    for f in REQUIRED_FIELDS:
        if f not in entry:
            issues.append({"level": "error", "field": f, "message": f"missing required field '{f}'"})

    # Canonical-value checks run only when the field is present, so a missing
    # field is reported once (as "missing"), not twice.
    if "category" in entry and entry.get("category") not in CATEGORIES:
        issues.append({"level": "error", "field": "category",
                       "message": f"non-canonical category {entry.get('category')!r}"})
    if "severity" in entry and entry.get("severity") not in SEVERITIES:
        issues.append({"level": "error", "field": "severity",
                       "message": f"non-canonical severity {entry.get('severity')!r}"})
    if "source" in entry and entry.get("source") not in SOURCES:
        issues.append({"level": "error", "field": "source",
                       "message": f"non-canonical source {entry.get('source')!r}"})
    if "fix_status" in entry and entry.get("fix_status") not in FIX_STATUSES:
        issues.append({"level": "error", "field": "fix_status",
                       "message": f"non-canonical fix_status {entry.get('fix_status')!r}"})

    fm = entry.get("failure_mode")
    if fm and fm not in FAILURE_MODES:
        issues.append({"level": "warning", "field": "failure_mode",
                       "message": f"non-canonical failure_mode {fm!r}"})

    for alt in ALTERNATE_FIELD_NAMES:
        if alt in entry:
            issues.append({"level": "error", "field": alt,
                           "message": f"alternate field '{alt}' present (shadows a canonical field)"})

    ag = entry.get("agent")
    if ag and canonical_agent(ag) not in MANIFEST_AGENTS:
        issues.append({"level": "warning", "field": "agent",
                       "message": f"non-canonical agent label {ag!r}"})

    if entry_id is not None and entry.get("id") not in (None, entry_id):
        issues.append({"level": "error", "field": "id",
                       "message": f"id {entry.get('id')!r} does not match filename {entry_id!r}"})

    return issues


def skeleton(entry_id: str, category: str, severity: str, agent: str,
             failure_mode: str, session: str, source: str,
             related_skill: str | None = None) -> dict:
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
        "related_skill": related_skill or None,
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
    ap.add_argument("--related-skill", default="",
                    help="Optional skill-id the error traces to (routing key for Gotchas writeback)")
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

    # Normalize the agent field: lowercase + the jarvis->master alias map
    # (e.g. "Jarvis" -> "master", "Knox" -> "knox"). A label that is still not
    # a canonical manifest agent warns but does not block (pat-030 keeps the
    # drift visible rather than silently rewriting the operator's intent).
    agent = canonical_agent(args.agent)
    if agent and agent not in MANIFEST_AGENTS:
        print(f"Warning: agent label '{args.agent}' is not a canonical manifest agent "
              f"({', '.join(MANIFEST_AGENTS)}). Entry created with the normalized value "
              f"'{agent}' — consider correcting the label if it drifts.", file=sys.stderr)

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

    entry = skeleton(entry_id, category=category, severity=severity,
                     agent=agent, failure_mode=failure_mode,
                     session=args.session, source=source,
                     related_skill=args.related_skill.strip() or None)

    # Self-check: the skeleton we are about to write must conform. Any "error"
    # here is a bug in this script, not in the caller's input, so fail loudly.
    errors = [i for i in validate_entry(entry, entry_id=entry_id) if i["level"] == "error"]
    if errors:
        fail("generated skeleton failed schema self-check: "
             + "; ".join(f"{i['field']}: {i['message']}" for i in errors))

    path.write_text(json.dumps(entry, indent=2) + "\n")
    print(str(path))


if __name__ == "__main__":
    main()

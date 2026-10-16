#!/usr/bin/env python3
"""Aggregate per-entry files into a single log view for analysis.

Reads systems/error-tracking/_meta.json and every systems/error-tracking/entries/*.json,
sorts entries by id, and writes a combined view to stdout (or to --out path).

Usage:
    python3 rebuild-log.py                  # print to stdout
    python3 rebuild-log.py --out log.json   # write to file
    python3 rebuild-log.py --conformance    # print a schema-conformance report

The --conformance report flags entries that do not conform to schema.md — the
pat-029 remediation. It uses the shared validate_entry() from new-entry.py and
NEVER rewrites an entry; it only reports. Nonconforming entries are invisible to
category/failure_mode/severity aggregation, so the report names them explicitly
at analysis time instead of letting them hide.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_validator():
    """Load validate_entry() from new-entry.py (hyphenated filename, so it can't
    be imported normally). Returns None if unavailable."""
    path = ROOT / "new-entry.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ies_new_entry", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"Warning: could not load validator from new-entry.py: {e}", file=sys.stderr)
        return None
    return getattr(mod, "validate_entry", None)


def build():
    meta = json.loads((ROOT / "_meta.json").read_text())
    entry_files = sorted((ROOT / "entries").glob("err-*.json"))
    entries = []
    for p in entry_files:
        try:
            entries.append((p.stem, json.loads(p.read_text())))
        except Exception as e:
            print(f"Warning: could not parse {p.name}: {e}", file=sys.stderr)
    entries.sort(key=lambda pair: pair[1].get("id") or pair[0])
    return {"metadata": meta, "entries": [e for _, e in entries]}, entries


def conformance_pairs():
    """(entry_id, entry) pairs for the conformance scan.

    Scans EVERY *.json in entries/, not just the canonical err-*.json the
    aggregate uses — a legacy-named file (e.g. golf-booking-session-expired-
    *.json) is itself a nonconforming entry and would otherwise be invisible to
    both the aggregate and the report."""
    pairs = []
    for p in sorted((ROOT / "entries").glob("*.json")):
        try:
            pairs.append((p.stem, json.loads(p.read_text())))
        except Exception as e:
            print(f"Warning: could not parse {p.name}: {e}", file=sys.stderr)
    return pairs


def conformance_report(entries):
    """Print a schema-conformance report over (entry_id, entry) pairs.

    Does not modify anything. Returns the count of nonconforming entries."""
    validate_entry = load_validator()
    if validate_entry is None:
        print("Conformance report unavailable: new-entry.py validator not loadable.",
              file=sys.stderr)
        return 0

    nonconforming = []
    error_entries = 0
    warning_entries = 0
    field_counts = {}
    for entry_id, entry in entries:
        issues = validate_entry(entry, entry_id=entry_id)
        if not issues:
            continue
        levels = {i["level"] for i in issues}
        if "error" in levels:
            error_entries += 1
        elif "warning" in levels:
            warning_entries += 1
        for i in issues:
            key = (i["level"], i["field"])
            field_counts[key] = field_counts.get(key, 0) + 1
        nonconforming.append((entry_id, entry.get("agent"), issues))

    total = len(entries)
    print(f"Schema-conformance report — {ROOT}")
    print(f"  entries scanned:        {total}")
    print(f"  conforming:             {total - len(nonconforming)}")
    print(f"  nonconforming (errors): {error_entries}")
    print(f"  drift-only (warnings):  {warning_entries}")
    print(f"  total flagged:          {len(nonconforming)} "
          f"({100 * len(nonconforming) / total:.1f}% of {total})" if total else "")
    print()
    print("  Issues by field (level, field -> count):")
    for (level, field), count in sorted(field_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {count:4}  [{level}] {field}")
    print()
    print("  Flagged entries:")
    for entry_id, agent, issues in nonconforming:
        tags = ", ".join(f"{i['level']}:{i['field']}" for i in issues)
        print(f"    {entry_id}  agent={agent!r}  {tags}")
    return len(nonconforming)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="Write to this path instead of stdout")
    ap.add_argument("--conformance", action="store_true",
                    help="Print a schema-conformance report and exit (does not rewrite entries)")
    args = ap.parse_args()

    data, pairs = build()

    if args.conformance:
        conformance_report(conformance_pairs())
        return

    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if args.out:
        Path(args.out).write_text(text)
        print(f"Wrote {len(data['entries'])} entries to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()

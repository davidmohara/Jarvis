#!/usr/bin/env python3
"""Aggregate per-entry files into a single log view for analysis.

Reads systems/error-tracking/_meta.json and every systems/error-tracking/entries/*.json,
sorts entries by id, and writes a combined view to stdout (or to --out path).

Usage:
    python3 rebuild-log.py                  # print to stdout
    python3 rebuild-log.py --out log.json   # write to file
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    meta = json.loads((ROOT / "_meta.json").read_text())
    entry_files = sorted((ROOT / "entries").glob("err-*.json"))
    entries = [json.loads(p.read_text()) for p in entry_files]
    entries.sort(key=lambda e: e["id"])
    return {"metadata": meta, "entries": entries}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="Write to this path instead of stdout")
    args = ap.parse_args()

    data = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    if args.out:
        Path(args.out).write_text(text)
        print(f"Wrote {len(data['entries'])} entries to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Dream Cycle Step 02 — Salience Scoring

Scores all episodic entries by co-occurrence frequency within the last 30 days.
Writes updated salience.score and salience.last-promoted-check to each file.

CRITICAL: Merges into the existing salience block — never replaces it wholesale.
Preserves salience.promoted (and any other existing salience fields) across rewrites.
This prevents the "promoted:true silently dropped every night" bug traced in
dream-summary-pattern.md 2026-07-15.

Usage:
    python3 systems/dream-cycle/salience-score.py [--date YYYY-MM-DD] [--dry-run]
"""

import os
import re
import sys
import argparse
from datetime import date, timedelta

EPISODIC_DIR = os.path.join(os.path.dirname(__file__), "../../memory/episodic")
EPISODIC_DIR = os.path.normpath(EPISODIC_DIR)


def parse_frontmatter(content):
    """Extract YAML frontmatter fields. Returns (fm_dict, raw_fm_text, body)."""
    if not content.startswith("---"):
        return {}, "", content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, "", content
    fm_text = content[3:end]
    body = content[end + 4:]

    fm = {}

    # tags (block list)
    tags_m = re.search(r"^tags:\s*\n((?:[ \t]+-[^\n]*\n)*)", fm_text, re.MULTILINE)
    if tags_m:
        fm["tags"] = [
            re.sub(r"^[ \t]+-\s*", "", l).strip()
            for l in tags_m.group(1).strip().splitlines()
            if l.strip()
        ]
    else:
        inline = re.search(r"^tags:\s*\[([^\]]*)\]", fm_text, re.MULTILINE)
        fm["tags"] = (
            [t.strip().strip("\"'") for t in inline.group(1).split(",") if t.strip()]
            if inline
            else []
        )

    # date
    date_m = re.search(r"^date:\s*(.+)$", fm_text, re.MULTILINE)
    if date_m:
        try:
            fm["date"] = date.fromisoformat(date_m.group(1).strip()[:10])
        except ValueError:
            fm["date"] = None
    else:
        fm["date"] = None

    # existing salience fields (preserve across rewrite)
    promoted_m = re.search(r"^\s*promoted:\s*(true|false)", fm_text, re.MULTILINE)
    fm["promoted"] = (promoted_m.group(1) == "true") if promoted_m else None  # None = not set

    return fm, fm_text, body


def update_salience_block(content, new_score, today_str, preserve_promoted):
    """
    Merge-update the salience block in frontmatter.

    Preserves any existing salience fields (especially promoted) while updating
    score and last-promoted-check. This is the fix for the drop-on-rewrite bug.
    """
    if not content.startswith("---"):
        return content
    end = content.find("\n---", 3)
    if end == -1:
        return content

    fm_section = content[3:end]
    rest = content[end:]

    # Build the new salience block
    salience_lines = [
        f"  score: {new_score}",
        f"  last-promoted-check: {today_str}",
    ]
    if preserve_promoted is True:
        salience_lines.append("  promoted: true")

    salience_block = "\nsalience:\n" + "\n".join(salience_lines)

    # Remove any existing salience block (multiline or inline)
    fm_section = re.sub(
        r"\nsalience:\s*\n(?:[ \t]+[^\n]*\n)*", "\n", fm_section
    )
    fm_section = re.sub(r"\nsalience:\s*\{[^\}]*\}", "", fm_section)
    # Also remove any stray top-level promoted: lines (old corruption pattern)
    fm_section = re.sub(r"\npromoted:\s*(true|false)", "", fm_section)

    fm_section = fm_section.rstrip() + salience_block

    return "---" + fm_section + rest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="Override today's date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Score but do not write files")
    args = parser.parse_args()

    today = date.fromisoformat(args.date) if args.date else date.today()
    window_start = today - timedelta(days=30)
    today_str = today.isoformat()

    entries = []
    no_date_files = []
    read_errors = []

    for fname in os.listdir(EPISODIC_DIR):
        fpath = os.path.join(EPISODIC_DIR, fname)
        if os.path.isdir(fpath) and fname == "digests":
            continue
        if not fname.endswith(".md") or fname == "README.md":
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            fm, fm_text, body = parse_frontmatter(content)
            entries.append(
                {
                    "path": fpath,
                    "fname": fname,
                    "content": content,
                    "tags": fm.get("tags", []),
                    "date": fm.get("date"),
                    "promoted": fm.get("promoted"),  # True, False, or None (not set)
                }
            )
            if fm.get("date") is None:
                no_date_files.append(fname)
        except Exception as e:
            read_errors.append(f"{fname}: {e}")

    window_entries = [
        e for e in entries if e["date"] and window_start <= e["date"] <= today
    ]

    score_updates = 0
    write_errors = []
    score_dist = {}

    for entry in entries:
        etags = set(entry["tags"])
        score = 0
        if etags:
            for other in window_entries:
                if other["path"] == entry["path"]:
                    continue
                if len(etags & set(other["tags"])) >= 2:
                    score += 1
        score = min(score, 10)
        score_dist[score] = score_dist.get(score, 0) + 1

        # Preserve promoted=True; ignore False/None (not yet promoted)
        preserve_promoted = entry["promoted"] is True

        if not args.dry_run:
            try:
                new_content = update_salience_block(
                    entry["content"], score, today_str, preserve_promoted
                )
                with open(entry["path"], "w", encoding="utf-8") as f:
                    f.write(new_content)
                score_updates += 1
            except Exception as e:
                write_errors.append(f"{entry['fname']}: {e}")

    dist_str = ",".join(f"{k}:{v}" for k, v in sorted(score_dist.items()))

    print(f"episodic_scanned: {len(entries)}")
    print(f"score_updates: {score_updates}")
    print(f"window_entries: {len(window_entries)}")
    print(f"no_date: {len(no_date_files)}")
    print(f"no_tags: {sum(1 for e in entries if not e['tags'])}")
    print(f"score_distribution: {dist_str}")
    print(f"read_errors: {len(read_errors)}")
    print(f"write_errors: {len(write_errors)}")
    if args.dry_run:
        print("(dry-run: no files written)")
    for err in read_errors + write_errors:
        print(f"  ERROR: {err}")


if __name__ == "__main__":
    main()

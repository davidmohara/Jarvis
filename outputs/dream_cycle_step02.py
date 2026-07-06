#!/usr/bin/env python3
"""Dream Cycle step-02: salience scoring for 2026-07-05.

Preserves prior `promoted: true` flags — regression noted in 2026-07-03 cycle.
Uses regex-based frontmatter extraction (per 2026-07-04 repair pattern).
"""
import os
import re
import sys
import json
import datetime

ROOT = "/Users/davidohara/develop/jarvis"
EPISODIC = os.path.join(ROOT, "memory/episodic")

TODAY = datetime.date(2026, 7, 5)
WINDOW_START = TODAY - datetime.timedelta(days=30)  # 2026-06-05

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)

def extract_field(fm, name):
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.+?)$", fm, re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else None

def extract_list(fm, name):
    """Extract a YAML list block. Handles both inline [a, b] and block form."""
    # inline form
    m = re.search(rf"^{re.escape(name)}\s*:\s*\[(.+?)\]", fm, re.MULTILINE)
    if m:
        return [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    # block form
    m = re.search(rf"^{re.escape(name)}\s*:\s*\n((?:\s*-\s*.+\n?)+)", fm, re.MULTILINE)
    if m:
        return [ln.strip().lstrip("- ").strip().strip("'\"") for ln in m.group(1).splitlines() if ln.strip()]
    return []

def extract_promoted(fm):
    """Extract prior salience.promoted value from any of its known layouts."""
    # nested: salience: \n  promoted: true
    m = re.search(r"^salience\s*:\s*\n((?:\s{2,}\S.*\n?)+)", fm, re.MULTILINE)
    if m:
        block = m.group(1)
        mp = re.search(r"^\s+promoted\s*:\s*(\S+)", block, re.MULTILINE)
        if mp:
            return mp.group(1).strip().lower() == "true"
    # orphan `promoted: true` line
    m = re.search(r"^\s*promoted\s*:\s*(\S+)", fm, re.MULTILINE)
    if m:
        return m.group(1).strip().lower() == "true"
    return False

def rewrite_salience_block(fm, score, promoted):
    """Remove any existing salience block/orphans, write a clean nested block."""
    # Remove nested salience block
    fm = re.sub(r"^salience\s*:\s*\n(?:\s{2,}\S.*\n?)+", "", fm, flags=re.MULTILINE)
    # Remove orphan lines
    for k in ["score", "last_scored", "last-promoted-check", "promoted"]:
        fm = re.sub(rf"^\s{{0,4}}{k}\s*:.*\n?", "", fm, flags=re.MULTILINE)
    # Append clean block
    block = f"salience:\n  score: {score}\n  last_scored: {TODAY.isoformat()}\n  last-promoted-check: {TODAY.isoformat()}\n  promoted: {'true' if promoted else 'false'}"
    return fm.rstrip("\n") + "\n" + block

def parse_date(val):
    if not val:
        return None
    val = val.strip().strip("'\"")
    m = re.match(r"(\d{4}-\d{2}-\d{2})", val)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1))
        except ValueError:
            return None
    return None

# ---- collect entries ----
entries = []
for root, dirs, files in os.walk(EPISODIC):
    if "digests" in dirs:
        dirs.remove("digests")
    for fn in files:
        if not fn.endswith(".md") or fn == "README.md":
            continue
        p = os.path.join(root, fn)
        try:
            with open(p) as f:
                content = f.read()
        except Exception as e:
            print(f"READ FAIL: {p}: {e}", file=sys.stderr)
            continue
        fm, body = parse_frontmatter(content)
        if fm is None:
            entries.append({"path": p, "fm": None, "body": body, "date": None, "tags": [], "promoted": False})
            continue
        tags = extract_list(fm, "tags")
        date_val = parse_date(extract_field(fm, "date"))
        promoted = extract_promoted(fm)
        entries.append({"path": p, "fm": fm, "body": body, "date": date_val, "tags": tags, "promoted": promoted})

print(f"Scanned {len(entries)} episodic files")

# ---- score co-occurrences ----
in_window = [e for e in entries if e["date"] and WINDOW_START <= e["date"] <= TODAY]
print(f"In-window entries ({WINDOW_START} to {TODAY}): {len(in_window)}")

no_tags = 0
no_date = 0
files_with_tags = 0
score_distribution = {}

for e in entries:
    if not e["tags"]:
        no_tags += 1
        score = 0
    else:
        files_with_tags += 1
        e_tags = set(e["tags"])
        count = 0
        for other in in_window:
            if other is e:
                continue
            if not other["tags"]:
                continue
            overlap = e_tags & set(other["tags"])
            if len(overlap) >= 2:
                count += 1
                if count >= 10:
                    break
        score = min(count, 10)
    if not e["date"]:
        no_date += 1
    e["score"] = score
    score_distribution[score] = score_distribution.get(score, 0) + 1

promoted_preserved = sum(1 for e in entries if e["promoted"])

# ---- write updated frontmatter ----
score_updates = 0
write_errors = []
for e in entries:
    if e["fm"] is None:
        continue
    new_fm = rewrite_salience_block(e["fm"], e["score"], e["promoted"])
    try:
        with open(e["path"], "w") as f:
            f.write(f"---\n{new_fm}\n---\n{e['body']}")
        score_updates += 1
    except Exception as ex:
        write_errors.append((e["path"], str(ex)))

print(f"Score updates: {score_updates}")
print(f"No tags: {no_tags}")
print(f"No date: {no_date}")
print(f"Files with tags: {files_with_tags}")
print(f"Promoted preserved: {promoted_preserved}")
print(f"Score distribution: {dict(sorted(score_distribution.items()))}")
if write_errors:
    print(f"WRITE ERRORS: {len(write_errors)}")
    for p, err in write_errors[:10]:
        print(f"  {p}: {err}")

result = {
    "episodic_scanned": len(entries),
    "score_updates": score_updates,
    "no_tags": no_tags,
    "no_date": no_date,
    "files_with_tags": files_with_tags,
    "in_window_count": len(in_window),
    "score_distribution": dict(sorted(score_distribution.items())),
    "window_start": WINDOW_START.isoformat(),
    "window_end": TODAY.isoformat(),
    "promoted_preserved": promoted_preserved,
    "write_errors": len(write_errors),
}
with open("/Users/davidohara/develop/jarvis/outputs/dream_cycle_step02_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("\nWrote result to outputs/dream_cycle_step02_result.json")

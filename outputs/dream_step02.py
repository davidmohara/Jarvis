#!/usr/bin/env python3
"""Dream cycle step-02: salience scoring by co-occurrence."""
import os, re, datetime, json
from collections import defaultdict

ROOT = "/Users/davidohara/develop/jarvis"
EPISODIC = f"{ROOT}/memory/episodic"
TODAY = datetime.date(2026, 7, 6)
WINDOW_START = TODAY - datetime.timedelta(days=30)  # 2026-06-06

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, None, text
    fm_text = parts[1]
    body = parts[2]
    return "---", fm_text, body

def parse_tags(fm_text):
    # Inline form
    m = re.search(r"^tags:\s*\[([^\]]*)\]", fm_text, re.MULTILINE)
    if m:
        return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
    # Block form (accept both indented and unindented `-` lines)
    m = re.search(r"^tags:\s*\n((?:[ \t]*-[ \t]+.+\n?)+)", fm_text, re.MULTILINE)
    if m:
        return [ln.strip().lstrip("-").strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]
    return []

def parse_date(fm_text):
    m = re.search(r"^date:\s*(\S+)", fm_text, re.MULTILINE)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1).strip()[:10])
        except Exception:
            pass
    m = re.search(r"^created:\s*(\S+)", fm_text, re.MULTILINE)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1).strip()[:10])
        except Exception:
            pass
    return None

def walk_episodic():
    entries = []
    for dirpath, dirnames, filenames in os.walk(EPISODIC):
        # Skip digests
        if "digests" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            if fn == "README.md":
                continue
            entries.append(os.path.join(dirpath, fn))
    return entries

files = walk_episodic()
data = []
no_tags = []
no_date = []

for path in files:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        continue
    _, fm_text, body = parse_frontmatter(raw)
    if fm_text is None:
        no_tags.append(path)
        no_date.append(path)
        data.append({"path": path, "tags": set(), "date": None, "raw": raw, "fm_text": None, "body": None})
        continue
    tags = set(parse_tags(fm_text))
    date = parse_date(path.split(os.sep)[-1])  # Fallback: filename
    parsed_date = parse_date(fm_text)
    if parsed_date is None:
        # Try filename prefix
        base = os.path.basename(path)
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", base)
        if m:
            try:
                parsed_date = datetime.date.fromisoformat(m.group(1))
            except Exception:
                pass
    if not tags:
        no_tags.append(path)
    if parsed_date is None:
        no_date.append(path)
    data.append({
        "path": path,
        "tags": tags,
        "date": parsed_date,
        "raw": raw,
        "fm_text": fm_text,
        "body": body
    })

# Compute co-occurrence
in_window = [d for d in data if d["date"] and WINDOW_START <= d["date"] <= TODAY]
in_window_count = len(in_window)

score_dist = defaultdict(int)
for entry in data:
    if not entry["tags"]:
        score = 0
    else:
        count = 0
        for other in in_window:
            if other["path"] == entry["path"]:
                continue
            if len(entry["tags"] & other["tags"]) >= 2:
                count += 1
                if count >= 10:
                    break
        score = min(count, 10)
    entry["score"] = score
    score_dist[score] += 1

# Write updated frontmatter
updated = 0
preserved_promoted = 0
for entry in data:
    if entry["fm_text"] is None:
        # Skip files with no frontmatter
        continue
    fm_text = entry["fm_text"]
    score = entry["score"]

    # Remove existing salience block
    lines = fm_text.splitlines()
    new_lines = []
    i = 0
    promoted_flag = None
    while i < len(lines):
        line = lines[i]
        if re.match(r"^salience:\s*$", line):
            # skip this and following indented lines
            j = i + 1
            while j < len(lines):
                if re.match(r"^\s+", lines[j]) or re.match(r"^\s*$", lines[j]):
                    # capture promoted flag
                    m = re.match(r"^\s+promoted:\s*(\S+)", lines[j])
                    if m:
                        promoted_flag = m.group(1).strip()
                    j += 1
                else:
                    break
            i = j
            continue
        # Orphan promoted line
        if re.match(r"^\s+promoted:\s*(\S+)", line):
            m = re.match(r"^\s+promoted:\s*(\S+)", line)
            promoted_flag = m.group(1).strip()
            i += 1
            continue
        new_lines.append(line)
        i += 1

    # Trim trailing blank lines
    while new_lines and not new_lines[-1].strip():
        new_lines.pop()

    # Append clean salience block
    new_lines.append("salience:")
    new_lines.append(f"  score: {score}")
    new_lines.append(f"  last_scored: {TODAY.isoformat()}")
    new_lines.append(f"  last-promoted-check: {TODAY.isoformat()}")
    if promoted_flag == "true":
        new_lines.append("  promoted: true")
        preserved_promoted += 1

    new_fm = "\n".join(new_lines)
    # Reconstruct
    new_content = f"---{new_fm}\n---{entry['body']}"

    try:
        with open(entry["path"], "w", encoding="utf-8") as f:
            f.write(new_content)
        updated += 1
    except Exception as e:
        pass

# Report
result = {
    "episodic_scanned": len(data),
    "score_updates": updated,
    "no_tags": len(no_tags),
    "no_date": len(no_date),
    "files_with_tags": len(data) - len(no_tags),
    "in_window_count": in_window_count,
    "score_distribution": ", ".join(f"{k}:{v}" for k, v in sorted(score_dist.items())),
    "window_start": WINDOW_START.isoformat(),
    "window_end": TODAY.isoformat(),
    "promoted_preserved": preserved_promoted,
}
print(json.dumps(result, indent=2))

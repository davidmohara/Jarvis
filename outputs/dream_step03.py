#!/usr/bin/env python3
"""Dream cycle step-03: semantic promotion."""
import os, re, datetime, json, glob
from collections import defaultdict

ROOT = "/Users/davidohara/develop/jarvis"
EPISODIC = f"{ROOT}/memory/episodic"
SEMANTIC = f"{ROOT}/memory/semantic"
ERROR_ENTRIES = f"{ROOT}/systems/error-tracking/entries"
LESSONS = f"{ROOT}/memory/LESSONS.md"
TODAY = datetime.date(2026, 7, 6)

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]

def parse_tags(fm_text):
    m = re.search(r"^tags:\s*\[([^\]]*)\]", fm_text, re.MULTILINE)
    if m:
        return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
    m = re.search(r"^tags:\s*\n((?:[ \t]*-[ \t]+.+\n?)+)", fm_text, re.MULTILINE)
    if m:
        return [ln.strip().lstrip("-").strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]
    return []

def parse_salience(fm_text):
    score = 0
    promoted = False
    last_check = None
    m = re.search(r"^salience:\s*\n((?:\s+.+\n?)+)", fm_text, re.MULTILINE)
    if m:
        block = m.group(1)
        m2 = re.search(r"^\s+score:\s*(\d+)", block, re.MULTILINE)
        if m2:
            score = int(m2.group(1))
        m2 = re.search(r"^\s+promoted:\s*(\S+)", block, re.MULTILINE)
        if m2:
            promoted = m2.group(1).strip().lower() == "true"
        m2 = re.search(r"^\s+last-promoted-check:\s*(\S+)", block, re.MULTILINE)
        if m2:
            last_check = m2.group(1).strip()
    return score, promoted, last_check

def parse_related_people(fm_text):
    m = re.search(r"^related_people:\s*\n((?:[ \t]*-[ \t]+.+\n?)+)", fm_text, re.MULTILINE)
    if m:
        return [ln.strip().lstrip("-").strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]
    return []

def walk_episodic():
    entries = []
    for dirpath, dirnames, filenames in os.walk(EPISODIC):
        if "digests" in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if not fn.endswith(".md") or fn == "README.md":
                continue
            entries.append(os.path.join(dirpath, fn))
    return entries

# ============ Phase A: find candidates ============
candidates = []
all_files = {}  # path -> {tags, promoted, score, fm_text, body, related}

for path in walk_episodic():
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        continue
    fm_text, body = parse_frontmatter(raw)
    if fm_text is None:
        continue
    tags = parse_tags(fm_text)
    score, promoted, last_check = parse_salience(fm_text)
    related = parse_related_people(fm_text)
    all_files[path] = {
        "tags": tags,
        "promoted": promoted,
        "score": score,
        "last_check": last_check,
        "fm_text": fm_text,
        "body": body,
        "raw": raw,
        "related": related,
    }
    if score >= 3 and not promoted and last_check == TODAY.isoformat():
        candidates.append(path)

# ============ Group into clusters by tag ============
# Domain classification is TAG-IDENTITY based, not people-based (per 2026-07-05 fix)
RELATIONSHIP_TAGS = {"one-texas", "utb-board", "alice-mburu", "kevin-graham", "ypo"}
PATTERN_TAGS = {"error-patterns", "lessons", "semantic-promotion", "dream-cycle", "dream-summary", "self-correction", "frontmatter-repair", "cleanup"}
DOMAIN_KNOWLEDGE_TAGS = {"co-sell", "revenue", "pipeline", "leads", "cyber-training", "microsoft"}

def domain_for_tag(tag):
    if tag in RELATIONSHIP_TAGS:
        return "relationships"
    if tag in PATTERN_TAGS:
        return "pattern"
    if tag in DOMAIN_KNOWLEDGE_TAGS:
        return "domain-knowledge"
    return "operational"

# Build tag -> [candidate paths]
clusters = defaultdict(list)
for path in candidates:
    for tag in all_files[path]["tags"]:
        clusters[tag].append(path)

# ============ For each cluster, create or update semantic entry ============
def existing_semantic_for(domain, tag_slug):
    domain_dir = os.path.join(SEMANTIC, domain)
    if not os.path.isdir(domain_dir):
        return None
    # Find any file whose name contains {tag}-pattern.md
    for fn in os.listdir(domain_dir):
        if fn.endswith(f"-{tag_slug}-pattern.md") or f"-{tag_slug}-" in fn:
            return os.path.join(domain_dir, fn)
    return None

def existing_matches_tag(path, tag_slug):
    """More precise match: does file's tag match this cluster's tag?"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception:
        return False
    fm, _ = parse_frontmatter(raw)
    if not fm:
        return False
    file_tags = parse_tags(fm)
    return tag_slug in file_tags

def find_existing_semantic(domain, tag):
    """Match on filename ending exactly with -{tag}-pattern.md."""
    domain_dir = os.path.join(SEMANTIC, domain)
    if not os.path.isdir(domain_dir):
        return None
    # Prefer exact -{tag}-pattern.md suffix; fall back to older domain=='domain' files if applicable
    candidates_list = []
    for fn in os.listdir(domain_dir):
        if fn.endswith(f"-{tag}-pattern.md"):
            candidates_list.append(os.path.join(domain_dir, fn))
    if candidates_list:
        # Prefer most recent
        candidates_list.sort()
        return candidates_list[-1]
    return None

def append_evidence(existing_path, tag, source_paths):
    with open(existing_path, "r", encoding="utf-8") as f:
        raw = f.read()
    fm, body = parse_frontmatter(raw)
    if fm is None:
        return False

    # Update frontmatter last-updated + synthesized-from
    def upsert(fm_text, key, value):
        pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
        if pattern.search(fm_text):
            return pattern.sub(f"{key}: {value}", fm_text)
        return fm_text + f"\n{key}: {value}"

    fm = upsert(fm, "last-updated", TODAY.isoformat())

    # Append evidence entry
    evidence_entry = f"\n\n### {TODAY.isoformat()} — Nightly promotion\n"
    evidence_entry += f"Sources this cycle:\n"
    for sp in source_paths:
        rel = os.path.relpath(sp, ROOT)
        evidence_entry += f"- `{rel}`\n"

    # Ensure body has ## Evidence section
    if "## Evidence" in body:
        # Insert new entry after the ## Evidence header
        idx = body.find("## Evidence")
        # Find end of section (next ## or EOF)
        after = body[idx:]
        section_end = after.find("\n## ", 1)
        if section_end == -1:
            body = body + evidence_entry
        else:
            insert_at = idx + section_end
            body = body[:insert_at] + evidence_entry + body[insert_at:]
    else:
        body = body.rstrip() + f"\n\n## Evidence{evidence_entry}"

    new_content = f"---{fm}\n---{body}"
    try:
        with open(existing_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception:
        return False

def create_semantic(domain, tag, source_paths):
    domain_dir = os.path.join(SEMANTIC, domain)
    os.makedirs(domain_dir, exist_ok=True)
    fname = f"{TODAY.isoformat()}-{tag}-pattern.md"
    path = os.path.join(domain_dir, fname)

    frontmatter = f"""---
type: semantic-pattern
subject: "{tag} pattern"
tag: {tag}
domain: {domain}
confidence: low
created: {TODAY.isoformat()}
last-updated: {TODAY.isoformat()}
synthesized-from: {len(source_paths)} episodic entries
tags:
  - {tag}
---
"""
    body = f"\n# {tag.replace('-', ' ').title()} Pattern\n\n"
    body += f"## Pattern Summary\n\nSynthesized from {len(source_paths)} episodic entries sharing the `{tag}` tag.\n\n"
    body += f"## Evidence\n\n### {TODAY.isoformat()} — Initial synthesis\n"
    body += "Sources:\n"
    for sp in source_paths:
        rel = os.path.relpath(sp, ROOT)
        body += f"- `{rel}`\n"
    body += f"\n## Implications\n\nInitial pattern; observations will be added as more entries with this tag are promoted.\n"

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter + body)
        return path
    except Exception:
        return None

def mark_promoted(path):
    entry = all_files[path]
    fm = entry["fm_text"]
    # Update salience.promoted: true
    # Find salience block
    m = re.search(r"^salience:\s*\n((?:\s+.+\n?)+)", fm, re.MULTILINE)
    if not m:
        return False
    block = m.group(1)
    if re.search(r"^\s+promoted:", block, re.MULTILINE):
        new_block = re.sub(r"^(\s+promoted:)\s*\S+", r"\1 true", block, count=1, flags=re.MULTILINE)
    else:
        new_block = block.rstrip("\n") + "\n  promoted: true\n"
    new_fm = fm.replace(block, new_block)
    new_content = f"---{new_fm}\n---{entry['body']}"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception:
        return False

# Process clusters
result = {
    "candidates_count": len(candidates),
    "clusters_found": 0,
    "semantic_created": 0,
    "semantic_updated": 0,
    "promoted_entries": 0,
    "cluster_actions": [],
}

processed_files = set()
for tag, paths in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
    domain = domain_for_tag(tag)
    existing = find_existing_semantic(domain, tag)
    if existing:
        ok = append_evidence(existing, tag, paths)
        if ok:
            result["semantic_updated"] += 1
            action = "update"
        else:
            action = "update-failed"
    else:
        created = create_semantic(domain, tag, paths)
        if created:
            result["semantic_created"] += 1
            action = "create"
        else:
            action = "create-failed"

    result["clusters_found"] += 1
    result["cluster_actions"].append({
        "tag": tag,
        "domain": domain,
        "size": len(paths),
        "action": action,
    })
    for p in paths:
        processed_files.add(p)

# Mark promoted on all candidate source files
for path in processed_files:
    if mark_promoted(path):
        result["promoted_entries"] += 1

# ============ Phase B: Error pattern check ============
error_files = glob.glob(f"{ERROR_ENTRIES}/*.json")
category_counts = defaultdict(int)
category_examples = defaultdict(list)
category_fm_modes = defaultdict(lambda: defaultdict(int))

cutoff = TODAY - datetime.timedelta(days=30)
for ef in error_files:
    try:
        with open(ef, "r", encoding="utf-8") as f:
            entry = json.load(f)
    except Exception:
        continue
    # Get date
    ts = entry.get("timestamp") or entry.get("occurred_at") or entry.get("date") or ""
    try:
        dt = datetime.date.fromisoformat(ts[:10])
    except Exception:
        # Try to extract from id: err-YYYYMMDDT...
        m = re.search(r"err-(\d{4})(\d{2})(\d{2})T", entry.get("id", ""))
        if m:
            dt = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        else:
            continue
    if dt < cutoff:
        continue
    cat = entry.get("category", "unknown")
    fm_mode = entry.get("failure_mode", "unknown")
    category_counts[cat] += 1
    category_fm_modes[cat][fm_mode] += 1
    category_examples[cat].append(entry.get("id", ""))

result["error_total_30d"] = sum(category_counts.values())
result["error_categories_30d"] = ", ".join(
    f"{k}:{v}" for k, v in sorted(category_counts.items(), key=lambda kv: -kv[1])
)

# Read LESSONS.md
try:
    with open(LESSONS, "r", encoding="utf-8") as f:
        lessons_text = f.read()
except Exception:
    lessons_text = ""

lessons_appended = 0
qualifying = [(cat, cnt) for cat, cnt in category_counts.items() if cnt >= 3]

# Check if the top failure mode for each category is already documented
for cat, cnt in qualifying:
    # Find dominant failure_mode
    fm_modes = category_fm_modes[cat]
    dominant_fm = max(fm_modes.items(), key=lambda kv: kv[1])[0] if fm_modes else "unknown"
    marker = f"Marker: {cat}/{dominant_fm}"
    # Check multiple markers: canonical Marker line or Category+Pattern combo
    already = (
        marker in lessons_text
        or (f"Category: {cat}" in lessons_text and f"Pattern: {dominant_fm}" in lessons_text)
        or (f"category: {cat}" in lessons_text and dominant_fm in lessons_text)
    )
    if not already:
        title = f"{cat.replace('-', ' ').title()} — {dominant_fm}"
        entry_text = f"\n\n## {TODAY.isoformat()} — {title}\n"
        entry_text += f"Detected: {cnt} occurrences over 30 days\n"
        entry_text += f"Category: {cat}\n"
        entry_text += f"Pattern: {dominant_fm}\n"
        entry_text += f"Marker: {cat}/{dominant_fm}\n"
        entry_text += f"Fix: Review recurring {cat}/{dominant_fm} errors; systemic fix required.\n"
        entry_text += f"Status: active\n"
        with open(LESSONS, "a", encoding="utf-8") as f:
            f.write(entry_text)
        lessons_appended += 1

result["lessons_appended"] = lessons_appended
result["qualifying_categories"] = [(k, v) for k, v in qualifying]

print(json.dumps(result, indent=2, default=str))

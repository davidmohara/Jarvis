#!/usr/bin/env python3
"""Dream Cycle step-03: semantic promotion + error pattern check.

Learnings applied:
- domain_for_tag classifies by TAG identity, not by related_people presence
  (per err-20260704T081843-WZH7M2 recovery)
- Consolidate onto existing semantic entries via tag-slug match, not date-slug
- All source episodic files receive salience.promoted:true on cluster contribution
"""
import os
import re
import json
import glob
import datetime
from collections import defaultdict

ROOT = "/Users/davidohara/develop/jarvis"
EPISODIC = os.path.join(ROOT, "memory/episodic")
SEMANTIC = os.path.join(ROOT, "memory/semantic")
ERROR_ENTRIES = os.path.join(ROOT, "systems/error-tracking/entries")
LESSONS = os.path.join(ROOT, "memory/LESSONS.md")

TODAY = datetime.date(2026, 7, 5)

# ---- Domain classification (tag-based; NEVER related_people-based) ----
RELATIONSHIPS_TAGS = {
    # only tags that literally name a person or account
    # deliberate: kept small; err-20260704 taught us to bias toward operational
}
DOMAIN_KNOWLEDGE_TAGS = {
    "one-texas", "ypo", "glc-chicago", "cabo", "utb-board", "gold-forum",
    "google-next", "drc-workshop", "make-a-wish",
}
PATTERN_TAGS = {
    "dream-cycle", "semantic-promotion", "error-patterns", "lessons",
    "score-inflation", "memory-pipeline", "memory-system",
}

def domain_for_tag(tag):
    if tag in RELATIONSHIPS_TAGS:
        return "relationships"
    if tag in DOMAIN_KNOWLEDGE_TAGS:
        return "domain-knowledge"
    if tag in PATTERN_TAGS:
        return "pattern"
    return "operational"

# ---- Frontmatter helpers ----
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
    m = re.search(rf"^{re.escape(name)}\s*:\s*\[(.+?)\]", fm, re.MULTILINE)
    if m:
        return [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    m = re.search(rf"^{re.escape(name)}\s*:\s*\n((?:\s*-\s*.+\n?)+)", fm, re.MULTILINE)
    if m:
        return [ln.strip().lstrip("- ").strip().strip("'\"") for ln in m.group(1).splitlines() if ln.strip()]
    return []

def extract_salience(fm):
    m = re.search(r"^salience\s*:\s*\n((?:\s{2,}\S.*\n?)+)", fm, re.MULTILINE)
    if not m:
        return None
    block = m.group(1)
    out = {}
    for k in ["score", "last_scored", "last-promoted-check", "promoted"]:
        mm = re.search(rf"^\s+{k}\s*:\s*(\S+)", block, re.MULTILINE)
        if mm:
            out[k] = mm.group(1).strip()
    return out

def set_salience_promoted(fm, promoted=True):
    """Set salience.promoted to given value."""
    def repl(match):
        block = match.group(1)
        if re.search(r"^\s+promoted\s*:", block, re.MULTILINE):
            block = re.sub(r"^(\s+promoted\s*:).*$", rf"\1 {'true' if promoted else 'false'}", block, flags=re.MULTILINE)
        else:
            block = block.rstrip("\n") + f"\n  promoted: {'true' if promoted else 'false'}\n"
        return "salience:\n" + block
    return re.sub(r"^salience\s*:\s*\n((?:\s{2,}\S.*\n?)+)", repl, fm, flags=re.MULTILINE)

# ---- Load all episodic entries ----
entries = []
for root, dirs, files in os.walk(EPISODIC):
    if "digests" in dirs:
        dirs.remove("digests")
    for fn in files:
        if not fn.endswith(".md") or fn == "README.md":
            continue
        p = os.path.join(root, fn)
        with open(p) as f:
            content = f.read()
        fm, body = parse_frontmatter(content)
        if fm is None:
            continue
        tags = extract_list(fm, "tags")
        sal = extract_salience(fm) or {}
        entries.append({
            "path": p,
            "fname": fn,
            "fm": fm,
            "body": body,
            "tags": tags,
            "score": int(sal.get("score", "0") or 0),
            "promoted": (sal.get("promoted", "false") == "true"),
            "last_check": sal.get("last-promoted-check", ""),
        })

# ---- Identify candidates ----
candidates = [e for e in entries
              if e["score"] >= 3
              and not e["promoted"]
              and e["last_check"] == TODAY.isoformat()]
print(f"Candidates (score>=3, promoted=false, checked-today): {len(candidates)}")

# ---- Cluster by tag ----
clusters = defaultdict(list)
for e in candidates:
    for t in e["tags"]:
        # Skip the deliverable-type tag as a cluster (too broad on its own)
        clusters[t].append(e)

# Sort clusters by size, keep those with 2+ members
sized_clusters = sorted(
    [(tag, members) for tag, members in clusters.items() if len(members) >= 2],
    key=lambda x: -len(x[1]),
)

# Also include single-file clusters where the tag is meaningful (score>=3 already)
# but only for tags we haven't already covered via multi-file cluster
covered_tags = {tag for tag, _ in sized_clusters}
for tag, members in clusters.items():
    if tag in covered_tags:
        continue
    if len(members) == 1 and members[0]["score"] >= 3:
        sized_clusters.append((tag, members))

print(f"Total clusters (>=2 members OR single with score>=3): {len(sized_clusters)}")

# ---- Process clusters ----
def find_existing(domain, tag):
    """Find semantic file matching tag-slug in this domain, most recent first."""
    dom_dir = os.path.join(SEMANTIC, domain)
    if not os.path.exists(dom_dir):
        return None
    matches = []
    for fn in os.listdir(dom_dir):
        if not fn.endswith("-pattern.md"):
            continue
        # Extract tag-slug from filename YYYY-MM-DD-{slug}-pattern.md
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)-pattern\.md$", fn)
        if not m:
            continue
        slug = m.group(2)
        if slug == tag:
            matches.append(fn)
    if matches:
        # sort by date desc
        matches.sort(reverse=True)
        return os.path.join(dom_dir, matches[0])
    return None

semantic_created = 0
semantic_updated = 0
promoted_source_files = set()
cluster_actions = []

for tag, members in sized_clusters:
    domain = domain_for_tag(tag)
    dom_dir = os.path.join(SEMANTIC, domain)
    os.makedirs(dom_dir, exist_ok=True)
    existing = find_existing(domain, tag)
    action = "update" if existing else "create"
    size = len(members)

    if existing:
        # Append evidence
        with open(existing) as f:
            content = f.read()
        # Build new evidence lines
        new_evidence_lines = []
        for e in members:
            rel_path = os.path.relpath(e["path"], ROOT)
            date_str = extract_field(e["fm"], "date") or ""
            new_evidence_lines.append(f"- {date_str}: [{e['fname']}]({rel_path}) (score {e['score']})")
        # Insert into ## Evidence section
        if "## Evidence" in content:
            parts = re.split(r"^(## Evidence)$", content, maxsplit=1, flags=re.MULTILINE)
            if len(parts) >= 3:
                head, hdr, rest = parts[0], parts[1], parts[2]
                # Find next section or end
                next_hdr_match = re.search(r"^## ", rest, re.MULTILINE)
                if next_hdr_match:
                    ev_block = rest[:next_hdr_match.start()]
                    tail = rest[next_hdr_match.start():]
                else:
                    ev_block = rest
                    tail = ""
                addition = "\n\n### " + TODAY.isoformat() + " dream-cycle promotion\n" + "\n".join(new_evidence_lines) + "\n"
                new_content = head + hdr + ev_block.rstrip("\n") + addition + ("\n" + tail if tail else "\n")
            else:
                new_content = content + "\n\n## Evidence\n" + "\n".join(new_evidence_lines) + "\n"
        else:
            new_content = content + "\n\n## Evidence\n" + "\n".join(new_evidence_lines) + "\n"

        # Update last-updated in frontmatter
        cfm, cbody = parse_frontmatter(new_content)
        if cfm is not None:
            if re.search(r"^last-updated\s*:", cfm, re.MULTILINE):
                cfm = re.sub(r"^last-updated\s*:.*$", f"last-updated: {TODAY.isoformat()}", cfm, flags=re.MULTILINE)
            else:
                cfm += f"\nlast-updated: {TODAY.isoformat()}"
            new_content = f"---\n{cfm}\n---\n{cbody}"

        with open(existing, "w") as f:
            f.write(new_content)
        semantic_updated += 1
    else:
        # Create new
        new_path = os.path.join(dom_dir, f"{TODAY.isoformat()}-{tag}-pattern.md")
        evidence_lines = []
        for e in members:
            rel_path = os.path.relpath(e["path"], ROOT)
            date_str = extract_field(e["fm"], "date") or ""
            evidence_lines.append(f"- {date_str}: [{e['fname']}]({rel_path}) (score {e['score']})")
        content = f"""---
type: semantic-pattern
tag: {tag}
domain: {domain}
confidence: low
created: {TODAY.isoformat()}
last-updated: {TODAY.isoformat()}
synthesized-from: dream-cycle-{TODAY.isoformat()}
source-count: {size}
---

# Pattern: {tag}

## Pattern Summary

Recurring signal around `{tag}` in episodic memory. Promoted by dream-cycle on {TODAY.isoformat()} after {size} co-occurring entries reached salience threshold.

## Evidence

### {TODAY.isoformat()} dream-cycle promotion
""" + "\n".join(evidence_lines) + """

## Implications

- Pattern is emerging; observe for consolidation over next 2–3 cycles.
- If pattern persists, promote confidence to medium.
"""
        with open(new_path, "w") as f:
            f.write(content)
        semantic_created += 1

    # Mark source episodic files as promoted
    for e in members:
        try:
            new_fm = set_salience_promoted(e["fm"], True)
            with open(e["path"], "w") as f:
                f.write(f"---\n{new_fm}\n---\n{e['body']}")
            promoted_source_files.add(e["path"])
            e["fm"] = new_fm  # for further loops
        except Exception as ex:
            print(f"  PROMOTE FAIL: {e['path']}: {ex}")

    cluster_actions.append({"tag": tag, "domain": domain, "size": size, "action": action})

print(f"Semantic created: {semantic_created}")
print(f"Semantic updated: {semantic_updated}")
print(f"Promoted source files: {len(promoted_source_files)}")

# ---- Phase B: Error pattern check ----
error_files = glob.glob(os.path.join(ERROR_ENTRIES, "*.json"))
error_cutoff = TODAY - datetime.timedelta(days=30)
category_counts = defaultdict(int)
category_failure_counts = defaultdict(int)
error_total = 0

for ef in error_files:
    try:
        with open(ef) as f:
            data = json.load(f)
    except Exception:
        continue
    # Parse timestamp from id field: err-YYYYMMDDTHHMMSS-XXXXXX
    fid = data.get("id") or os.path.basename(ef).replace(".json", "")
    m = re.match(r"err-(\d{8})T", fid)
    if not m:
        continue
    try:
        d = datetime.datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        continue
    if d < error_cutoff or d > TODAY:
        continue
    error_total += 1
    cat = data.get("category", "unknown")
    fm_field = data.get("failure_mode", "unknown")
    category_counts[cat] += 1
    category_failure_counts[f"{cat}/{fm_field}"] += 1

top_categories = sorted(category_counts.items(), key=lambda x: -x[1])
error_cat_str = ", ".join(f"{c}:{n}" for c, n in top_categories[:10])
print(f"Error total (30d): {error_total}")
print(f"Top categories: {error_cat_str}")

# Threshold check on category+failure_mode combos
threshold_combos = [(k, v) for k, v in category_failure_counts.items() if v >= 3]
print(f"Threshold-breaching combos: {len(threshold_combos)}")

# Append lessons if not already there
lessons_appended = 0
lessons_note_parts = []
if os.path.exists(LESSONS):
    with open(LESSONS) as f:
        lessons_content = f.read()
else:
    lessons_content = "# Lessons\n\n"

for combo, count in threshold_combos:
    cat, fm_mode = combo.split("/", 1)
    # Check if already present (by category + failure_mode combo)
    if f"Category: {cat}" in lessons_content and f"Failure mode: {fm_mode}" in lessons_content:
        continue
    # Try broader check
    marker = f"{cat}/{fm_mode}"
    if marker in lessons_content:
        continue
    title = f"{cat.replace('-', ' ').title()} — {fm_mode.replace('-', ' ')}"
    entry = f"""
## {TODAY.isoformat()} — {title}
Detected: {count} occurrences over 30 days
Category: {cat}
Failure mode: {fm_mode}
Marker: {marker}
Pattern: Recurring {cat} error mode: {fm_mode}
Fix: Investigate common triggers; propose systemic fix via Rigby error analysis.
Status: active
"""
    lessons_content += entry
    lessons_appended += 1
    lessons_note_parts.append(f"{cat}/{fm_mode}({count})")

if lessons_appended > 0:
    with open(LESSONS, "w") as f:
        f.write(lessons_content)

print(f"Lessons appended: {lessons_appended}")

result = {
    "candidates_count": len(candidates),
    "clusters_found": len(sized_clusters),
    "semantic_created": semantic_created,
    "semantic_updated": semantic_updated,
    "promoted_entries": len(promoted_source_files),
    "cluster_actions": cluster_actions,
    "error_total_30d": error_total,
    "error_categories_30d": error_cat_str,
    "lessons_appended": lessons_appended,
    "lessons_note": ("Appended: " + ", ".join(lessons_note_parts)) if lessons_appended else "All threshold-breaching combos already present in LESSONS.md; no new appends.",
}
with open("/Users/davidohara/develop/jarvis/outputs/dream_cycle_step03_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("\nWrote result to outputs/dream_cycle_step03_result.json")

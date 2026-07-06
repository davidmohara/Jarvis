#!/usr/bin/env python3
"""Dream cycle step-01: working memory cleanup with heuristic enrichment."""
import os, re, sys, datetime, json, shutil, pathlib

ROOT = "/Users/davidohara/develop/jarvis"
WORKING = f"{ROOT}/memory/working"
EPISODIC = f"{ROOT}/memory/episodic"
TODAY = datetime.date(2026, 7, 6)
NOW = datetime.datetime(2026, 7, 6, 3, 9, 35)

results = {
    "archived": [],
    "deleted": [],
    "skipped_not_expired": [],
    "skipped_no_status": [],
    "skipped_unparseable": [],
    "skipped_already_archived": [],
    "stranded": [],
    "enrichment_no_date": [],
}

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    fm_text = parts[1].strip()
    body = parts[2].lstrip("\n")
    return fm_text, body

def parse_expires(fm_text):
    m = re.search(r"^expires:\s*(.+?)$", fm_text, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    # Try datetime (ISO)
    try:
        # Strip TZ if present
        stripped = re.sub(r"[+-]\d{2}:\d{2}$", "", val)
        if "T" in stripped:
            return datetime.datetime.fromisoformat(stripped)
        # Date only
        return datetime.date.fromisoformat(stripped)
    except Exception:
        return None

def parse_status(fm_text):
    m = re.search(r"^status:\s*(\S+)", fm_text, re.MULTILINE)
    return m.group(1).strip() if m else None

def is_expired(exp):
    if isinstance(exp, datetime.datetime):
        return exp < NOW
    if isinstance(exp, datetime.date):
        return exp < TODAY
    return False

def heuristic_enrich(fname, fm_text, body):
    # Date: from `created` field or filename prefix
    date_val = None
    m = re.search(r"^created:\s*(\S+)", fm_text, re.MULTILINE)
    if m:
        val = m.group(1).strip()
        try:
            date_val = val[:10]  # YYYY-MM-DD
        except Exception:
            pass
    if not date_val:
        fm = re.match(r"^(\d{4}-\d{2}-\d{2})", fname)
        if fm:
            date_val = fm.group(1)
    if not date_val:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
        if m:
            date_val = m.group(1)

    # agent-source
    m = re.search(r"^agent-source:\s*(\S+)", fm_text, re.MULTILINE)
    agent = m.group(1).strip() if m else None

    # Existing tags in frontmatter (to preserve intent)
    existing_tags = []
    tag_line = re.search(r"^tags:\s*\[([^\]]*)\]", fm_text, re.MULTILINE)
    if tag_line:
        existing_tags = [t.strip().strip("'\"") for t in tag_line.group(1).split(",") if t.strip()]
    else:
        # YAML block form
        block = re.search(r"^tags:\s*\n((?:\s+-\s+.+\n?)+)", fm_text, re.MULTILINE)
        if block:
            existing_tags = [ln.strip().lstrip("-").strip() for ln in block.group(1).splitlines() if ln.strip()]

    text_lower = (fm_text + "\n" + body).lower()

    # Deliverable type first
    tags = []
    type_map = [
        ("morning-briefing", ["morning briefing", "morning-briefing", "master morning"]),
        ("daily-review", ["daily review", "daily-review"]),
        ("dream-summary", ["dream summary", "dream-summary", "dream cycle"]),
        ("session-wrap", ["session wrap", "session-wrap", "session working memory"]),
        ("pipeline-review", ["pipeline review"]),
        ("system-eval", ["system eval", "system-eval", "eval harness"]),
        ("shutdown-cleanup", ["shutdown cleanup", "shutdown-cleanup"]),
        ("briefing", ["briefing"]),
    ]
    for tag, patterns in type_map:
        if any(p in text_lower for p in patterns):
            tags.append(tag)
            break

    # Agent
    if agent:
        tags.append(agent)

    # Preserve existing tag intent
    for t in existing_tags:
        if t and t not in tags:
            tags.append(t)

    # Additional keywords
    keyword_tags = {
        "calendar": ["calendar", "outlook"],
        "omnifocus": ["omnifocus"],
        "email": ["email", "inbox"],
        "leads": ["lead ", "leads"],
        "overdue-tasks": ["overdue"],
        "rock4": ["rock 4", "rock4"],
        "quinn": ["quinn"],
        "plaud": ["plaud"],
        "clay": ["clay"],
        "slack": ["slack"],
        "eval": ["eval", "assertion", "grading"],
        "self-correction": ["self-correction", "self-detected", "corrected"],
        "semantic-promotion": ["semantic promotion", "semantic-promotion"],
        "dream-cycle": ["dream cycle", "dream-cycle"],
    }
    for tag, patterns in keyword_tags.items():
        if any(p in text_lower for p in patterns):
            if tag not in tags:
                tags.append(tag)

    tags = tags[:10]
    if len(tags) < 3:
        while len(tags) < 3:
            filler = ["working-archive", "jarvis", "session"]
            for f in filler:
                if f not in tags:
                    tags.append(f)
                    break
            else:
                break

    # related_people (heuristic — look for common names in body)
    people = []
    people_patterns = {
        "david-ohara": ["david o'hara", "david ohara", "davidohara"],
        "alice-mburu": ["alice mburu"],
        "kevin-graham": ["kevin graham"],
        "matt-yasar": ["matt yasar"],
        "ari-jacoby": ["ari jacoby"],
        "kevin-baker": ["kevin baker"],
        "nick-koury": ["nick koury"],
        "maha-abbey": ["maha abbey"],
        "scott-belcher": ["belcher"],
        "susie-ohara": ["susie"],
        "ehren-seim": ["ehren seim"],
    }
    for slug, patterns in people_patterns.items():
        if any(p in text_lower for p in patterns):
            people.append(slug)

    return date_val, tags, people

def build_new_frontmatter(fm_text, date_val, tags, people, salience_score=0):
    # Strip existing status/type/tags/related_people/salience/date/source_file
    lines = fm_text.splitlines()
    result = []
    skip_block = False
    for i, line in enumerate(lines):
        # Skip block-form tags: header, capture indented block
        if re.match(r"^tags:\s*$", line):
            skip_block = True
            continue
        if skip_block:
            if re.match(r"^\s+-", line) or re.match(r"^\s*$", line):
                continue
            else:
                skip_block = False
        if re.match(r"^tags:\s*\[", line):
            continue
        # Skip related_people block
        if re.match(r"^related_people:\s*$", line):
            skip_block = True
            continue
        if re.match(r"^related_people:\s*\[", line):
            continue
        if re.match(r"^salience:\s*$", line):
            skip_block = True
            continue
        if line.startswith("  score:") or line.startswith("  last_scored:") or line.startswith("  last-promoted-check:") or line.startswith("  promoted:"):
            continue
        if re.match(r"^(status|type|date|source_file):", line):
            continue
        result.append(line)

    # Now append the new/updated fields
    result.append("type: working-archive")
    result.append("status: archived")
    if date_val:
        result.append(f"date: {date_val}")
    # source file will be added by caller
    return "\n".join(result)

def process_file(fname):
    path = os.path.join(WORKING, fname)
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    fm_text, body = parse_frontmatter(raw)
    if fm_text is None:
        results["skipped_unparseable"].append(fname)
        return

    exp = parse_expires(fm_text)
    if exp is None:
        results["skipped_unparseable"].append(fname)
        return

    status = parse_status(fm_text)
    if status == "archived":
        results["skipped_already_archived"].append(fname)
        return
    if status is None:
        results["skipped_no_status"].append(fname)
        return
    if status != "active":
        results["skipped_not_expired"].append(fname)  # not active — treat as skip
        return
    if not is_expired(exp):
        results["skipped_not_expired"].append(fname)
        return

    # Non-trivial check
    body_lines = [l for l in body.splitlines() if l.strip() and not l.strip().startswith("#")]
    trivial = len(body_lines) < 3

    if trivial:
        # Mutate to archived, delete
        new_fm = re.sub(r"^status:\s*\S+", "status: archived", fm_text, flags=re.MULTILINE)
        new_content = f"---\n{new_fm}\n---\n{body}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        try:
            os.remove(path)
            results["deleted"].append(fname)
        except Exception as e:
            results["stranded"].append({"file": fname, "reason": f"delete failed: {e}"})
        return

    # Enrich + mutate + move
    date_val, tags, people = heuristic_enrich(fname, fm_text, body)
    if not date_val:
        results["enrichment_no_date"].append(fname)

    new_fm = build_new_frontmatter(fm_text, date_val, tags, people)
    new_fm += f"\nsource_file: memory/working/{fname}"
    new_fm += "\ntags:"
    for t in tags:
        new_fm += f"\n  - {t}"
    new_fm += "\nrelated_people:"
    for p in people:
        new_fm += f"\n  - {p}"
    new_fm += "\nsalience:"
    new_fm += "\n  score: 0"

    new_content = f"---\n{new_fm}\n---\n{body}"
    # Write to source first
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # mv to episodic
    dest = os.path.join(EPISODIC, fname)
    try:
        os.rename(path, dest)
        results["archived"].append(fname)
    except Exception as e:
        results["stranded"].append({"file": fname, "reason": f"mv failed: {e}"})

# Main
files = sorted([f for f in os.listdir(WORKING) if f != "README.md" and not f.startswith(".")])
for f in files:
    if os.path.isfile(os.path.join(WORKING, f)):
        try:
            process_file(f)
        except Exception as e:
            results["stranded"].append({"file": f, "reason": f"exception: {e}"})

print(json.dumps(results, indent=2))

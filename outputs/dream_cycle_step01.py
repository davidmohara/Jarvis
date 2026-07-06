#!/usr/bin/env python3
"""Dream Cycle step-01: working memory cleanup for 2026-07-05."""
import os
import re
import sys
import datetime

ROOT = "/Users/davidohara/develop/jarvis"
WORKING = os.path.join(ROOT, "memory/working")
EPISODIC = os.path.join(ROOT, "memory/episodic")

sys.path.insert(0, os.path.join(ROOT, "systems/dream-cycle"))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "backfill", os.path.join(ROOT, "systems/dream-cycle/backfill-episodic-tags.py")
)
backfill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backfill)

TODAY = datetime.date(2026, 7, 5)
NOW = datetime.datetime(2026, 7, 5, 8, 9, 39, tzinfo=datetime.timezone.utc)

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)

def field(fm, name):
    if fm is None:
        return None
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.+?)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None

def parse_expires(val):
    """Return (is_expired, note). expires < today = expired."""
    if not val:
        return None, "no-expires-field"
    val = val.strip().strip("'\"")
    # Try full timestamp with tz first
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(val, fmt)
            if dt.tzinfo is None:
                # assume Central time (UTC-5 in July DST)
                dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
            return (dt < NOW), f"timestamp {dt.isoformat()}"
        except ValueError:
            continue
    # Try handling +/-hh:mm variant
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2}):(\d{2})$", val)
    if m:
        try:
            dt = datetime.datetime.strptime(m.group(1) + m.group(2) + m.group(3), "%Y-%m-%dT%H:%M:%S%z")
            return (dt < NOW), f"timestamp {dt.isoformat()}"
        except ValueError:
            pass
    # Date only
    try:
        d = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        return (d < TODAY), f"date {d.isoformat()}"
    except ValueError:
        pass
    return None, f"unparseable {val!r}"

def enrich(fm, body, fname):
    date_val = backfill.derive_date(fm, fname)
    tags = backfill.derive_tags(body, fname, fm)
    people = backfill.derive_people(body, fm)
    return date_val, tags, people

def mutate_and_move(path, fname, fm, body):
    """Add archive fields, write, then mv to episodic."""
    date_val, tags, people = enrich(fm, body, fname)
    source_path = f"memory/working/{fname}"

    # Remove existing enrichment fields for idempotency
    new_fm = fm
    for f in ["date", "source_file"]:
        new_fm = re.sub(rf"^{f}\s*:.*\n?", "", new_fm, flags=re.MULTILINE)
    new_fm = re.sub(r"^tags\s*:\s*(?:\n(?:\s*-\s*.+\n?)+|.+\n)", "", new_fm, flags=re.MULTILINE)
    new_fm = re.sub(r"^related_people\s*:\s*(?:\n(?:\s*-\s*.+\n?)+|\s*\n|.+\n)", "", new_fm, flags=re.MULTILINE)
    # Update status to archived; add type and salience if missing
    if re.search(r"^status\s*:", new_fm, re.MULTILINE):
        new_fm = re.sub(r"^status\s*:.*$", "status: archived", new_fm, flags=re.MULTILINE)
    else:
        new_fm += "\nstatus: archived"
    if not re.search(r"^type\s*:", new_fm, re.MULTILINE):
        new_fm += "\ntype: working-archive"
    else:
        new_fm = re.sub(r"^type\s*:.*$", "type: working-archive", new_fm, flags=re.MULTILINE)

    # Add enrichment block
    lines = []
    if date_val:
        lines.append(f"date: {date_val}")
    lines.append(f"source_file: {source_path}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    lines.append("related_people:")
    for p in people:
        lines.append(f"  - {p}")
    # Add salience block
    lines.append("salience:")
    lines.append("  score: 0")
    lines.append(f"  last_scored: {NOW.strftime('%Y-%m-%d')}")
    lines.append("  promoted: false")

    enrichment = "\n".join(lines)
    new_fm = new_fm.rstrip("\n") + "\n" + enrichment
    new_content = f"---\n{new_fm}\n---\n{body}"

    with open(path, "w") as f:
        f.write(new_content)
    dest = os.path.join(EPISODIC, fname)
    os.rename(path, dest)
    return date_val, tags, people, dest

def main():
    archived, deleted, skipped_not_expired, skipped_no_status, skipped_unparseable, skipped_already, stranded = [], [], [], [], [], [], []

    for fn in sorted(os.listdir(WORKING)):
        if fn == "README.md":
            continue
        if not fn.endswith(".md"):
            continue
        path = os.path.join(WORKING, fn)
        with open(path) as f:
            content = f.read()
        fm, body = parse_frontmatter(content)
        if fm is None:
            skipped_unparseable.append(fn)
            print(f"SKIP unparseable (no fm): {fn}")
            continue
        expires_val = field(fm, "expires")
        status_val = field(fm, "status")
        expired, note = parse_expires(expires_val)
        print(f"{fn}: expires={expires_val!r} status={status_val!r} expired={expired} note={note}")

        if expired is None:
            skipped_unparseable.append(fn)
            continue
        if status_val is None:
            skipped_no_status.append(fn)
            continue
        if status_val.strip().strip("'\"") == "archived":
            skipped_already.append(fn)
            continue
        if not expired:
            skipped_not_expired.append(fn)
            continue
        if status_val.strip().strip("'\"") != "active":
            skipped_not_expired.append(fn)
            continue

        # Non-trivial body test
        body_lines = [ln for ln in body.split("\n") if ln.strip() and not ln.strip().startswith("#")]
        trivial = len(body_lines) < 3
        if trivial:
            # Set status:archived and delete
            new_fm = re.sub(r"^status\s*:.*$", "status: archived", fm, flags=re.MULTILINE)
            with open(path, "w") as f:
                f.write(f"---\n{new_fm}\n---\n{body}")
            try:
                os.remove(path)
                deleted.append(fn)
                print(f"  → DELETED (trivial)")
            except Exception as e:
                stranded.append((fn, str(e)))
        else:
            try:
                date_val, tags, people, dest = mutate_and_move(path, fn, fm, body)
                archived.append(fn)
                print(f"  → ARCHIVED to episodic/{fn}")
                print(f"    date={date_val} tags={tags[:5]}... people={people}")
            except Exception as e:
                stranded.append((fn, str(e)))
                print(f"  → STRANDED: {e}")

    print()
    print(f"SUMMARY: archived={len(archived)} deleted={len(deleted)} skipped_not_expired={len(skipped_not_expired)} skipped_no_status={len(skipped_no_status)} skipped_unparseable={len(skipped_unparseable)} stranded={len(stranded)}")
    import json
    result = {
        "archived": archived,
        "deleted": deleted,
        "skipped_not_expired": skipped_not_expired,
        "skipped_no_status": skipped_no_status,
        "skipped_unparseable": skipped_unparseable,
        "skipped_already_archived": skipped_already,
        "stranded": stranded,
    }
    with open("/Users/davidohara/develop/jarvis/outputs/dream_cycle_step01_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\nWrote result to outputs/dream_cycle_step01_result.json")

if __name__ == "__main__":
    main()

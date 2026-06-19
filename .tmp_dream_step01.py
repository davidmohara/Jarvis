#!/usr/bin/env python3
"""Dream cycle step-01: working memory cleanup. Today 2026-06-17."""
import os, re, sys, datetime, subprocess

REPO = "/sessions/bold-elegant-allen/mnt/jarvis"
WORKING = os.path.join(REPO, "memory", "working")
EPISODIC = os.path.join(REPO, "memory", "episodic")
TODAY = datetime.datetime(2026, 6, 17, 8, 8, 44, tzinfo=datetime.timezone.utc)

# heuristic enrichment - simple tag vocab subset for working entries
TAG_KW = {
    "briefing":         [r"\bbriefing\b"],
    "morning-briefing": [r"morning briefing"],
    "daily-review":     [r"daily review"],
    "dream-summary":    [r"dream", r"dream cycle"],
    "session-wrap":     [r"session wrap"],
    "calendar":         [r"\bcalendar\b"],
    "omnifocus":        [r"omnifocus"],
    "leads":            [r"\blead"],
    "pipeline":         [r"pipeline"],
    "co-sell":          [r"co.?sell"],
    "revenue":          [r"revenue|bookings"],
    "travel":           [r"travel|flight|airport"],
    "rock1":            [r"rock ?1"],
    "rock2":            [r"rock ?2"],
    "rock3":            [r"rock ?3"],
    "rock4":            [r"rock ?4"],
    "system-maintenance":[r"git|commit|cleanup|maintenance"],
    "memory-pipeline":  [r"working memory|episodic|semantic|salience"],
    "chief":            [r"chief"],
    "chase":            [r"chase"],
    "knox":             [r"knox"],
    "harper":           [r"harper"],
    "rigby":            [r"rigby"],
    "galen":            [r"galen"],
    "quinn":            [r"quinn"],
    "shep":             [r"shep"],
    "sterling":         [r"sterling"],
}

PEOPLE_KW = [
    "alice-mburu","ehren-seim","scott-allen","brian-rabon","julli-randol",
    "sean-brown","jay-larson","david-ohara","mark-mctigue",
]


def parse_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def fm_get(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_dt(s):
    if not s:
        return None
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    return None


def derive_tags(body, agent_source):
    body_l = body.lower()
    tags = []
    for tag, pats in TAG_KW.items():
        for p in pats:
            if re.search(p, body_l):
                tags.append(tag)
                break
    if agent_source and agent_source not in tags:
        tags.insert(0, agent_source)
    # always include something useful first
    if "briefing" in tags and "briefing" != tags[0]:
        tags.remove("briefing"); tags.insert(0, "briefing")
    if not tags:
        tags = ["working", "session"]
    # dedupe preserving order, cap 10
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:10]


def derive_people(body):
    body_l = body.lower()
    out = []
    for p in PEOPLE_KW:
        if p.replace("-", " ") in body_l or p in body_l:
            out.append(p)
    return out


def body_substantive_lines(body):
    return [l for l in body.split("\n") if l.strip() and not l.strip().startswith("#")]


def main():
    archived, deleted, skipped, stranded = 0, 0, 0, 0
    skipped_already_archived = []
    skipped_unparseable = []
    skipped_not_expired = []
    stranded_list = []
    archived_files = []

    for fname in sorted(os.listdir(WORKING)):
        if fname == "README.md":
            continue
        path = os.path.join(WORKING, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_fm(text)
        if fm is None:
            skipped_unparseable.append(fname)
            skipped += 1
            continue
        expires_s = fm_get(fm, "expires")
        status = (fm_get(fm, "status") or "").strip().strip('"')
        # Skip if status already archived
        if status == "archived":
            skipped_already_archived.append(fname)
            skipped += 1
            continue
        exp = parse_dt(expires_s) if expires_s else None
        if exp is None:
            skipped_unparseable.append(fname)
            skipped += 1
            continue
        if exp >= TODAY:
            skipped_not_expired.append(fname)
            skipped += 1
            continue
        if status != "active":
            # only archive active+expired
            skipped += 1
            continue
        # Eligible: enrich and move
        substantive = body_substantive_lines(body)
        trivial = len(substantive) < 3
        agent_source = fm_get(fm, "agent-source") or fm_get(fm, "agent_source")
        if agent_source:
            agent_source = agent_source.strip().strip('"').lower()
        created = fm_get(fm, "created") or ""
        date_val = None
        m = re.match(r"(\d{4}-\d{2}-\d{2})", created)
        if m:
            date_val = m.group(1)
        else:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", fname)
            if m:
                date_val = m.group(1)

        # Build new frontmatter
        # Remove old status/type, append new
        new_fm = fm
        new_fm = re.sub(r"^status:.*$", "status: archived", new_fm, flags=re.MULTILINE)
        if not re.search(r"^status:", new_fm, re.MULTILINE):
            new_fm += "\nstatus: archived"
        new_fm = re.sub(r"^type:.*$", "type: working-archive", new_fm, flags=re.MULTILINE)
        if not re.search(r"^type:", new_fm, re.MULTILINE):
            new_fm += "\ntype: working-archive"

        if not trivial:
            tags = derive_tags(body, agent_source)
            people = derive_people(body)
            # remove any prior salience/date/source_file/tags/related_people
            for k in ["salience", "date", "source_file", "tags", "related_people"]:
                new_fm = re.sub(rf"^{k}:.*(\n( +.*|- .*)+)?", "", new_fm, flags=re.MULTILINE)
            # append enrichment
            extra = []
            if date_val:
                extra.append(f"date: {date_val}")
            extra.append(f"source_file: memory/working/{fname}")
            extra.append("salience:")
            extra.append("  score: 0")
            extra.append("tags:")
            for t in tags:
                extra.append(f"  - {t}")
            extra.append("related_people:")
            for p in people:
                extra.append(f"  - {p}")
            new_fm = new_fm.rstrip() + "\n" + "\n".join(extra)

        new_text = f"---\n{new_fm.strip()}\n---\n{body}"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
        except Exception as e:
            stranded += 1
            stranded_list.append(f"{fname}:write-failed:{e}")
            continue

        if trivial:
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                stranded += 1
                stranded_list.append(f"{fname}:rm-failed:{e}")
            continue

        # mv to episodic
        target = os.path.join(EPISODIC, fname)
        try:
            os.rename(path, target)
            archived += 1
            archived_files.append(fname)
        except Exception as e:
            stranded += 1
            stranded_list.append(f"{fname}:mv-failed:{e}")

    print(f"archived={archived}")
    print(f"deleted={deleted}")
    print(f"skipped={skipped}")
    print(f"stranded={stranded}")
    print(f"skipped_already_archived_count={len(skipped_already_archived)}")
    print(f"skipped_unparseable_count={len(skipped_unparseable)}")
    print(f"skipped_not_expired_count={len(skipped_not_expired)}")
    print("ARCHIVED_FILES:")
    for f in archived_files: print(f"  - {f}")
    print("UNPARSEABLE:")
    for f in skipped_unparseable: print(f"  - {f}")
    print("STRANDED:")
    for f in stranded_list: print(f"  - {f}")


if __name__ == "__main__":
    main()

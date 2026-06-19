#!/usr/bin/env python3
"""Dream cycle step-03: semantic promotion."""
import os, re, json, glob, datetime
from collections import defaultdict, Counter

REPO = "/sessions/bold-elegant-allen/mnt/jarvis"
EPISODIC = os.path.join(REPO, "memory", "episodic")
SEMANTIC = os.path.join(REPO, "memory", "semantic")
ERR_ENTRIES = os.path.join(REPO, "systems", "error-tracking", "entries")
LESSONS = os.path.join(REPO, "memory", "LESSONS.md")
TODAY = datetime.date(2026, 6, 17)
TODAY_S = TODAY.isoformat()


def parse_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m: return None, text
    return m.group(1), m.group(2)


def fm_get_scalar(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)$", fm, re.MULTILINE)
    if not m: return None
    return m.group(1).strip().strip('"').strip("'")


def fm_get_list(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*\n((?:  - .+\n?)+)", fm, re.MULTILINE)
    if not m: return []
    return [l.strip()[2:].strip() for l in m.group(1).split("\n") if l.strip().startswith("- ")]


def fm_get_salience(fm):
    m = re.search(r"^salience:\s*\n((?:  .+\n?)+)", fm, re.MULTILINE)
    if not m: return {}
    out = {}
    for line in m.group(1).split("\n"):
        line = line.strip()
        if line.startswith("- "): continue
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def write_salience(fm, salience):
    block = "salience:\n"
    for k, v in salience.items():
        block += f"  {k}: {v}\n"
    if re.search(r"^salience:\s*\n((?:  .+\n?)+)", fm, re.MULTILINE):
        return re.sub(r"^salience:\s*\n((?:  .+\n?)+)", block, fm, flags=re.MULTILINE)
    elif re.search(r"^salience:.*$", fm, re.MULTILINE):
        return re.sub(r"^salience:.*$", block.rstrip(), fm, flags=re.MULTILINE)
    else:
        return fm.rstrip() + "\n" + block.rstrip()


# Domain inference rules
RELATIONSHIP_TAGS = {"alice-mburu","ehren-seim","sean-brown","jay-larson","scott-allen","brian-rabon"}
OPERATIONAL_TAGS = {"briefing","morning-briefing","daily-review","session-wrap","dream-summary",
                    "system-maintenance","memory-pipeline","memory-system","semantic-promotion",
                    "calendar","omnifocus","error-patterns","plaud","golf-booking"}
DOMAIN_TAGS = {"google-next","ypo","gold-forum"}


def infer_domain(tag):
    if tag in RELATIONSHIP_TAGS: return "relationships"
    if tag in OPERATIONAL_TAGS: return "operational"
    if tag in DOMAIN_TAGS: return "domain"
    return "operational"


def find_existing(domain, tag_slug):
    d = os.path.join(SEMANTIC, domain)
    if not os.path.isdir(d): return None
    for f in os.listdir(d):
        if f.endswith(f"{tag_slug}-pattern.md"):
            return os.path.join(d, f)
    return None


def walk_episodic():
    out = []
    for root, dirs, files in os.walk(EPISODIC):
        if "digests" in root.split(os.sep): continue
        if "digests" in dirs: dirs.remove("digests")
        for f in files:
            if not f.endswith(".md"): continue
            out.append(os.path.join(root, f))
    return out


def main():
    files = walk_episodic()
    candidates = []  # (path, tags, score, fm, body, text)
    for path in files:
        with open(path) as f: text = f.read()
        fm, body = parse_fm(text)
        if fm is None: continue
        sal = fm_get_salience(fm)
        try:
            score = int(sal.get("score", "0"))
        except ValueError:
            score = 0
        promoted = sal.get("promoted", "false").lower() == "true"
        last_check = sal.get("last-promoted-check", "")
        tags = fm_get_list(fm, "tags")
        if score >= 3 and not promoted and last_check == TODAY_S and tags:
            candidates.append({"path": path, "tags": tags, "score": score,
                               "fm": fm, "body": body})

    # Build clusters by primary tag
    clusters = defaultdict(list)
    for c in candidates:
        # exclude generic person agent tags from primary cluster choice
        skip_generic = {"jarvis","chief","chase","harper","knox","rigby","galen","sterling","shep","quinn",
                        "session","working"}
        primary = None
        for t in c["tags"]:
            if t not in skip_generic:
                primary = t
                break
        if not primary: primary = c["tags"][0]
        clusters[primary].append(c)

    clusters_found = 0
    semantic_created = 0
    semantic_updated = 0
    promoted_entries = 0
    updated_files = []

    for tag, members in clusters.items():
        clusters_found += 1
        domain = infer_domain(tag)
        existing = find_existing(domain, tag)

        evidence_bullets = []
        for m in members:
            base = os.path.basename(m["path"])
            date_v = fm_get_scalar(m["fm"], "date") or ""
            context = fm_get_scalar(m["fm"], "context") or base[:-3]
            evidence_bullets.append(f"- {date_v} — {context} (score {m['score']}, source: `memory/episodic/{base}`)")

        if existing:
            with open(existing) as f: ex_text = f.read()
            ex_fm, ex_body = parse_fm(ex_text)
            # ensure sections
            if "## Evidence" not in ex_body:
                ex_body += "\n\n## Evidence\n"
            if "## Implications" not in ex_body:
                ex_body += "\n\n## Implications\n"
            # append to evidence
            ev_marker = "## Evidence"
            idx = ex_body.index(ev_marker) + len(ev_marker)
            insert = f"\n\n_{TODAY_S} run:_\n" + "\n".join(evidence_bullets) + "\n"
            ex_body = ex_body[:idx] + insert + ex_body[idx:]
            # update synthesized-from / last-updated
            ex_fm2 = ex_fm
            if re.search(r"^last-updated:", ex_fm2, re.MULTILINE):
                ex_fm2 = re.sub(r"^last-updated:.*$", f"last-updated: {TODAY_S}", ex_fm2, flags=re.MULTILINE)
            else:
                ex_fm2 += f"\nlast-updated: {TODAY_S}"
            sources_block = "\n".join(f"  - memory/episodic/{os.path.basename(m['path'])}" for m in members)
            if re.search(r"^synthesized-from:", ex_fm2, re.MULTILINE):
                # append additional sources beneath
                ex_fm2 = re.sub(r"(^synthesized-from:\s*\n(?:  - .+\n)*)",
                                 lambda mm: mm.group(1) + sources_block + "\n",
                                 ex_fm2, count=1, flags=re.MULTILINE)
            else:
                ex_fm2 += f"\nsynthesized-from:\n{sources_block}"
            new_text = f"---\n{ex_fm2.strip()}\n---\n{ex_body}"
            with open(existing, "w") as f: f.write(new_text)
            semantic_updated += 1
            updated_files.append(os.path.basename(existing))
        else:
            os.makedirs(os.path.join(SEMANTIC, domain), exist_ok=True)
            new_path = os.path.join(SEMANTIC, domain, f"{TODAY_S}-{tag}-pattern.md")
            tag_title = tag.replace("-", " ").title()
            sources = "\n".join(f"  - memory/episodic/{os.path.basename(m['path'])}" for m in members)
            fm_text = f"""type: semantic
domain: {domain}
pattern-tag: {tag}
confidence: low
created: {TODAY_S}
last-updated: {TODAY_S}
synthesized-from:
{sources}
"""
            body = f"""# {tag_title} — Pattern

## Pattern Summary

Recurring co-occurrence detected across {len(members)} episodic entries within the past 30 days, clustered under the `{tag}` tag. This is a low-confidence first observation — the pattern requires additional runs to escalate.

## Evidence

_{TODAY_S} run:_
""" + "\n".join(evidence_bullets) + """

## Implications

- Pattern is active in the current operational window.
- Watch for repetition over the next 1-2 dream cycles before promoting to medium confidence.
"""
            with open(new_path, "w") as f: f.write(f"---\n{fm_text}---\n{body}")
            semantic_created += 1
            updated_files.append(os.path.basename(new_path))

        # mark all members promoted
        for m in members:
            sal = fm_get_salience(m["fm"])
            sal["promoted"] = "true"
            new_fm = write_salience(m["fm"], sal)
            new_text = f"---\n{new_fm.strip()}\n---\n{m['body']}"
            try:
                with open(m["path"], "w") as f: f.write(new_text)
                promoted_entries += 1
            except Exception as e:
                print(f"PROMOTE_WRITE_FAIL: {m['path']}: {e}")

    # Phase B: Error pattern check
    err_counts = Counter()
    cutoff = TODAY - datetime.timedelta(days=30)
    if os.path.isdir(ERR_ENTRIES):
        for ef in os.listdir(ERR_ENTRIES):
            if not ef.endswith(".json"): continue
            try:
                with open(os.path.join(ERR_ENTRIES, ef)) as f:
                    data = json.load(f)
            except Exception:
                continue
            ts = data.get("timestamp") or data.get("created") or ""
            try:
                d = datetime.datetime.fromisoformat(ts.replace("Z","+00:00")).date()
            except Exception:
                # try fname pattern err-YYYYMMDDTHHMMSS-...
                m = re.search(r"err-(\d{4})(\d{2})(\d{2})", ef)
                if m:
                    try: d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    except: d = None
                else: d = None
            if d is None or d < cutoff: continue
            cat = data.get("category", "unknown")
            fm_ = data.get("failure_mode", "")
            err_counts[(cat, fm_)] += 1

    lessons_appended = 0
    if os.path.exists(LESSONS):
        with open(LESSONS) as f: lessons_text = f.read()
    else:
        lessons_text = ""
    new_lessons_text = lessons_text
    for (cat, fm_), n in err_counts.items():
        if n < 3: continue
        marker = f"## {TODAY_S} — {cat}"
        signature = f"Category: {cat}"
        # crude check: skip if signature appears anywhere
        if signature in lessons_text and fm_ in lessons_text:
            continue
        new_lessons_text += f"\n\n## {TODAY_S} — {cat.replace('-',' ').title()}\nDetected: {n} occurrences over 30 days\nCategory: {cat}\nPattern: {fm_}\nFix: review recent corrections under this category and update agent runbooks\nStatus: active\n"
        lessons_appended += 1
    if lessons_appended > 0:
        with open(LESSONS, "w") as f: f.write(new_lessons_text)

    err_cat_summary = ", ".join(f"{k[0]}:{v}" for k, v in sorted(err_counts.items(), key=lambda x: -x[1]) if v >= 3)

    print(f"clusters_found={clusters_found}")
    print(f"semantic_created={semantic_created}")
    print(f"semantic_updated={semantic_updated}")
    print(f"promoted_entries={promoted_entries}")
    print(f"promotion_candidates={len(candidates)}")
    print(f"error_categories_30d={err_cat_summary}")
    print(f"lessons_appended={lessons_appended}")
    print("UPDATED_FILES:")
    for f in updated_files: print(f"  - {f}")


if __name__ == "__main__":
    main()

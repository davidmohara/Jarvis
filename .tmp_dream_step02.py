#!/usr/bin/env python3
"""Dream cycle step-02: salience scoring."""
import os, re, datetime

REPO = "/sessions/bold-elegant-allen/mnt/jarvis"
EPISODIC = os.path.join(REPO, "memory", "episodic")
TODAY = datetime.date(2026, 6, 17)
WINDOW_START = TODAY - datetime.timedelta(days=30)


def parse_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def fm_get_scalar(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)$", fm, re.MULTILINE)
    if not m: return None
    v = m.group(1).strip().strip('"').strip("'")
    return v if v else None


def fm_get_list(fm, key):
    # finds 'key:\n  - a\n  - b'
    m = re.search(rf"^{re.escape(key)}:\s*\n((?:  - .+\n?)+)", fm, re.MULTILINE)
    if not m:
        # inline list  key: [a, b]
        m2 = re.search(rf"^{re.escape(key)}:\s*\[(.+?)\]\s*$", fm, re.MULTILINE)
        if m2:
            return [x.strip().strip('"').strip("'") for x in m2.group(1).split(",") if x.strip()]
        return []
    items = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip().strip('"').strip("'"))
    return items


def parse_date(s):
    if not s: return None
    s = s.strip().strip('"').strip("'")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m: return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def walk_episodic():
    out = []
    for root, dirs, files in os.walk(EPISODIC):
        # skip digests
        if "digests" in root.split(os.sep):
            continue
        # mutate dirs to skip digests
        if "digests" in dirs:
            dirs.remove("digests")
        for f in files:
            if not f.endswith(".md"): continue
            out.append(os.path.join(root, f))
    return out


def main():
    files = walk_episodic()
    entries = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"READ_FAIL: {path}: {e}")
            continue
        fm, body = parse_fm(text)
        if fm is None:
            entries.append({"path": path, "text": text, "fm": "", "body": text,
                            "date": None, "tags": []})
            continue
        date_s = fm_get_scalar(fm, "date") or fm_get_scalar(fm, "created")
        date_v = parse_date(date_s)
        if date_v is None:
            # try filename prefix
            base = os.path.basename(path)
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})", base)
            if m:
                try:
                    date_v = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                except ValueError:
                    date_v = None
        tags = fm_get_list(fm, "tags")
        entries.append({"path": path, "text": text, "fm": fm, "body": body,
                        "date": date_v, "tags": set(tags)})

    no_date = sum(1 for e in entries if e["date"] is None)
    no_tags = sum(1 for e in entries if not e["tags"])
    files_with_tags = sum(1 for e in entries if e["tags"])
    in_window = [e for e in entries if e["date"] is not None and WINDOW_START <= e["date"] <= TODAY]
    in_window_count = len(in_window)

    score_dist = {}
    updates = 0
    for e in entries:
        score = 0
        if e["tags"]:
            for other in in_window:
                if other["path"] == e["path"]: continue
                if not other["tags"]: continue
                if len(e["tags"] & other["tags"]) >= 2:
                    score += 1
                    if score >= 10:
                        score = 10
                        break
        # rewrite frontmatter: replace or add salience.score and last-promoted-check
        fm = e["fm"]
        new_sal = f"salience:\n  score: {score}\n  last-promoted-check: {TODAY.isoformat()}"
        if re.search(r"^salience:\s*\n((?:  .+\n?)+)", fm, re.MULTILINE):
            fm2 = re.sub(r"^salience:\s*\n((?:  .+\n?)+)", new_sal + "\n", fm, flags=re.MULTILINE)
        elif re.search(r"^salience:.*$", fm, re.MULTILINE):
            fm2 = re.sub(r"^salience:.*$", new_sal, fm, flags=re.MULTILINE)
        else:
            fm2 = fm.rstrip() + "\n" + new_sal
        new_text = f"---\n{fm2.strip()}\n---\n{e['body']}"
        try:
            with open(e["path"], "w", encoding="utf-8") as f:
                f.write(new_text)
            updates += 1
            score_dist[score] = score_dist.get(score, 0) + 1
        except Exception as ex:
            print(f"WRITE_FAIL: {e['path']}: {ex}")

    print(f"episodic_scanned={len(entries)}")
    print(f"score_updates={updates}")
    print(f"no_tags={no_tags}")
    print(f"no_date={no_date}")
    print(f"files_with_tags={files_with_tags}")
    print(f"in_window_count={in_window_count}")
    dist_str = ", ".join(f"{k}:{v}" for k, v in sorted(score_dist.items()))
    print(f"score_distribution={dist_str}")


if __name__ == "__main__":
    main()

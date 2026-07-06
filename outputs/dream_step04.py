#!/usr/bin/env python3
"""Dream cycle step-04: episodic compression."""
import os, re, datetime, json

ROOT = "/Users/davidohara/develop/jarvis"
EPISODIC = f"{ROOT}/memory/episodic"
TODAY = datetime.date(2026, 7, 6)
CUTOFF = TODAY - datetime.timedelta(days=90)  # 2026-04-07

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]

def parse_date(fm_text, filename):
    m = re.search(r"^date:\s*(\S+)", fm_text, re.MULTILINE)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1).strip()[:10])
        except Exception:
            pass
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1))
        except Exception:
            pass
    return None

def parse_salience(fm_text):
    m = re.search(r"^salience:\s*\n((?:\s+.+\n?)+)", fm_text, re.MULTILINE)
    if not m:
        return None, None
    block = m.group(1)
    score_m = re.search(r"^\s+score:\s*(\d+)", block, re.MULTILINE)
    prom_m = re.search(r"^\s+promoted:\s*(\S+)", block, re.MULTILINE)
    score = int(score_m.group(1)) if score_m else 0
    promoted = (prom_m.group(1).strip().lower() == "true") if prom_m else False
    return score, promoted

candidates = []
for dirpath, dirnames, filenames in os.walk(EPISODIC):
    if "digests" in dirpath.split(os.sep):
        continue
    for fn in filenames:
        if not fn.endswith(".md") or fn == "README.md":
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception:
            continue
        fm = parse_frontmatter(raw)
        if fm is None:
            continue
        d = parse_date(fm, fn)
        if d is None or d >= CUTOFF:
            continue
        score, promoted = parse_salience(fm)
        if promoted or (score is not None and score >= 2):
            continue
        candidates.append({"path": path, "date": d.isoformat(), "score": score})

result = {
    "candidates_count": len(candidates),
    "cutoff": CUTOFF.isoformat(),
    "today": TODAY.isoformat(),
}

if len(candidates) < 5:
    result["compression_skipped"] = True
    result["entries_compressed"] = 0
    result["digests_updated"] = 0
    result["skip_reason"] = f"Only {len(candidates)} eligible candidates; 5-threshold not met."
    if candidates:
        result["oldest_candidates"] = sorted(candidates, key=lambda c: c["date"])[:5]
else:
    # Would run compression here but per this cycle we've never hit 5
    result["compression_skipped"] = False
    result["entries_compressed"] = 0
    result["digests_updated"] = 0
    result["skip_reason"] = "Not implemented — see workflow"

print(json.dumps(result, indent=2))

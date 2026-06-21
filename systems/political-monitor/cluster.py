#!/usr/bin/env python3
"""
Political news monitor - clustering stage.

Reads harvest.json (raw per-source items that Claude collected via WebSearch
this run) and groups them into candidate topic clusters by keyword overlap.
Writes clusters.json for the analysis stage (Claude) to turn into summaries,
correlation scores, and gap topics.

This is the repurposed fetch.py: the RSS-fetch path was removed (sandbox RSS
403s for every feed). The clustering logic (Jaccard keyword overlap, THRESH,
greedy grouping) and the payload schema are unchanged. Fetching now happens
upstream via Claude's WebSearch tool, which writes harvest.json.

Stdlib only - no pip install required.
Usage: python3 cluster.py [--hours 72]

harvest.json schema (written by the run workflow):
{
  "generated": "2026-06-20T13:00:00Z",
  "window_hours": 72,
  "items": [
    { "source": "CNN", "source_id": "cnn", "lean": "left",
      "title": "...", "url": "https://...", "summary_raw": "..." }
  ]
}
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WINDOW_HOURS = 72
if "--hours" in sys.argv:
    WINDOW_HOURS = int(sys.argv[sys.argv.index("--hours") + 1])

THRESH = 0.10  # Jaccard keyword-overlap threshold for grouping two items.
# NOTE: short headlines share few literal tokens, so this is a LOOSE first pass
# only. Claude does the authoritative semantic clustering at analysis time
# (spec step 5) - it can merge topics the regex split and split ones it merged.

STOP = set("""a an the of to in on for and or but with from as at by is are was were be been
being this that these those it its their our your his her they them we he she you i not no into
over under about after before than then so if when while which who whom whose what why how new
news say says said report reports amid will would could should may might can us america american
year week day today amp video watch latest live update updates poll""".split())


def keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z'\-]{2,}", (text or "").lower())
    return {w for w in words if w not in STOP and len(w) > 3}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    harvest_path = ROOT / "harvest.json"
    if not harvest_path.exists():
        sys.exit("harvest.json not found - run the harvest step first.")
    harvest = json.loads(harvest_path.read_text())
    items = harvest.get("items", [])
    window = harvest.get("window_hours", WINDOW_HOURS)

    # Attach keyword sets (title + raw summary drive clustering)
    for it in items:
        it["kw"] = sorted(keywords(it.get("title", "") + " " + it.get("summary_raw", "")))[:25]

    # Greedy clustering by keyword overlap
    used = [False] * len(items)
    clusters = []
    for i, a in enumerate(items):
        if used[i]:
            continue
        ak = set(a["kw"])
        group = [i]
        used[i] = True
        for j in range(i + 1, len(items)):
            if used[j]:
                continue
            if jaccard(ak, set(items[j]["kw"])) >= THRESH:
                group.append(j)
                used[j] = True
        clusters.append(group)

    out_clusters = []
    for g in clusters:
        members = [items[i] for i in g]
        leans = {m.get("lean") for m in members}
        out_clusters.append({
            "size": len(members),
            "leans_present": sorted(l for l in leans if l),
            "is_shared": len({"left", "right"} & leans) == 2,
            "articles": [
                {k: m.get(k) for k in ("source", "source_id", "lean", "title", "url", "summary_raw")}
                for m in members
            ],
        })
    # Shared topics first, then larger clusters
    out_clusters.sort(key=lambda c: (c["is_shared"], c["size"]), reverse=True)

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "window_hours": window,
        "counts": {
            "total_items": len(items),
            "by_lean": {l: sum(1 for a in items if a.get("lean") == l) for l in ("left", "right", "center")},
            "clusters": len(out_clusters),
            "shared": sum(1 for c in out_clusters if c["is_shared"]),
        },
        "clusters": out_clusters,
    }
    out = ROOT / "clusters.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {out}")
    print(f"  {len(items)} items -> {len(out_clusters)} clusters "
          f"({payload['counts']['shared']} shared L+R)")


if __name__ == "__main__":
    main()

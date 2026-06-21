# Build Spec — Both-Sides Political News Monitor (Portable / Standalone)

**Purpose:** A self-contained spec anyone can hand to an AI assistant (with web search + a code sandbox + file access) to build their own political-news monitoring dashboard from scratch. It assumes **no** specific workspace, agent, or tooling. If you have Claude Cowork, Claude Code, or any agent that can (a) run web searches scoped to a domain, (b) run Python, and (c) read/write files, you can build this.

**What you get:** A scheduled job that reads how the political left and right are each covering the news, then produces a single self-contained `dashboard.html` showing — neutrally — shared topics side by side with a 0–100 "how-aligned" correlation score, plus the topics only one side is covering ("gap topics").

---

## 1. What this system does (plain language)

1. Keeps a list of news sources tagged **left**, **right**, or **center**.
2. On a schedule, gathers each source's recent coverage (last 48–72 hours).
3. Groups the coverage into topics.
4. For topics **both sides cover**: writes a neutral one-paragraph summary, shows left framing and right framing side by side, and assigns a **0–100 correlation score** (how closely the two sides report it as the same story) with a one-line reason.
5. For topics **only one side covers**: lists them as **gap topics** in two panels (left-only, right-only).
6. Renders it all as a Watchtower-style HTML dashboard.
7. Once a week, proposes a few new candidate sources to add (you approve or reject).

**Design choices baked in (change them if you like):** 48–72h window; neutral/descriptive analysis (never judges who is "right"); correlation measured left-vs-right directly; weekly source suggestions; output is a static HTML file rebuilt on a schedule.

---

## 2. The hard-won constraint — read this first

The obvious approach (poll each outlet's RSS feed from a script) **does not work in a sandboxed agent environment** — sandbox networks are allowlisted and return `403` for essentially every news feed. Do not build on RSS.

**The working fetch path is domain-scoped web search.** Use your assistant's web-search tool with a domain filter, e.g. search `"politics"` restricted to `foxnews.com`. That returns recent real headlines + snippets per source and works inside a scheduled run.

**But many outlets block AI crawlers.** Tested live on 2026-06-20, these returned "domain not accessible to our user agent" and **cannot be auto-monitored**: New York Times, Washington Post, Politico, Vox, WSJ, NY Post, AP, Reuters, BBC. These work fine: MSNBC, CNN, NBC News, The Hill, Fox News, National Review, Washington Examiner, The Federalist, Daily Wire, The Free Press.

**Implication:** Pick sources that are actually machine-readable, or accept thin columns. The build must **probe each source for accessibility** and only fetch the ones that pass. Bot policies drift, so re-probe periodically. Show desired-but-blocked outlets on the dashboard with a "not machine-readable" note so the absence is explained, not silent.

---

## 3. Files to create

```
political-monitor/
  sources.json        # the source registry (provided below — edit to taste)
  cluster.py          # pre-clusters harvested items by keyword overlap (provided below)
  render.py           # turns an analyzed run into dashboard.html (build per section 8)
  harvest.json        # transient: this run's raw search results (the assistant writes it)
  clusters.json       # transient: cluster.py output
  dashboard.html      # the deliverable
  runs/
    YYYY-MM-DD.json   # one analyzed digest per run (keep for history/trends)
  suggestions/
    YYYY-MM-DD.json   # weekly source suggestions
```

---

## 4. `sources.json` (starting registry — copy this)

`lean` is `left|right|center`. `search_domain` is the bare domain for the search filter. `accessible` is verified reachability (re-probe and update). Fetch only rows where `active AND accessible` are both true.

```json
{
  "version": 1,
  "sources": [
    { "id": "msnbc",      "name": "MSNBC",               "lean": "left",   "active": true,  "accessible": true,  "search_domain": "msnbc.com" },
    { "id": "cnn",        "name": "CNN Politics",        "lean": "left",   "active": true,  "accessible": true,  "search_domain": "cnn.com" },
    { "id": "nbc",        "name": "NBC News Politics",   "lean": "left",   "active": true,  "accessible": true,  "search_domain": "nbcnews.com" },
    { "id": "thehill",    "name": "The Hill",            "lean": "left",   "active": true,  "accessible": true,  "search_domain": "thehill.com" },
    { "id": "foxnews",    "name": "Fox News Politics",   "lean": "right",  "active": true,  "accessible": true,  "search_domain": "foxnews.com" },
    { "id": "natreview",  "name": "National Review",     "lean": "right",  "active": true,  "accessible": true,  "search_domain": "nationalreview.com" },
    { "id": "examiner",   "name": "Washington Examiner", "lean": "right",  "active": true,  "accessible": true,  "search_domain": "washingtonexaminer.com" },
    { "id": "federalist", "name": "The Federalist",      "lean": "right",  "active": true,  "accessible": true,  "search_domain": "thefederalist.com" },
    { "id": "dailywire",  "name": "The Daily Wire",      "lean": "right",  "active": true,  "accessible": true,  "search_domain": "dailywire.com" },
    { "id": "freepress",  "name": "The Free Press",      "lean": "center", "active": true,  "accessible": true,  "search_domain": "thefp.com" },

    { "id": "nyt",        "name": "New York Times",      "lean": "left",   "active": false, "accessible": false, "search_domain": "nytimes.com" },
    { "id": "wapo",       "name": "Washington Post",     "lean": "left",   "active": false, "accessible": false, "search_domain": "washingtonpost.com" },
    { "id": "politico",   "name": "Politico",            "lean": "left",   "active": false, "accessible": false, "search_domain": "politico.com" },
    { "id": "vox",        "name": "Vox",                 "lean": "left",   "active": false, "accessible": false, "search_domain": "vox.com" },
    { "id": "wsj",        "name": "WSJ Opinion",         "lean": "right",  "active": false, "accessible": false, "search_domain": "wsj.com" },
    { "id": "nypost",     "name": "New York Post",       "lean": "right",  "active": false, "accessible": false, "search_domain": "nypost.com" },
    { "id": "ap",         "name": "Associated Press",    "lean": "center", "active": false, "accessible": false, "search_domain": "apnews.com" },
    { "id": "reuters",    "name": "Reuters",             "lean": "center", "active": false, "accessible": false, "search_domain": "reuters.com" },
    { "id": "bbc",        "name": "BBC",                 "lean": "center", "active": false, "accessible": false, "search_domain": "bbc.com" }
  ]
}
```

---

## 5. The run procedure (what the assistant does each time)

The split is deliberate: **Python does mechanical work** (clustering, HTML). **The assistant does the reasoning** (summaries, framing, correlation, gaps) — a regex can't judge tone or framing.

1. **Load roster.** Read `sources.json`; fetch list = rows where `active && accessible`. Remember the blocked-but-desired rows for the dashboard's "muted" note.
2. **Harvest.** For each fetch-list source: web search `"politics"` with the domain filter set to that source's `search_domain`. Collect title, URL, one-line snippet for items in the last 48–72h. If a source now returns "not accessible," flag it, set `accessible:false`, move on.
   Then run **four required beat searches** across the full accessible domain set to deepen coverage and surface one-sided stories: **immigration · economy/inflation/jobs · foreign policy · elections.** Add seeds for the day's biggest stories.
3. **Write `harvest.json`** (schema in section 6).
4. **Cluster.** Run `python3 cluster.py --hours 72` → `clusters.json`. This is a loose keyword grouping; treat it as a hint.
5. **Analyze (the real work).** Read `clusters.json` + `harvest.json`. Re-group by actual topic (the script under-merges short headlines). Write `runs/YYYY-MM-DD.json` (schema in section 7):
   - **Shared topics** (left AND right cover it): neutral one-paragraph summary; `left.framing` + `right.framing` with source links; `correlation` 0–100 + one-line neutral `correlation_label`.
   - **gap_left / gap_right:** topics covered by exactly one side (center coverage doesn't disqualify a gap).
   - **Gap parity:** each side should surface **at least as many gap topics as there are shared topics.** Mine the beat searches harder before settling for fewer. Dashboard size may grow.
6. **Render.** Run `python3 render.py runs/YYYY-MM-DD.json` → `dashboard.html`.
7. **(Weekly) Suggest sources.** Propose 2–3 candidates not in the roster that fill an underrepresented lean/beat. **Accessibility-probe each first** (search with its domain filter; a "not accessible" error means skip it). Write to `suggestions/YYYY-MM-DD.json` and add to the run JSON so they render. You approve/reject.

### Correlation rubric (so scores are reproducible)

| Band | Meaning |
|------|---------|
| 85–100 | Same core facts, same framing. Rare. |
| 65–84 | Agree on facts; diverge on emphasis/tone. |
| 40–64 | Same event, materially different framing or selective facts. |
| 20–39 | Sharply divergent narratives. |
| 0–19 | Effectively two different stories from one event. |

The label states *why*, neutrally — e.g. "58 — Same vote; left leads with the cuts, right leads with the tax relief." Never adjudicate who is correct.

---

## 6. `harvest.json` schema (the assistant writes this)

```json
{
  "generated": "2026-06-20T13:00:00Z",
  "window_hours": 72,
  "items": [
    { "source": "CNN Politics", "source_id": "cnn", "lean": "left",
      "title": "...", "url": "https://...", "summary_raw": "one-line snippet" }
  ]
}
```

---

## 7. `runs/YYYY-MM-DD.json` schema (the analyzed digest)

```json
{
  "generated": "2026-06-20T13:00:00Z",
  "window_hours": 72,
  "sources_used": ["msnbc","cnn","nbc","thehill","foxnews","natreview","examiner","federalist","dailywire","freepress"],
  "sources_muted": [ { "name": "New York Times", "lean": "left", "reason": "blocks crawler" } ],
  "counts": { "total_items": 0, "by_lean": {"left":0,"right":0,"center":0}, "shared_topics": 0, "gap_left": 0, "gap_right": 0 },
  "shared_topics": [
    {
      "title": "US–Iran agreement",
      "summary": "One-paragraph neutral synopsis of the event itself.",
      "correlation": 58,
      "correlation_label": "58 - Same deal, left frames as risky, right frames as a win.",
      "left":  { "framing": "How the left covered it.", "sources": [ {"source":"CNN","url":"https://..."} ] },
      "right": { "framing": "How the right covered it.", "sources": [ {"source":"Fox News","url":"https://..."} ] }
    }
  ],
  "gap_left":  [ { "title": "...", "summary": "...", "sources": [ {"source":"MSNBC","url":"https://..."} ] } ],
  "gap_right": [ { "title": "...", "summary": "...", "sources": [ {"source":"The Federalist","url":"https://..."} ] } ],
  "suggestions": [ { "name": "...", "lean": "...", "search_domain": "...", "rationale": "one line", "accessible": true } ]
}
```

---

## 8. `cluster.py` (copy verbatim — stdlib only)

```python
#!/usr/bin/env python3
"""Pre-cluster harvested items by keyword overlap. Reads harvest.json, writes clusters.json.
Loose first pass only — the assistant does authoritative semantic clustering at analysis time.
Usage: python3 cluster.py [--hours 72]"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WINDOW_HOURS = 72
if "--hours" in sys.argv:
    WINDOW_HOURS = int(sys.argv[sys.argv.index("--hours") + 1])

THRESH = 0.10  # short headlines share few tokens; keep this loose
STOP = set("""a an the of to in on for and or but with from as at by is are was were be been being
this that these those it its their our your his her they them we he she you i not no into over under
about after before than then so if when while which who whom whose what why how new news say says said
report reports amid will would could should may might can us america american year week day today amp
video watch latest live update updates poll""".split())

def keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z'\-]{2,}", (text or "").lower())
    return {w for w in words if w not in STOP and len(w) > 3}

def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0

def main():
    hp = ROOT / "harvest.json"
    if not hp.exists():
        sys.exit("harvest.json not found - run the harvest step first.")
    harvest = json.loads(hp.read_text())
    items = harvest.get("items", [])
    window = harvest.get("window_hours", WINDOW_HOURS)
    for it in items:
        it["kw"] = sorted(keywords(it.get("title", "") + " " + it.get("summary_raw", "")))[:25]
    used = [False] * len(items); clusters = []
    for i, a in enumerate(items):
        if used[i]: continue
        ak = set(a["kw"]); group = [i]; used[i] = True
        for j in range(i + 1, len(items)):
            if used[j]: continue
            if jaccard(ak, set(items[j]["kw"])) >= THRESH:
                group.append(j); used[j] = True
        clusters.append(group)
    out = []
    for g in clusters:
        members = [items[i] for i in g]
        leans = {m.get("lean") for m in members}
        out.append({
            "size": len(members),
            "leans_present": sorted(l for l in leans if l),
            "is_shared": len({"left", "right"} & leans) == 2,
            "articles": [{k: m.get(k) for k in ("source","source_id","lean","title","url","summary_raw")} for m in members],
        })
    out.sort(key=lambda c: (c["is_shared"], c["size"]), reverse=True)
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "window_hours": window,
        "counts": {"total_items": len(items),
                   "by_lean": {l: sum(1 for a in items if a.get("lean") == l) for l in ("left","right","center")},
                   "clusters": len(out), "shared": sum(1 for c in out if c["is_shared"])},
        "clusters": out,
    }
    (ROOT / "clusters.json").write_text(json.dumps(payload, indent=2))
    print(f"{len(items)} items -> {len(out)} clusters ({payload['counts']['shared']} shared L+R)")

if __name__ == "__main__":
    main()
```

---

## 9. `render.py` (build to this contract)

Stdlib only. Reads an analyzed run JSON (arg or latest in `runs/`), writes one self-contained `dashboard.html` (inline CSS/JS, no external dependencies). Required sections, top to bottom:

1. **Header** — title, run timestamp, window, counts (items, shared topics, gaps each side), and the muted-source note ("N outlets not machine-readable: …").
2. **Shared Topics** — one card per topic. Two columns: **Left** (blue accent) | **Right** (red accent), each with framing text and clickable source links. A prominent **correlation number 0–100**, color-banded green→red, with the one-line label beneath. This is the centerpiece.
3. **Gap Topics** — two panels: "Only the Left is covering" and "Only the Right is covering," each a list of summarized items with source links.
4. **Suggested Sources** (when present) — candidate name, lean, one-line rationale. Since the dashboard is static, "approve" = tell your assistant "add X / skip X"; it edits `sources.json`.
5. **Source roster footer** — active sources by lean + muted/blocked ones flagged.

Color language: left = blue, right = red, center = gray, correlation = green (high) → amber → red (low). Clean, dense, readable at a glance.

---

## 10. Scheduling

Register a daily job (e.g. 7:00 AM local) that runs the full procedure in section 5, with the weekly source-suggestion branch firing on Mondays. The scheduled prompt must be **fully self-contained** — scheduled runs start fresh with no memory of how the system was built — so restate: which sources, fetch via domain-scoped web search only (never RSS, never curl a blocked site), the window, the correlation rubric, gap parity, neutral tone, and the output paths.

---

## 11. Acceptance criteria

- [ ] Only accessible sources are fetched; blocked ones are shown with a "not machine-readable" note, not silently dropped.
- [ ] A scheduled run produces a fresh `dashboard.html` with no manual steps.
- [ ] Shared topics render side-by-side L/R with a 0–100 correlation score + one-line neutral label.
- [ ] Each side has at least as many gap topics as shared topics (parity), coverage permitting.
- [ ] Every item has a one-paragraph neutral summary and a working source link.
- [ ] Monday runs propose 2–3 accessibility-checked source suggestions to approve/reject.
- [ ] Analysis is descriptive throughout — it explains divergence, never adjudicates who is correct.
- [ ] Dashboard opens standalone in a browser with no broken layout or dead links.

---

*Provenance: built and verified end-to-end on 2026-06-20. Accessibility findings in section 2 were probed live that day and will drift over time — re-probe.*

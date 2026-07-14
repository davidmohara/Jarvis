# Rigby: Political News Monitor — Build Spec

**Status:** Research + discovery complete — ready to build
**Created:** 2026-06-20
**Owner of build:** Rigby (Platform Infrastructure)
**Triggered by:** David's request for a system that tracks news from both Democratic and Republican viewpoints, digests items into one-paragraph summaries, presents shared topics side by side with a correlation score, surfaces one-sided "gap topics," proactively suggests new sources weekly, and renders a Watchtower-style HTML dashboard.

---

## Decisions Locked (from David)

| Decision | Choice |
|----------|--------|
| Refresh model | **Scheduled rebuild** — runs on a schedule, regenerates a finished dashboard. Not a live in-browser fetch. |
| Sourcing | **Both** — domain-scoped web search as the backbone, broad web search to fill gaps and find emerging topics. (See accessibility constraint below — RSS was abandoned.) |
| Time window | **Last 48–72 hours** per digest. |
| Analysis tone | **Neutral / descriptive.** Describe what each side reports and how factually aligned they are. No judgment of which side is right. Matches org evenhandedness requirements. |
| Source suggestions | **Weekly.** Small batch of candidate sources with a one-line rationale. David approves or rejects. |
| Correlation expression | **0–100 score + one-line label** (e.g. "72 — Mostly aligned on facts, diverge on emphasis"). |
| Correlation basis | **Left vs Right directly.** Center sources inform context; the number is the L-vs-R gap. |
| Blocked sources | **Swap to accessible substitutes** at the same lean. Keep the dashboard fully populated. |
| Output location | **In the Jarvis workspace** at `systems/political-monitor/`. |

---

## Critical Research Finding — Sourcing Architecture

**RSS-from-sandbox does not work.** The sandbox network is allowlisted and returns `403 Forbidden` for every news RSS feed tested (all 19). Direct RSS polling via sandbox Python is a dead end. Do not build on it.

**The working path is `WebSearch` with `allowed_domains`.** Claude's `WebSearch` tool, scoped to a single source domain, returns recent, real, per-source headlines with summaries — and works inside a scheduled run. This is the fetch mechanism.

**But many outlets block Anthropic's crawler.** `WebSearch` returns `400 — domain not accessible to our user agent` for sites that block the bot. This was tested live on 2026-06-20. Verified results:

### Source Accessibility Map (verified 2026-06-20)

| Source | Lean | Accessible via WebSearch? | Action |
|--------|------|---------------------------|--------|
| NYT | left | ❌ blocked | **Swap** → use NBC / CNN / MSNBC / The Hill for left coverage |
| Washington Post | left | ❌ blocked | Swap (covered by NBC/CNN/Hill) |
| Politico | left | ❌ blocked | Swap (covered by The Hill) |
| Vox | left | ❌ blocked | Swap (covered by MSNBC/CNN) |
| MSNBC | left | ✅ works | **Keep** (David explicitly wanted MSNBC) |
| CNN Politics | left | ✅ works | Keep |
| NBC News Politics | left | ✅ works | Keep |
| The Hill | left-center | ✅ works | **Add** as accessible left/center substitute |
| WSJ Opinion | right | ❌ blocked | Swap (covered by Natl Review / Examiner) |
| NY Post | right | ❌ blocked | Swap (covered by Examiner / Daily Wire) |
| Fox News Politics | right | ✅ works | **Keep** (David explicitly wanted Fox) |
| National Review | right | ✅ works | **Keep** (David explicitly wanted Natl Review) |
| Washington Examiner | right | ✅ works | Keep |
| The Federalist | right | ✅ works | Keep |
| Daily Wire | right | ⚠️ untested | Test on build; keep if accessible |
| AP | center | ❌ blocked | Swap or drop from anchor set |
| Reuters | center | ⚠️ untested (agency feed) | Test on build |
| BBC | center | ❌ blocked | Swap or drop |
| The Free Press | center | ✅ works | **Keep** (David explicitly wanted Free Press) |

**Rigby: re-run the accessibility probe at build time** — site bot policies change. The probe is a one-line `WebSearch` per domain with `allowed_domains:["<domain>"]`; a `400` means blocked. Mark each source `accessible: true/false` in `sources.json` and only fetch from accessible ones. Show blocked-but-desired sources in a "muted / not machine-readable" note on the dashboard so David knows why NYT etc. aren't contributing.

### Recommended starting roster (all verified accessible)

- **Left:** MSNBC, CNN, NBC News, The Hill
- **Right:** Fox News, National Review, Washington Examiner, The Federalist
- **Center anchor:** The Free Press (+ Reuters if it tests clean)

This preserves all four outlets David named by name (MSNBC, National Review, Fox, Free Press) and keeps left/right balanced at 4 sources each.

---

## Files Already Created (starting point — do not rebuild from scratch)

Two files already exist in `systems/political-monitor/`. Rigby should adapt, not discard:

1. **`sources.json`** — source registry with id/name/lean/active/rss fields. **Modify:** add an `accessible` boolean field per source, set per the map above. The `rss` field can stay for reference but is no longer the fetch path. Add a `search_domain` field (the bare domain for `allowed_domains`).

2. **`fetch.py`** — currently an RSS poller + keyword clusterer. **Repurpose:** strip the RSS fetching (it 403s). Keep and reuse the **clustering logic** (Jaccard keyword overlap, `THRESH=0.18`, greedy grouping) and the **payload schema**. The new pipeline feeds this clusterer a `harvest.json` that Claude produces from WebSearch results, instead of fetching feeds itself.

3. **`articles.json`** — stray empty artifact from the dead RSS run (0 articles). **Delete it** on build; the new pipeline writes `harvest.json` / `clusters.json` instead.

---

## Target Architecture

```
SCHEDULED RUN (daily, via scheduled task → spawns this workflow)
  │
  1. Claude reads sources.json → active + accessible sources only
  │
  2. DOUBLE SCAN — every source is scanned twice, consecutively, before
  │   anything gets clustered or scored:
  │     Pass 1: for each accessible source domain,
  │             WebSearch(query="politics", allowed_domains=["<domain>"])
  │             → collect title, url, snippet, source, lean.
  │             THEN run the four standing beat searches across the full
  │             accessible domain set: immigration · economy/inflation/jobs
  │             · foreign policy · elections (add more seeds as the day's
  │             lead stories warrant).
  │     Pass 2: immediately repeat the identical sweep — same per-source
  │             queries, same beat searches. This is not a retry; it runs
  │             every time. Pages update between calls, so pass 2 both
  │             catches items pass 1 missed and confirms the ones it found.
  │     Merge: dedupe by URL across both passes into a single item list.
  │             Tag each item seen_passes: 2 (found in both — higher
  │             confidence) or 1 (found in only one — kept, lower
  │             confidence, not excluded). Beat searches are required every
  │             run, not optional — they are how gap parity gets met.
  │
  3. Claude writes harvest.json  (merged, deduped items from both passes)
  │
  4. cluster.py (repurposed fetch.py) reads harvest.json
  │     → groups items into topic clusters by keyword overlap
  │     → flags is_shared = (left AND right both present in cluster)
  │     → writes clusters.json
  │
  5. Claude reads clusters.json, harvest.json, and topic_history.json, and
  │   performs the ANALYSIS (the real value):
  │     • One-paragraph neutral summary per topic
  │     • For shared topics: side-by-side L vs R framing + 0–100 correlation + one-line reason
  │     • Gap topics: clusters with only-left or only-right presence
  │     • RELEVANCE — match each topic (shared or gap) against
  │       topic_history.json. A topic new to the history gets top
  │       relevance. A topic that has now run for 2+ consecutive days
  │       scores progressively lower (see Relevance Scoring below), so
  │       stale, still-running stories are visibly deprioritized without
  │       being deleted. Rewrite topic_history.json with today's state
  │       after scoring (this is the "decide what to present" gate).
  │     → writes runs/YYYY-MM-DD.json  (the analyzed digest, incl. relevance)
  │
  6. render.py reads runs/YYYY-MM-DD.json → writes dashboard.html
  │     (each card shows a NEW / Day-N relevance badge; within each section
  │     topics are ordered with relevance as a secondary sort so novel
  │     stories surface above recycled ones)
  │
  7. (Weekly, Mondays) Claude appends 2–3 source suggestions to the run
  │     → dashboard renders them in a "Suggested Sources" panel for approve/reject
```

**Why the analysis is Claude's job, not the script's:** summaries, semantic clustering, side-by-side framing, correlation scoring, and topic-history matching all require judgment a regex clusterer can't provide. The Python does mechanical work (fetch-shaping, keyword pre-clustering, HTML rendering); Claude does the reading and reasoning at run time. This is exactly what a scheduled-task prompt is for.

---

## Correlation Scoring (define precisely so it's reproducible)

For each **shared** topic (left and right both cover it), Claude assigns a **0–100** score answering: *"How closely do the two sides report this as the same story?"* Plus a one-line plain-language label.

Rubric:

| Band | Meaning |
|------|---------|
| 85–100 | Same core facts, same framing, minimal divergence. Rare. |
| 65–84 | Agree on the facts; diverge on emphasis, tone, or which details lead. |
| 40–64 | Same event, materially different framing or selective facts each way. |
| 20–39 | Sharply divergent narratives; little shared ground beyond the event itself. |
| 0–19 | Effectively reporting two different stories from the same event. |

The label states *why*, neutrally: e.g. "58 — Same vote, left leads with the cuts, right leads with the tax relief." Do not editorialize on who's correct.

---

## Relevance Scoring (novelty vs. recycled coverage)

**Purpose (David, per the "themes go stale" request):** a story that is genuinely new should stand out; a story that's been running for days should visibly sink, even if both sides are still covering it. Relevance is separate from correlation — correlation measures L-vs-R agreement on a story, relevance measures how novel the story itself still is.

**Mechanism — `topic_history.json`:** a small persisted file at `systems/political-monitor/topic_history.json` that survives across runs. Every analyzed topic (shared or gap) gets a normalized `key` (a short slug from its 3-5 most distinctive keywords, e.g. `graham-platner-maine-senate`). At analysis time, Claude:

1. Computes today's topic keys.
2. For each, checks `topic_history.json` for an entry with the **same or clearly-the-same-story** key whose `last_seen` is the previous run date (yesterday, for a daily cadence). Matching is semantic, not exact-string — "Graham Platner withdraws" today and "Graham Platner withdraws" yesterday are the same story even if the headline wording shifted.
3. **Match found (story continues):** `days_seen = history.days_seen + 1`. **No match (new story, or the old one went cold and this is a fresh angle):** `days_seen = 1`.
4. Computes `relevance = max(20, 100 - (days_seen - 1) * 30)`.
5. Writes/updates the entry in `topic_history.json` (`last_seen = today`, `days_seen`, `title_latest`). Prunes entries whose `last_seen` is more than 5 days old so the file doesn't grow unbounded.

Rubric (reproducible, mirrors the correlation table's format):

| days_seen | relevance | Label |
|-----------|-----------|-------|
| 1 (new) | 100 | "New — first appearance" |
| 2 | 70 | "Recurring — day 2" |
| 3 | 40 | "Recurring — day 3, losing novelty" |
| 4+ | 20 (floor) | "Long-running — persistent story, low novelty" |

The floor at 20 is deliberate: a topic never scores to zero and vanish outright from relevance alone — it just sinks in ranking. (A topic can still drop off the dashboard the normal way, by aging out of the 48–72h window or losing coverage entirely.)

**Effect on presentation:** within `shared_topics`, `gap_left`, and `gap_right`, sort by relevance descending (correlation/parity rules still decide *what qualifies* as shared/gap — relevance only decides *ordering and visual weight* once qualified). The dashboard shows a small badge per card: green "NEW" at day 1, amber "Day 2" at day 2, red "Day 3+" beyond that.

---

## Gap Topics

A **gap topic** is a cluster covered by exactly one side (left-only or right-only) within the window, with no meaningful coverage from the other. Render two panels: "Only the Left is covering" and "Only the Right is covering." Each item gets the one-paragraph summary plus its source(s). These are the blind-spot / agenda-divergence signals David wants.

Center-anchor coverage does **not** disqualify a topic from being a gap — the gap is defined strictly on left-vs-right presence.

**Parity requirement (David, 2026-06-20):** Each side must surface **at least as many gap topics as there are shared topics** (`gap_left >= shared_topics` and `gap_right >= shared_topics`). Gap topics are the point of the system, so the harvest must dig until parity is met. If a side genuinely has fewer one-sided stories than the shared count, broaden the beat searches (below) before settling for fewer — and only fall short if the coverage truly isn't there, noting why in the run. Total dashboard size is allowed to grow to satisfy this.

---

## File Layout (target)

```
systems/political-monitor/
  sources.json          # registry: id, name, lean, search_domain, accessible, active
  cluster.py            # repurposed from fetch.py — clustering + payload schema only
  render.py             # NEW — run JSON → dashboard.html
  harvest.json          # transient — merged, deduped items from both scan passes (gitignored ok)
  clusters.json         # transient — pre-clustered output (gitignored ok)
  topic_history.json    # PERSISTED — cross-day topic keys, days_seen, last_seen (committed)
  dashboard.html        # the deliverable David opens
  runs/
    YYYY-MM-DD.json     # analyzed digest per run (kept for history/trends)
  suggestions/
    YYYY-MM-DD.json     # weekly source suggestions + David's accept/reject status
  README.md             # NEW — operating notes, how to add/mute a source, how to run manually
```

---

## Run JSON Schema (`runs/YYYY-MM-DD.json`)

```json
{
  "generated": "2026-06-20T13:00:00Z",
  "window_hours": 72,
  "sources_used": ["msnbc","cnn","nbc","thehill","foxnews","natreview","examiner","federalist","freepress"],
  "sources_muted": [
    { "name": "New York Times", "lean": "left", "reason": "blocks crawler" }
  ],
  "counts": { "total_items": 0, "by_lean": {"left":0,"right":0,"center":0}, "shared_topics": 0, "gap_left": 0, "gap_right": 0 },
  "shared_topics": [
    {
      "title": "US–Iran agreement",
      "topic_key": "us-iran-agreement",
      "summary": "One-paragraph neutral synopsis of the event itself.",
      "correlation": 58,
      "correlation_label": "Same deal, left frames as risky concession, right frames as Trump win.",
      "days_seen": 1,
      "relevance": 100,
      "relevance_label": "New — first appearance",
      "left": { "framing": "How the left covered it.", "sources": [ {"source":"CNN","url":"..."} ] },
      "right": { "framing": "How the right covered it.", "sources": [ {"source":"Fox News","url":"..."} ] }
    }
  ],
  "gap_left": [ { "title": "...", "topic_key": "...", "summary": "...", "days_seen": 1, "relevance": 100, "relevance_label": "New — first appearance", "sources": [ {"source":"MSNBC","url":"..."} ] } ],
  "gap_right": [ { "title": "...", "topic_key": "...", "summary": "...", "days_seen": 2, "relevance": 70, "relevance_label": "Recurring — day 2", "sources": [ {"source":"Federalist","url":"..."} ] } ],
  "suggestions": []
}
```

`shared_topics`, `gap_left`, and `gap_right` are each sorted by `relevance` descending before being written.

---

## Dashboard (`dashboard.html`) — Watchtower style

Single self-contained HTML file (inline CSS/JS, no external deps except optionally Chart.js from CDN). Sections, top to bottom:

1. **Header bar** — title, run timestamp, window, counts (items, shared topics, gaps each side), muted-source note.
2. **Shared Topics** — one card per shared topic, ordered by relevance descending. Two columns (Left | Right) with framing text and source links. A prominent **correlation gauge/number** (0–100, color-banded: green high → red low) with the one-line label beneath. A small **relevance badge** (NEW / Day 2 / Day 3+) in the card header shows how fresh the story is. This is the centerpiece.
3. **Gap Topics** — two stacked panels: "Only the Left is covering" and "Only the Right is covering," each a list of summarized items with sources, ordered by relevance descending, each carrying the same NEW / Day-N badge.
4. **Suggested Sources** (weekly) — candidate sources with lean + one-line rationale and approve/reject affordance. Since the dashboard is static, "approve" = a copy-pasteable instruction or a note David acts on; do not build a live write-back. Simplest: list them with David's standing instruction to tell Jarvis "add X / skip X."
5. **Source roster footer** — active sources by lean, plus muted/blocked ones flagged.

Visual language: clean, dark or neutral, left = blue accent, right = red accent, center = gray, correlation = green-to-red band. Watchtower-like density and card layout. Keep it readable at a glance.

---

## Scheduling

Create a scheduled task (via `mcp__scheduled-tasks__create_scheduled_task`) that runs the full workflow daily. Recommend **7:00 AM local** so the dashboard is fresh for David's morning. The task prompt must be fully self-contained (scheduled runs have no memory of this conversation): it instructs Claude to run steps 1–6 above, and on Mondays also step 7 (weekly source suggestions).

Suggested cron: `0 7 * * *` (daily 7am local). Weekly-suggestion branch keys off day-of-week inside the prompt.

---

## Weekly Source Suggestions Logic

Each Monday run, Claude proposes 2–3 candidate sources not already in the roster, chosen to (a) fill an underrepresented lean or topic area, or (b) add a credible voice adjacent to existing ones. Each suggestion: name, lean, one-line rationale, and accessibility pre-check (run the WebSearch probe before suggesting — never suggest a blocked source). Write to `suggestions/YYYY-MM-DD.json` and surface on the dashboard. David replies yes/no to Jarvis, who edits `sources.json` accordingly.

---

## Org / Compliance Notes

- Content is public news; no Protected or Confidential data involved. No DPA concerns.
- Analysis must stay **neutral and descriptive** per David's choice and org evenhandedness rules. The correlation label explains divergence; it does not adjudicate truth.
- All source fetching goes through approved Claude tools (`WebSearch`). No scraping, no `curl`/`requests` to fetch blocked content — that path is prohibited and also fails in-sandbox anyway.

---

## Resolved with David (2026-06-20)

1. **Topical seed searches:** CONFIRMED — the four beat searches (immigration, economy, foreign policy, elections) are a required part of every harvest, run across the full accessible domain set after the per-source pass.
2. **Gap parity:** CONFIRMED — each side surfaces at least as many gap topics as shared topics; dashboard size may grow to satisfy this.

## Resolved with David (2026-07-14)

3. **Double scan:** CONFIRMED — every source (plus the beat searches) is scanned twice, consecutively, in every run before clustering or scoring. Pass 2 is not conditional on pass 1 missing something; it always runs.
4. **Relevance decay:** CONFIRMED — a topic seen for 2+ consecutive days scores progressively lower on a separate 0–100 relevance scale (100 new → 20 floor by day 4+), tracked in a new persisted `topic_history.json`. New topics score highest; repeated topics score lower but are never fully suppressed by relevance alone.

## Open Questions (non-blocking — sensible defaults chosen)

1. **History/trends:** Keep run JSONs indefinitely for future trend charts (e.g. "correlation on immigration over time")? Default: keep them.
2. **Daily vs weekday-only:** Run 7 days or weekdays only? Default: daily.

---

## Implementation Steps (Ordered, for Rigby)

### Phase 1 — Source registry
1. Re-run the accessibility probe (`WebSearch` per domain) for every source; record `accessible` true/false.
2. Rewrite `sources.json` to the recommended roster: add `search_domain` and `accessible` fields; set the verified accessible set active.

### Phase 2 — Pipeline scripts
3. Repurpose `fetch.py` → `cluster.py`: remove RSS fetching; keep clustering + payload schema; input is `harvest.json`, output is `clusters.json`.
4. Build `render.py`: reads a `runs/YYYY-MM-DD.json`, emits `dashboard.html` per the layout above. Test with a hand-built sample run JSON first.

### Phase 3 — Run workflow
5. Author the run workflow (a `workflows/political-monitor/workflow.md` or a skill) encoding steps 1–6: harvest via WebSearch → write harvest.json → cluster.py → Claude analysis → write run JSON → render.py.
6. Do one **live end-to-end run** with real WebSearch data. Verify: shared topics show real L/R framing, correlation numbers are sane against the rubric, gap panels populate, dashboard renders cleanly in a browser.

### Phase 4 — Schedule + suggestions
7. Create the daily scheduled task (`0 7 * * *`) with a self-contained prompt; include the Monday weekly-suggestion branch.
8. Implement the weekly source-suggestion step with the pre-suggestion accessibility probe.

### Phase 5 — Docs + commit
9. Write `README.md` (how to add/mute a source, run manually, where outputs land).
10. Commit everything per `skills/git/SKILL.md`.

---

## Acceptance Criteria

- [ ] `sources.json` lists only accessible sources as active; blocked ones flagged, not fetched.
- [ ] A scheduled daily run produces a fresh `dashboard.html` with no manual steps.
- [ ] Shared topics render side-by-side L/R with a 0–100 correlation score + one-line neutral label.
- [ ] Gap topics show one-sided coverage in two clearly labeled panels.
- [ ] Every item has a one-paragraph neutral summary and working source link(s).
- [ ] Muted/blocked desired sources (e.g. NYT) are shown with a "not machine-readable" note.
- [ ] Monday runs append 2–3 vetted (accessibility-checked) source suggestions David can accept/reject.
- [ ] Analysis is descriptive/neutral throughout — no adjudication of which side is correct.
- [ ] Dashboard opens standalone in a browser with no broken layout or dead links.
- [ ] Every run scans all accessible sources plus beat searches **twice, consecutively**, merging/deduping into one `harvest.json` before clustering or scoring.
- [ ] Every topic (shared and gap) carries a `days_seen` / `relevance` pair computed against `topic_history.json`; new topics score 100, topics on their 2nd+ consecutive day score progressively lower per the rubric, with a floor of 20.
- [ ] `topic_history.json` persists across runs, is updated every run, and is pruned of entries stale for more than 5 days.
- [ ] Shared and gap topic lists are ordered by relevance descending, and each card shows a NEW / Day-N badge.

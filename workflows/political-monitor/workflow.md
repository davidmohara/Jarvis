---
name: political-monitor
description: Daily build of the political news monitor - scan all sources twice consecutively via WebSearch, cluster, analyze L/R framing with a 0-100 correlation score plus a relevance score that decays for topics repeated across consecutive days, surface gap topics, render the Watchtower dashboard. Mondays also propose new sources.
agent: rigby
model: sonnet
---

<!-- system:start -->
# Political News Monitor - Run Workflow

**Goal:** Produce a fresh `dashboard.html` that shows, neutrally, how the left and the right are covering the same stories (side-by-side framing + a 0-100 correlation score) and which topics only one side is covering.

**Owner:** Rigby (Platform Infrastructure).

**System dir:** `systems/political-monitor/` (sandbox mount: `/sessions/.../mnt/IES/systems/political-monitor/`).

**Build spec (authoritative):** `specs/political-monitor.md`. Read it if anything here is ambiguous.

**Hard rules:**
- Fetch ONLY via the `WebSearch` tool with `allowed_domains`. RSS-from-sandbox 403s; never use it. Never `curl`/`requests` a blocked outlet.
- Fetch only sources where `active` AND `accessible` are both true in `sources.json`.
- **Every source (and every beat search) is scanned twice, consecutively, every run — no exceptions.** This happens before clustering or scoring; it is not a retry-on-failure, it always runs.
- Analysis stays neutral and descriptive. The correlation label explains divergence in framing; it never says which side is right.
- Every topic (shared and gap) gets a `relevance` score from `topic_history.json`: new topics score high; topics seen on 2+ consecutive days score progressively lower. Scoring happens before deciding what makes the final dashboard ordering.
- Public news only. No Protected/Confidential data is involved.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

## Steps

### 1. Load the roster
Read `systems/political-monitor/sources.json`. Build the fetch list: every source where `active==true AND accessible==true`. Note the `sources_muted` list (active-desired but `accessible==false`, e.g. NYT) for the dashboard.

### 2. Harvest via WebSearch — TWO consecutive passes

**Pass 1.** For each fetch-list source, call:
`WebSearch(query="politics", allowed_domains=["<search_domain>"])`
Collect title, url, and a one-line raw snippet for recent items (last 48-72h). If a call returns `400 ... not accessible`, the site now blocks the crawler: flag it, set its `accessible:false` in `sources.json`, move it to muted, and continue.

Then run the four REQUIRED beat searches across the full accessible domain set (these are mandatory every run — they are how gap parity gets met):
`WebSearch(query="immigration policy <month year>", allowed_domains=[<all accessible domains>])`
`WebSearch(query="economy inflation jobs <month year>", allowed_domains=[...])`
`WebSearch(query="foreign policy <lead conflict> <month year>", allowed_domains=[...])`
`WebSearch(query="2026 midterm elections primaries campaign <month year>", allowed_domains=[...])`
Add 1-2 more seeds for the day's biggest stories as needed.

**Pass 2.** Immediately repeat the exact same sweep — same per-source queries, same beat searches, same candidate seeds. This is mandatory every run, not a fallback for a thin pass 1. Pages update between calls, so pass 2 catches new items and confirms the ones pass 1 already found.

**Merge.** Combine both passes, dedupe by `url`. For each surviving item, set `seen_passes: 2` if it appeared in both passes, `seen_passes: 1` if only one. Keep both; do not drop single-pass items.

### 3. Write harvest.json
Write `systems/political-monitor/harvest.json` in this shape:
```json
{ "generated": "<ISO8601>", "window_hours": 72,
  "items": [ { "source": "CNN Politics", "source_id": "cnn", "lean": "left",
               "title": "...", "url": "https://...", "summary_raw": "...", "seen_passes": 2 } ] }
```
Keep only items inside the window. Dedupe obvious repeats.

### 4. Pre-cluster
Run `python3 systems/political-monitor/cluster.py --hours 72`. It writes `clusters.json` (loose keyword grouping; `is_shared` flags clusters with both left and right). This is a HINT, not the final grouping.

### 5. Analyze (this is the real work - Claude does it)
Read `clusters.json` AND `harvest.json`. Do the authoritative SEMANTIC clustering yourself - the script under-merges short headlines, so re-group by actual topic. Then:

- **Shared topics** (left AND right both cover it): a one-paragraph neutral summary of the event; `left.framing` and `right.framing` (how each side covers it, with source links); a `correlation` 0-100 and a one-line neutral `correlation_label`.
- **Correlation rubric:** 85-100 same facts+framing; 65-84 agree on facts, diverge on emphasis; 40-64 same event, materially different framing; 20-39 sharply divergent narratives; 0-19 effectively two different stories.
- **gap_left / gap_right:** topics covered by exactly one side (center coverage does not disqualify a gap). One-paragraph summary + sources each. **Parity rule:** each side must have AT LEAST as many gap topics as there are shared topics (`gap_left >= shared`, `gap_right >= shared`). If you're short, mine the beat searches harder before settling. Total size may grow.
- **Relevance (score before deciding what to present):** read `systems/political-monitor/topic_history.json`. For every topic (shared, gap_left, gap_right) compute a `topic_key` (slug of its 3-5 most distinctive keywords) and semantically match it against history entries whose `last_seen` is the previous run date. Match → `days_seen = history.days_seen + 1`; no match → `days_seen = 1`. Then `relevance = max(20, 100 - (days_seen - 1) * 30)`, with `relevance_label`: day1 "New — first appearance", day2 "Recurring — day 2", day3 "Recurring — day 3, losing novelty", day4+ "Long-running — persistent story, low novelty". Sort `shared_topics`, `gap_left`, `gap_right` each by `relevance` descending. Rewrite `topic_history.json`: update matched entries (`last_seen`, `days_seen`, `title_latest`), add new entries for `days_seen==1` topics, and prune any entry whose `last_seen` is more than 5 days old.
- Write `systems/political-monitor/runs/YYYY-MM-DD.json` matching the schema in the spec, including `topic_key`, `days_seen`, `relevance`, `relevance_label` on every topic.
- `counts` **must use these exact keys** (the render script hard-validates them and will abort if any are missing or wrong type):
  ```json
  "counts": {
    "total_items": <int>,
    "by_lean": { "left": <int>, "right": <int>, "center": <int> },
    "shared_topics": <int>,
    "gap_left": <int>,
    "gap_right": <int>
  }
  ```
  Do not use `items_harvested`, `shared`, or any other key names. These are the only accepted field names.
- Fill `sources_used`, `sources_muted`, `generated`, `window_hours`.

### 6. Render + validate
Run `python3 systems/political-monitor/render.py systems/political-monitor/runs/YYYY-MM-DD.json`. The script runs a **hard schema validation before rendering** — if it exits with code 1, read the error output, fix the run JSON, and re-run. Do not proceed to step 7 until render exits cleanly with `✓ Schema validation passed`. Confirm the written `dashboard.html` has shared cards with gauges and relevance badges, both gap panels ordered by relevance, the muted-source note, and working links.

### 7. (Mondays only) Weekly source suggestions
If today is Monday: propose 2-3 candidate sources NOT already in the roster that fill an underrepresented lean or beat. For EACH candidate, run the accessibility probe first:
`WebSearch(query="politics", allowed_domains=["<candidate_domain>"])` - a `400` means blocked; never suggest a blocked source.
Write the vetted candidates (name, lean, search_domain, one-line rationale, accessible:true) to `systems/political-monitor/suggestions/YYYY-MM-DD.json`, and also add them to the run JSON's `suggestions` array before step 6 so they render on the dashboard. David replies "add X" / "skip X" to Jarvis, who edits `sources.json`.

### 8. Cleanup + commit
`harvest.json` and `clusters.json` are transient (gitignored). `topic_history.json` is NOT transient — it is the cross-day memory that makes relevance decay work; always commit it. Commit `sources.json` changes, `topic_history.json`, the new `runs/*.json`, any `suggestions/*.json`, and `dashboard.html` via `skills/git/SKILL.md`. Suggested message: `chore(rigby): political-monitor daily run YYYY-MM-DD`.

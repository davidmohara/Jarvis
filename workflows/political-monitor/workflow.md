---
name: political-monitor
description: Daily build of the political news monitor - harvest both-sides coverage via WebSearch, cluster, analyze L/R framing with a 0-100 correlation score, surface gap topics, render the Watchtower dashboard. Mondays also propose new sources.
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
- Analysis stays neutral and descriptive. The correlation label explains divergence in framing; it never says which side is right.
- Public news only. No Protected/Confidential data is involved.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

## Steps

### 1. Load the roster
Read `systems/political-monitor/sources.json`. Build the fetch list: every source where `active==true AND accessible==true`. Note the `sources_muted` list (active-desired but `accessible==false`, e.g. NYT) for the dashboard.

### 2. Harvest via WebSearch
For each fetch-list source, call:
`WebSearch(query="politics", allowed_domains=["<search_domain>"])`
Collect title, url, and a one-line raw snippet for recent items (last 48-72h). If a call returns `400 ... not accessible`, the site now blocks the crawler: flag it, set its `accessible:false` in `sources.json`, move it to muted, and continue.

Then run the four REQUIRED beat searches across the full accessible domain set (these are mandatory every run — they are how gap parity gets met):
`WebSearch(query="immigration policy <month year>", allowed_domains=[<all accessible domains>])`
`WebSearch(query="economy inflation jobs <month year>", allowed_domains=[...])`
`WebSearch(query="foreign policy <lead conflict> <month year>", allowed_domains=[...])`
`WebSearch(query="2026 midterm elections primaries campaign <month year>", allowed_domains=[...])`
Add 1-2 more seeds for the day's biggest stories as needed.

### 3. Write harvest.json
Write `systems/political-monitor/harvest.json` in this shape:
```json
{ "generated": "<ISO8601>", "window_hours": 72,
  "items": [ { "source": "CNN Politics", "source_id": "cnn", "lean": "left",
               "title": "...", "url": "https://...", "summary_raw": "..." } ] }
```
Keep only items inside the window. Dedupe obvious repeats.

### 4. Pre-cluster
Run `python3 systems/political-monitor/cluster.py --hours 72`. It writes `clusters.json` (loose keyword grouping; `is_shared` flags clusters with both left and right). This is a HINT, not the final grouping.

### 5. Analyze (this is the real work - Claude does it)
Read `clusters.json` AND `harvest.json`. Do the authoritative SEMANTIC clustering yourself - the script under-merges short headlines, so re-group by actual topic. Then write `systems/political-monitor/runs/YYYY-MM-DD.json` matching the schema in the spec:
- **Shared topics** (left AND right both cover it): a one-paragraph neutral summary of the event; `left.framing` and `right.framing` (how each side covers it, with source links); a `correlation` 0-100 and a one-line neutral `correlation_label`.
- **Correlation rubric:** 85-100 same facts+framing; 65-84 agree on facts, diverge on emphasis; 40-64 same event, materially different framing; 20-39 sharply divergent narratives; 0-19 effectively two different stories.
- **gap_left / gap_right:** topics covered by exactly one side (center coverage does not disqualify a gap). One-paragraph summary + sources each. **Parity rule:** each side must have AT LEAST as many gap topics as there are shared topics (`gap_left >= shared`, `gap_right >= shared`). If you're short, mine the beat searches harder before settling. Total size may grow.
- Fill `counts`, `sources_used`, `sources_muted`, `generated`, `window_hours`.

### 6. Render
Run `python3 systems/political-monitor/render.py systems/political-monitor/runs/YYYY-MM-DD.json`. It writes `dashboard.html`. Confirm it has shared cards with gauges, both gap panels, the muted-source note, and working links.

### 7. (Mondays only) Weekly source suggestions
If today is Monday: propose 2-3 candidate sources NOT already in the roster that fill an underrepresented lean or beat. For EACH candidate, run the accessibility probe first:
`WebSearch(query="politics", allowed_domains=["<candidate_domain>"])` - a `400` means blocked; never suggest a blocked source.
Write the vetted candidates (name, lean, search_domain, one-line rationale, accessible:true) to `systems/political-monitor/suggestions/YYYY-MM-DD.json`, and also add them to the run JSON's `suggestions` array before step 6 so they render on the dashboard. David replies "add X" / "skip X" to Jarvis, who edits `sources.json`.

### 8. Cleanup + commit
`harvest.json` and `clusters.json` are transient (gitignored). Commit `sources.json` changes, the new `runs/*.json`, any `suggestions/*.json`, and `dashboard.html` via `skills/git/SKILL.md`. Suggested message: `chore(rigby): political-monitor daily run YYYY-MM-DD`.

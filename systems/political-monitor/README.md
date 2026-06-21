# Political News Monitor

Tracks how the Democratic-leaning and Republican-leaning press cover the news. Each run digests recent items into one-paragraph neutral summaries, presents topics both sides cover **side by side** with a **0-100 correlation score** (how closely the two sides report it as the same story), and surfaces **gap topics** that only one side is covering. Output is a self-contained `dashboard.html`.

Analysis is descriptive and even-handed: the correlation label explains *why* framing diverges, never which side is correct.

## What runs

A daily scheduled task (07:00 local) rebuilds the dashboard with no manual steps, following `workflows/political-monitor/workflow.md`. On Mondays it also proposes 2-3 new candidate sources for David to approve or reject.

## Pipeline

```
sources.json  --(WebSearch per accessible domain)-->  harvest.json
harvest.json  --(cluster.py: keyword pre-clustering)-->  clusters.json
clusters.json + harvest.json  --(Claude: summaries, L/R framing, correlation, gaps)-->  runs/YYYY-MM-DD.json
runs/YYYY-MM-DD.json  --(render.py)-->  dashboard.html
```

The Python does mechanical work (loose keyword clustering, HTML rendering). Claude does the reasoning (semantic clustering, summaries, side-by-side framing, correlation scoring, gap detection) at run time.

## Files

| File | Role |
|------|------|
| `sources.json` | Source registry. `lean`, `active`, `accessible`, `search_domain`. Committed. |
| `cluster.py` | Loose keyword pre-clustering. Reads `harvest.json`, writes `clusters.json`. |
| `render.py` | Run JSON -> `dashboard.html`. |
| `harvest.json` | Transient - this run's raw WebSearch items. Gitignored. |
| `clusters.json` | Transient - pre-clustered output. Gitignored. |
| `runs/YYYY-MM-DD.json` | Analyzed digest per run. Kept for history/trends. |
| `suggestions/YYYY-MM-DD.json` | Weekly source suggestions + accept/reject status. |
| `dashboard.html` | The deliverable David opens. |

## Sourcing constraint (important)

RSS polling from the sandbox returns 403 for every feed - it is not used. Fetching happens through Claude's `WebSearch` tool scoped to one domain at a time (`allowed_domains`). Many major outlets (NYT, WaPo, Politico, Vox, WSJ, NY Post, AP, Reuters, BBC) block Anthropic's crawler and return `400 - domain not accessible`. Those are kept in `sources.json` as `accessible:false` and shown on the dashboard under a "not machine-readable" note so it is clear why they are not contributing. Bot policies drift, so the workflow re-probes on every run and on every Monday suggestion.

**Current active + accessible roster (10):**
- Left: MSNBC, CNN, NBC News, The Hill
- Right: Fox News, National Review, Washington Examiner, The Federalist, The Daily Wire
- Center: The Free Press

## Add a source

1. Probe it: `WebSearch(query="politics", allowed_domains=["<domain>"])`. A `400` means blocked - do not add it.
2. If it returns results, add a row to `sources.json`:
   ```json
   { "id": "slug", "name": "Display Name", "lean": "left|right|center",
     "active": true, "accessible": true, "search_domain": "example.com", "rss": "" }
   ```
3. It is picked up on the next run.

## Mute a source

Set `"active": false` in `sources.json` (keeps the row for history). To mark a source the crawler can no longer reach, set `"accessible": false` - it then renders under the muted note instead of being fetched.

## Run manually

From the system directory:
```bash
# 1. (Claude) harvest via WebSearch -> write harvest.json
python3 cluster.py --hours 72          # -> clusters.json
# 2. (Claude) analyze -> write runs/YYYY-MM-DD.json
python3 render.py runs/YYYY-MM-DD.json  # -> dashboard.html
```
Or just tell Jarvis "run the political monitor" and the full workflow executes.

## Where outputs land

`dashboard.html` in this directory is the current view. Historical analyzed runs accumulate in `runs/`. Weekly suggestions land in `suggestions/`.

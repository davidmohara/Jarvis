---
name: pipeline-snapshot
description: >
  Pull a weekly pipeline health snapshot for Dallas, TX and South Texas (One Texas) from the
  Improving Sales Analytics PowerBI report. Primary data source for grading Rock 1 (Revenue
  Visibility). Reports total pipeline and 90-day weighted pipeline side-by-side for both regions.
  Trigger on /pipeline-snapshot, "pipeline snapshot", "pipeline health", "rock 1 data", or
  "90 day pipeline".
owning_agent: chase
model: sonnet
trigger_keywords: [pipeline, deal status, revenue snapshot, crm]
trigger_agents: [chase]
---

# Pipeline Snapshot

## Purpose

Pull pipeline data for Dallas, TX and South Texas from the Improving Sales Analytics
PowerBI report. This is the primary grading source for Rock 1 (Revenue Visibility):
"Jarvis pulls account trajectory data weekly; Rock 1 graded on actuals, not feel."

**Scope: One Texas only** — Dallas, TX and South Texas. Do not report all-Improving totals.

Two pages pulled on every run:
1. **Pipeline Analytics** — total pipeline, stage breakdown, opportunity type mix
2. **90 Day Weighted Pipeline** — weighted pipeline within 90-day close window (primary Rock 1 metric)

Note: South Texas = Austin + Houston combined in PowerBI slicer terminology.

---

## Phase 0 — Cache Check (Run First)

**Freshness threshold: 7 days** (pipeline changes daily; weekly cadence is the intended pull frequency).

1. Read `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` via `mcp__obsidian-local__get_vault_file`.
   (Pipeline health data is stored here alongside co-sell — see the `### Pipeline Health (Rock 1)` section.)

2. Find the most recent `## Week of YYYY-MM-DD — Pipeline Snapshot` entry. Parse its
   `*Pulled: YYYY-MM-DD*` date.

3. If `pulled_date` >= today minus 7 days: **use cache**.
   - Extract the Pipeline Health (Rock 1) section from the most recent snapshot.
   - Output in standard format below, noting the snapshot date.
   - Report: `[Chase/Pipeline]: Using cached data from {pulled_date} (within 7-day window). Skipping PowerBI pull.`
   - **Stop here.**

4. If stale: proceed to Phase 1.

---

## Phase 1 — Navigate to Pipeline Analytics, Filter to Dallas, TX

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/ReportSection7e20c80e361d6cc45eed?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 5 seconds. Confirm page title contains "Power BI".

Click the Dallas, TX slicer item:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === 'Dallas, TX') { span.click(); return 'clicked Dallas'; }
  }
  return 'not found';
})()
```

Wait 2 seconds. Read KPI tiles and stage breakdown from DOM:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  return document.body.innerText.substring(0, 5000);
})()
```

Read:
- **Total Pipeline Revenue** (KPI tile)
- **Pipeline Opp Count** (KPI tile)
- **Weighted Pipeline Value** (KPI tile)
- **Pipeline by Probability Stage** table: 10%-Identified through 99%-Procurement, $ each
- **Pipeline by Opportunity Type**: New / Extension / Backfill, revenue + %

---

## Phase 2 — Filter to South Texas (same page)

South Texas = Austin, TX + Houston, TX. No "South Texas" slicer label exists — select both
cities. Deselect Dallas first, then select Houston, then Austin.

```js
mcp__Control_Chrome__execute_javascript
code: (function() {
  return new Promise((resolve) => {
    const items = document.querySelectorAll('.slicerItemContainer');
    for (const item of items) {
      if (item.getAttribute('title') === 'Dallas, TX' && item.getAttribute('aria-selected') === 'true') {
        item.querySelector('.slicerCheckbox')?.click();
      }
    }
    setTimeout(() => {
      const items2 = document.querySelectorAll('.slicerItemContainer');
      for (const item of items2) {
        if (item.getAttribute('title') === 'Houston, TX') item.querySelector('.slicerCheckbox')?.click();
      }
      setTimeout(() => {
        const items3 = document.querySelectorAll('.slicerItemContainer');
        for (const item of items3) {
          if (item.getAttribute('title') === 'Austin, TX') item.querySelector('.slicerCheckbox')?.click();
        }
        setTimeout(() => {
          const sel = Array.from(document.querySelectorAll('.slicerItemContainer'))
            .filter(i => i.getAttribute('aria-selected') === 'true')
            .map(i => i.getAttribute('title'));
          resolve('Selected: ' + sel.join(', '));
        }, 500);
      }, 400);
    }, 600);
  });
})()
```

Verify response shows Austin, TX + Houston, TX selected. Wait 2 seconds. Read same KPI values.

Note: Read Austin and Houston separately if the slicer supports single-select — navigate
to each city, read, then combine for South Texas total.

---

## Phase 3 — Navigate to 90 Day Weighted Pipeline, Filter to Dallas, TX

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/9f4623c483c060b75480?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 5 seconds. Click Dallas, TX slicer:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === 'Dallas, TX') { span.click(); return 'clicked Dallas'; }
  }
  return 'not found';
})()
```

Wait 2 seconds. Read from DOM:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  return document.body.innerText.substring(0, 5000);
})()
```

Read:
- **Weighted Pipeline Value** (90-day KPI tile)
- **Weighted Pipeline Opp Count** (KPI tile)
- **90-day pipeline by Probability Stage**: each stage $ value
- **90-day pipeline by Opportunity Type**: New / Extension / Backfill weighted values

---

## Phase 4 — Filter to South Texas (90-day page)

Same pattern as Phase 2 — deselect Dallas (600ms), select Houston (400ms), select Austin
(400ms). Verify selection. Read same 90-day values for South Texas.

For Austin and Houston separately: if the slicer is single-select, read each city
individually and combine for South Texas total.

---

## Phase 5 — Save to Obsidian and Output

Append the pipeline snapshot to `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` under
a new `## Week of [today] — Pipeline Snapshot` heading (or add `### Pipeline Health (Rock 1)`
subsection to an existing week entry if co-sell was already written today).

Use `mcp__obsidian-local__append_to_vault_file`.

Output using the standard format below.

---

## Output Format

```
## Pipeline Snapshot — Rock 1 — [Today's Date]

### 90-Day Weighted Pipeline (Primary Rock 1 Metric)

| Metric                        | Dallas, TX    | South Texas   | One Texas     |
|-------------------------------|---------------|---------------|---------------|
| 90-Day Weighted Value         | $X.XXM        | $X.XXM        | $X.XXM        |
| 90-Day Weighted Opp Count     | XXX           | XXX           | XXX           |

### Total Pipeline

| Metric                   | Dallas, TX    | South Texas   | One Texas     |
|--------------------------|---------------|---------------|---------------|
| Total Pipeline Revenue   | $X.XXM        | $X.XXM        | $X.XXM        |
| Pipeline Opp Count       | XXX           | XXX           | XXX           |
| Weighted Pipeline Value  | $X.XXM        | $X.XXM        | $X.XXM        |

### Pipeline by Probability Stage

| Stage                    | Dallas, TX    | South Texas   |
|--------------------------|---------------|---------------|
| 10%-Identified           | $X.XXM        | $X.XXM        |
| 25%-Qualified            | $X.XXM        | $X.XXM        |
| 50%-Proposing            | $X.XXM        | $X.XXM        |
| 75%-Positive Feedback    | $X.XXM        | $X.XXM        |
| 90%-Verbal               | $X.XXM        | $X.XXM        |
| 99%-Procurement          | $X.XXM        | $X.XXM        |
```

Follow with 2-3 sentences of Chase-voice commentary. Lead with the 90-day weighted number —
that is the Rock 1 grading metric, not total pipeline. Flag stage concentration risk if > 40%
of pipeline is at 10%-Identified. Note region imbalance if one side is significantly weaker.
Do not soften numbers.

---

## Notes

- **One Texas only** — never report all-Improving numbers.
- **South Texas = Austin, TX + Houston, TX** — no "South Texas" slicer label. Select both cities.
  Deselect Dallas first (600ms), then Houston (400ms), then Austin (400ms). Verify selection.
- Use `.slicerCheckbox` clicks — clicking the container directly hits the expand toggle.
- If KPI text not visible in body text after 2s, wait 3 more seconds and re-read.
- The 90-Day Weighted Pipeline is the Rock 1 metric. Lead with it. Total pipeline is context.
- **Escape key simulation**: `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))`

---

## Source

PowerBI report: Improving Sales Analytics — Pipeline Analytics
Pages: Pipeline Analytics, 90 Day Weighted Pipeline
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
Freshness threshold: 7 days
Auth: SSO (auto via Chrome session)
Rock 1 context: Revenue Visibility — "graded on actuals, not feel." One Texas only.

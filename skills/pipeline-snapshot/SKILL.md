---
name: pipeline-snapshot
description: >
  Pull a weekly pipeline health snapshot for Dallas, TX and South Texas (One Texas) from the
  Improving Sales Analytics PowerBI report. Primary data source for grading Rock 1 (Revenue
  Visibility). Reports total pipeline and 90-day weighted pipeline side-by-side for both regions.
  Trigger on /pipeline-snapshot, "pipeline snapshot", "pipeline health", "rock 1 data", or
  "90 day pipeline".
agent: chase
model: sonnet
---

# Pipeline Snapshot

## Purpose

Pull live pipeline data for Dallas, TX and South Texas from the Improving Sales Analytics
PowerBI report. This is the primary grading source for Rock 1 (Revenue Visibility): "Jarvis
pulls account trajectory data weekly; Rock 1 graded on actuals, not feel."

**Scope: One Texas only** — Dallas, TX and South Texas. Do not report all-Improving totals.

Two pages are pulled on every run:
1. **Pipeline Analytics** — total pipeline, stage breakdown, opportunity type mix
2. **90 Day Weighted Pipeline** — weighted pipeline within 90-day close window (primary Rock 1 metric)

Note: South Texas = Austin + Houston combined in PowerBI slicer terminology.

---

## Execution

### Step 1 — Navigate to Pipeline Analytics, Filter to Dallas, TX

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/ReportSection7e20c80e361d6cc45eed?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

SSO auto-authenticates. No manual login needed. Navigate directly to this URL — do NOT use
the mcas.ms variant or click through nav. The report loads in 3-5 seconds.

Take a screenshot to confirm KPI tiles and the enterprise slicer are visible before proceeding:

```
mcp__playwright__browser_take_screenshot
```

Click the Dallas, TX slicer item by text:

```js
mcp__playwright__browser_evaluate
function: () => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === 'Dallas, TX') { span.click(); return 'clicked'; }
  }
  return 'not found';
}
```

Take a screenshot and read the following values:

**KPI tiles:**
- Total Pipeline Revenue
- Pipeline Opp Count
- Weighted Pipeline Value

**Pipeline by Probability Stage table** (read each row present):
- 10%-Identified through 99%-Procurement

**Pipeline by Opportunity Type table:**
- New: revenue + % revenue
- Extension: revenue + % revenue
- Backfill: revenue + % revenue

### Step 2 — Filter to South Texas (same page)

South Texas = Austin, TX + Houston, TX selected simultaneously. There is no "South Texas" slicer
label — the report uses individual city names. Deselect Dallas first, then select both cities.
Use `.slicerCheckbox` clicks (not span clicks) to avoid hitting the expand toggle.

```js
mcp__Control_Chrome__execute_javascript
code: (function() {
  return new Promise((resolve) => {
    // Step 1: Deselect Dallas
    const items = document.querySelectorAll('.slicerItemContainer');
    for (const item of items) {
      if (item.getAttribute('title') === 'Dallas, TX' && item.getAttribute('aria-selected') === 'true') {
        item.querySelector('.slicerCheckbox')?.click();
      }
    }
    setTimeout(() => {
      // Step 2: Select Austin and Houston one at a time
      const items2 = document.querySelectorAll('.slicerItemContainer');
      for (const item of items2) {
        const t = item.getAttribute('title');
        if (t === 'Houston, TX') item.querySelector('.slicerCheckbox')?.click();
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

Wait 3 seconds after execution. Verify selection shows Austin, TX + Houston, TX before reading data.

Take a screenshot and read the same set of values: KPI tiles, stage breakdown, opportunity
type breakdown.

### Step 3 — Navigate to 90 Day Weighted Pipeline, Filter to Dallas, TX

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/84f84d9e-1283-4aad-8feb-b301bb819881/9f4623c483c060b75480?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 3-5 seconds for the page to load. Take a screenshot to confirm KPI tiles are visible.

Definition (for reference): "90 Day Weighted Pipeline is calculated as Est Revenue multiplied
by the Probability value with an Estimated Close Date between current date and 90 days from
current date."

Click Dallas, TX slicer:

```js
mcp__playwright__browser_evaluate
function: () => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === 'Dallas, TX') { span.click(); return 'clicked'; }
  }
  return 'not found';
}
```

Take a screenshot and read:

**KPI tiles:**
- Weighted Pipeline Value (90-day)
- Weighted Pipeline Opp Count

**90-day pipeline by Probability Stage table** (read each row present)

**90-day pipeline by Opportunity Type table:**
- New: weighted value + %
- Extension: weighted value + %
- Backfill: weighted value + %

### Step 4 — Filter to South Texas (same page)

Same pattern as Step 2 — deselect Dallas, then select Houston, TX then Austin, TX with 400ms
gaps between each click. See Step 2 for the full JS block. Verify selection before reading.

Take a screenshot and read the same values.

### Step 5 — Output Formatted Report

Compile all data and output the report using the format below.

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
that is the Rock 1 grading metric, not total pipeline. Flag stage concentration risk if more
than 40% of pipeline is at 10%-Identified (early-stage concentration means revenue is too far
out to matter this quarter). Note region imbalance if one side is significantly weaker.

Do not soften numbers. Do not reference past due opps — that is operational detail outside
David's scope on this rock.

---

## Notes

- **One Texas only** — never report all-Improving numbers. Always filter to Dallas TX or South
  Texas before reading KPI tiles.
- **South Texas = Austin, TX + Houston, TX** — there is no "South Texas" slicer label. Select both cities. Deselect Dallas first (600ms gap), then click Houston, then Austin (400ms gap each). Verify selection before reading.
- Slicer is multi-select. Read each region separately before navigating away.
- If KPI tiles are not visible after navigation, wait 2 seconds and screenshot again.
- The 90-Day Weighted Pipeline is the primary Rock 1 metric. Lead with it. Total pipeline is
  supporting context.

---

## Source

PowerBI report: Improving Sales Analytics — Pipeline Analytics
Pages: Pipeline Analytics, 90 Day Weighted Pipeline
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)
Rock 1 context: Revenue Visibility — "graded on actuals, not feel." One Texas only.

---
name: bookings-review
description: >
  Pull YTD bookings data for Dallas, TX and South Texas from the Improving Sales Analytics
  PowerBI report. Reports both regions side-by-side. Trigger when David says "bookings",
  "bookings review", "/bookings-review", or asks about YTD bookings for Dallas or South Texas.
agent: chase
---

# Bookings Review

## Purpose

Pull live YTD bookings data for Dallas, TX and South Texas from the Improving Sales Analytics
PowerBI report. Report both regions side-by-side using Playwright browser automation.

Note: South Texas = Austin + Houston combined in PowerBI slicer terminology. Output is
intentionally side-by-side only — bookings are not aggregated into a One Texas combined total.

---

## Execution

### Step 1 — Navigate Directly to Wins By Enterprise

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/61775932-91be-43e4-bb21-fd3354978687/ReportSection7e20c80e361d6cc45eed?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

SSO auto-authenticates. No manual login needed. Navigate directly to this URL — do NOT use
the mcas.ms variant or click through the nav, both cause unnecessary redirects or wrong-page
landings. The report loads in 3-5 seconds. Take a screenshot to confirm the enterprise slicer
is visible before proceeding.

```
mcp__playwright__browser_take_screenshot
```

### Step 2 — Read Dallas, TX

Click the Dallas, TX slicer item by text — more reliable than coordinates:

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

Then take a screenshot to capture the KPI tiles:

```
mcp__playwright__browser_take_screenshot
```

Read the following values from the screenshot:
- Bookings YTD
- Bookings (New) YTD
- Bookings (Extension) YTD
- Annual Bookings Target
- Sales amount needed to reach Target
- Opportunities Won
- On Target %

### Step 3 — Read South Texas

Click South Texas the same way:

```js
mcp__playwright__browser_evaluate
function: () => {
  const spans = document.querySelectorAll('span.slicerText');
  for (const span of spans) {
    if (span.textContent.trim() === 'South Texas') { span.click(); return 'clicked'; }
  }
  return 'not found';
}
```

Take a screenshot and read the same KPI values.

---

## Output Format

Report results as a side-by-side comparison table:

```
## YTD Bookings — [Today's Date]

| Metric                          | Dallas, TX   | South Texas  |
|---------------------------------|-------------|-------------|
| Bookings YTD                    | $X.XM        | $X.XM        |
| Bookings (New) YTD              | $X.XM        | $X.XM        |
| Bookings (Extension) YTD        | $X.XM        | $X.XM        |
| Annual Bookings Target          | $X.XM        | $X.XM        |
| Sales Needed to Hit Target      | $X.XM        | $X.XM        |
| Opportunities Won               | XX           | XX           |
| On Target %                     | XX%          | XX%          |
```

Follow with one sentence of Chase-voice commentary on combined trajectory or any region
significantly off-pace. If one region is at risk, say so directly.

---

## Notes

- The slicer is single-select — clicking one deselects the other. Slicer items are real DOM
  elements (`span.slicerText`) — do NOT use coordinate injection, which breaks when the
  slicer tree renders differently. Text-based selection is reliable across sessions.
- If `span.slicerText` returns `'not found'`, fall back to a text-content search:
  ```js
  mcp__playwright__browser_evaluate
  function: () => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.trim() === 'Dallas, TX') { el.click(); return 'clicked'; }
    }
    return 'not found';
  }
  ```
- Output is side-by-side only. Bookings are dollar amounts that could be summed, but the
  report format intentionally keeps them separate for regional clarity.

---

## Source

PowerBI report: Improving Sales Analytics — Sales Wins / Wins By Enterprise
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)

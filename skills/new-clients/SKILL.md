---
name: new-clients
description: >
  Pull New Logos & Anchors YTD counts from the Improving Enterprise Scorecard v4 PowerBI
  report. Reports Dallas and South Texas (Austin + Houston) separately, then combines for
  One Texas total. Trigger on /new-clients, "new logos", "new anchors", "new clients",
  or "logos and anchors".
agent: chase
---

# New Clients (New Logos & Anchors)

## Purpose

Pull YTD New Logos & Anchors counts for Dallas and South Texas from the Enterprise
Scorecard v4 Sales Momentum page. Report by enterprise, combine for One Texas total,
and compare against Q1 targets.

- **New Logo**: a brand-new client relationship
- **New Anchor**: a new strategic/anchor engagement
- South Texas = Austin + Houston

---

## Execution

### Step 1 — Navigate to Sales Momentum Page

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c72372fd0de36d82124?experience=power-bi
```

Wait 3-5 seconds. Take a screenshot to confirm the New Logos & Anchors chart is visible.

```
mcp__playwright__browser_take_screenshot
```

### Step 2 — Filter to Dallas, Read Data

Before hovering for tooltip data, confirm the page is at 71% zoom — that is the calibrated
state for the chart coordinates below. Check the zoom indicator in the bottom-right corner of
the page in the screenshot from Step 1. If zoom differs, adjust coordinates proportionally or
use the `Month Name [Month]` field in the tooltip to verify you're reading the correct point.

Run this single evaluate to open the dropdown, expand United States if needed, and
select Dallas. It handles all timing internally — no multi-step open/expand/reopen.

```js
mcp__playwright__browser_evaluate
function: () => {
  return new Promise((resolve) => {
    const wrappers = document.querySelectorAll('.slicer-content-wrapper');
    const dropdown = wrappers[1]?.querySelector('.slicer-dropdown-menu');
    if (!dropdown) return resolve('no dropdown');
    dropdown.click();

    const attempt = (tries) => {
      setTimeout(() => {
        const popups = document.querySelectorAll('[id^="slicer-dropdown-popup"]');
        let popup = null;
        for (const p of popups) {
          if (p.querySelectorAll('.slicerItemContainer').length > 0) { popup = p; break; }
        }
        if (!popup && tries > 0) return attempt(tries - 1);
        if (!popup) return resolve('popup never ready');

        const usItem = Array.from(popup.querySelectorAll('.slicerItemContainer'))
          .find(i => i.getAttribute('title') === 'United States');
        if (!usItem) return resolve('US not found');

        if (usItem.getAttribute('aria-expanded') !== 'true') {
          usItem.querySelector('.expandButton')?.click();
          setTimeout(() => { dropdown.click(); attempt(3); }, 400);
          return;
        }

        if (usItem.getAttribute('aria-selected') === 'true') {
          usItem.querySelector('.slicerCheckbox')?.click();
        }

        setTimeout(() => {
          const dallas = Array.from(popup.querySelectorAll('.slicerItemContainer'))
            .find(i => i.getAttribute('title') === 'Dallas');
          dallas?.querySelector('.slicerCheckbox')?.click();
          resolve('Dallas selected');
        }, 200);
      }, 400);
    };
    attempt(5);
  });
}
```

Close the dropdown:

```
mcp__playwright__browser_press_key
key: Escape
```

Now hover over the March cumulative data point in the New Logos & Anchors chart and
read the tooltip from the DOM. The chart March position is approximately (420, 515):

```js
mcp__playwright__browser_run_code
code: async (page) => {
  await page.mouse.move(420, 515);
  await page.waitForTimeout(800);
  return page.evaluate(() => {
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      const text = (div.innerText || '').replace(/\s+/g, ' ').trim();
      if (text.includes('Target Logos') && div.offsetWidth < 600) return text;
    }
    return null;
  });
}
```

The tooltip text contains:
- Company names prefixed with "Select Row" — count them per section for actual Logos/Anchors
- `Target Logos: N` — the cumulative Q1 logo target at March
- `Target Anchors: N` — the cumulative Q1 anchor target at March
- `Month Name Mar` — confirms you're reading March data

If March shows 0 for a region, check February (380, 515) and January (340, 525) to
confirm the cumulative totals from those months. The chart is cumulative — the most
recent month with data is the YTD total.

Record:
- Dallas Logos YTD = count of "Select Row" entries in the Logo section
- Dallas Anchors YTD = count of "Select Row" entries in the Anchor section
- Dallas Q1 Logo Target = value after "Target Logos:"
- Dallas Q1 Anchor Target = value after "Target Anchors:"

### Step 3 — Filter to South Texas (Austin + Houston), Read Data

```js
mcp__playwright__browser_evaluate
function: () => {
  return new Promise((resolve) => {
    const wrappers = document.querySelectorAll('.slicer-content-wrapper');
    const dropdown = wrappers[1]?.querySelector('.slicer-dropdown-menu');
    if (!dropdown) return resolve('no dropdown');
    dropdown.click();

    const attempt = (tries) => {
      setTimeout(() => {
        const popups = document.querySelectorAll('[id^="slicer-dropdown-popup"]');
        let popup = null;
        for (const p of popups) {
          if (p.querySelectorAll('.slicerItemContainer').length > 0) { popup = p; break; }
        }
        if (!popup && tries > 0) return attempt(tries - 1);
        if (!popup) return resolve('popup never ready');

        const items = popup.querySelectorAll('.slicerItemContainer');
        for (const item of items) {
          const title = item.getAttribute('title');
          const selected = item.getAttribute('aria-selected') === 'true';
          if (title === 'Dallas' && selected) item.querySelector('.slicerCheckbox')?.click();
          if ((title === 'Austin' || title === 'Houston') && !selected)
            item.querySelector('.slicerCheckbox')?.click();
        }
        resolve('South Texas selected');
      }, 400);
    };
    attempt(5);
  });
}
```

Close and hover March again:

```
mcp__playwright__browser_press_key
key: Escape
```

```js
mcp__playwright__browser_run_code
code: async (page) => {
  await page.mouse.move(420, 515);
  await page.waitForTimeout(800);
  return page.evaluate(() => {
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      const text = (div.innerText || '').replace(/\s+/g, ' ').trim();
      if (text.includes('Target Logos') && div.offsetWidth < 600) return text;
    }
    return null;
  });
}
```

Record South Texas Logos, Anchors, and targets the same way.

### Step 4 — Output Formatted Report

Compile Dallas and South Texas data and output using the format below.

---

## Output Format

```
## New Clients — One Texas — [Today's Date]

### New Logos & Anchors YTD

| Metric              | Dallas | South Texas | One Texas | Q1 Target      |
|---------------------|--------|-------------|-----------|----------------|
| New Logos YTD       | X      | X           | X         | X (DFW + STX)  |
| New Anchors YTD     | X      | X           | X         | X (DFW + STX)  |
| Total New Clients   | X      | X           | X         | —              |

### Gap to Target

| Metric              | Dallas | South Texas | One Texas |
|---------------------|--------|-------------|-----------|
| Logo Gap            | X      | X           | X         |
| Anchor Gap          | X      | X           | X         |

**Dallas logos:** [list company names from tooltip]
**South Texas logos:** [list company names, or "none"]
```

Follow with 2-3 sentences of Chase-voice commentary. Lead with One Texas total vs
target. Call out any enterprise at zero — that is a funnel problem, not a timing problem.
Do not soften the numbers.

---

## Notes

- The chart is **cumulative YTD** — the March data point represents total through March,
  not just March. Hover the latest month with data to get the YTD number.
- Count logos/anchors by counting "Select Row" occurrences in each section of the
  tooltip text. Zero "Select Row" entries = zero clients.
- Confirmed chart coordinates (Sales Momentum page, New Logos & Anchors chart, 71% zoom):
  - January: approximately (340, 525)
  - February: approximately (380, 515)
  - March: approximately (420, 515)
- If coordinates drift (page re-renders at different zoom), scan nearby y-values
  (±15px) and check for "Month Name Mar" in the tooltip to confirm the right point.
- The single Promise-based evaluate handles dropdown open, US expand, and city
  selection with built-in retry. Do not break it into separate steps.
- Tooltip persists in DOM after hover — always move mouse away between reads to
  avoid stale data.
- Q1 targets per enterprise differ (confirmed: Dallas Logo Q1=5, South Texas Logo Q1=4;
  both Anchor Q1=2 as of 2026).

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Sales Momentum (`3c72372fd0de36d82124`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)

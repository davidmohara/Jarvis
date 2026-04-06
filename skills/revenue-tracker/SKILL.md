---
name: revenue-tracker
description: >
  Pull enterprise revenue data from the Improving Enterprise Scorecard v4 Financial
  Outlook page. Reports Revenue vs. Target, Revenue vs. Prior Year, Sequential Quarterly
  Revenue, and Monthly Revenue for Dallas and South Texas (Austin + Houston) separately,
  then combines for One Texas total. Trigger on /revenue-tracker, "revenue tracker",
  "enterprise revenue", "revenue vs target", "financial outlook", or "scorecard revenue".
agent: chase
---

# Revenue Tracker

## Purpose

Pull live revenue performance data for Dallas and South Texas from the Enterprise
Scorecard v4 Financial Outlook page. Report by enterprise, then combine for One Texas.

Key metrics:
- **Revenue vs. Target**: Current Quarter %, Last Quarter %, YTD %
- **Revenue vs. Prior Year**: Current Quarter %, Last Quarter %, YTD %
- **Sequential Quarterly Revenue**: Current Quarter %, Previous Quarter %, 90-Day Forecast vs. Target %
- **Monthly Revenue**: most recent closed month $ from bar chart hover

Note: South Texas = Austin + Houston. One Texas = Dallas + South Texas combined.

---

## Execution

### Step 1 — Navigate to Financial Outlook Page

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c7c59c7edecc090aa27?experience=power-bi
```

Wait 3-5 seconds. Take a screenshot to confirm the KPI tiles are visible.

```
mcp__playwright__browser_take_screenshot
```

### Step 2 — Filter to Dallas, Read Data

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

Take a screenshot and read all KPI tile values directly from the image:

```
mcp__playwright__browser_take_screenshot
```

**KPI tiles — Revenue vs. Target:** Current Quarter %, Last Quarter %, YTD %

**KPI tiles — Revenue vs. Previous Year:** Current Quarter %, Last Quarter %, YTD %

**KPI tiles — Sequential Quarterly Revenue:** Current Quarter %, Previous Quarter %, 90-Day Forecast vs. Target %

Now hover to get the most recent month's revenue dollar figure:

```js
mcp__playwright__browser_run_code
code: async (page) => {
  await page.mouse.move(700, 450);
  await page.waitForTimeout(500);
  await page.mouse.move(396, 265);
  await page.waitForTimeout(1200);
  return page.evaluate(() => {
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      if (div.children.length > 0) continue;
      const text = (div.innerText || div.textContent || '').replace(/\s+/g, ' ').trim();
      if (text.includes('Month Name') && text.includes('Monthly Revenue')) return text;
    }
    return null;
  });
}
```

The tooltip returns: `Month Name [Month], Monthly Revenue $X`. Record the month name and dollar value.

Record:
- Dallas Revenue vs. Target: CQ %, LQ %, YTD %
- Dallas Revenue vs. Prior Year: CQ %, LQ %, YTD %
- Dallas Sequential Quarterly: CQ %, PQ %, 90-Day %
- Dallas Monthly Revenue: $X (Month)

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

Close and screenshot:

```
mcp__playwright__browser_press_key
key: Escape
```

```
mcp__playwright__browser_take_screenshot
```

Read KPI tiles and hover for monthly revenue the same way as Dallas.

### Step 4 — Output Formatted Report

Compile Dallas and South Texas data and output using the format below.

---

## Output Format

```
## Revenue Tracker — One Texas — [Today's Date]

### Revenue vs. Target

| Metric           | Dallas | South Texas | One Texas (simple avg) |
|------------------|--------|-------------|------------------------|
| Current Quarter  | X%     | X%          | X%                     |
| Last Quarter     | X%     | X%          | X%                     |
| YTD              | X%     | X%          | X%                     |

### Revenue vs. Prior Year

| Metric           | Dallas | South Texas | One Texas (simple avg) |
|------------------|--------|-------------|------------------------|
| Current Quarter  | X%     | X%          | X%                     |
| Last Quarter     | X%     | X%          | X%                     |
| YTD              | X%     | X%          | X%                     |

### Sequential Quarterly Revenue

| Metric                     | Dallas | South Texas |
|----------------------------|--------|-------------|
| Current Quarter            | X%     | X%          |
| Previous Quarter           | X%     | X%          |
| 90-Day Forecast vs. Target | X%     | X%          |

### Monthly Revenue ([Month])

| Metric          | Dallas | South Texas | One Texas |
|-----------------|--------|-------------|-----------|
| Monthly Revenue | $X.XM  | $X.XM       | $X.XM     |
```

One Texas columns use simple averages for % metrics (Dallas and South Texas are comparable
size — if that changes materially, weight by revenue instead). Monthly Revenue One Texas
= Dallas + South Texas sum.

Follow with 2-3 sentences of Chase-voice commentary. Lead with QTD Revenue vs. Target.
Call out any enterprise with a double miss (below target AND below prior year). Flag
any 90-Day Forecast below 90% — that means the gap isn't closing this quarter.
Do not soften misses.

---

## Notes

- **One Texas only** — never report all-Improving numbers. Always filter before reading.
- The single Promise-based evaluate handles open + expand + select with built-in retry.
  Do not break it into separate steps.
- KPI tiles are large and readable directly from the screenshot — no DOM scraping needed.
- Monthly Revenue tooltip: hover at (x≈396, y≈265), read leaf div containing "Month Name"
  and "Monthly Revenue $X". The most recent month with actual bar data is the last closed month.
- Always use `.slicerCheckbox` for clicks — clicking the treeitem directly hits the expand toggle.
- South Texas = Austin + Houston selected simultaneously in a single evaluate pass.

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Financial Outlook (`3c7c59c7edecc090aa27`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)

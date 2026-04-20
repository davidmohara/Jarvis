---
name: revenue-tracker
description: >
  Pull enterprise revenue data from the Improving Enterprise Scorecard v4 Financial
  Outlook page. Reports Revenue vs. Target, Revenue vs. Prior Year, Sequential Quarterly
  Revenue, and Monthly Revenue for Dallas and South Texas (Austin + Houston) separately,
  then combines for One Texas total. Trigger on /revenue-tracker, "revenue tracker",
  "enterprise revenue", "revenue vs target", "financial outlook", or "scorecard revenue".
owning_agent: chase
model: sonnet
trigger_keywords: [revenue, bookings, ats, target vs actual]
trigger_agents: [chase, quinn]
---

# Revenue Tracker

## Purpose

Pull revenue performance data for Dallas and South Texas from the Enterprise Scorecard v4
Financial Outlook page. Report by enterprise, then combine for One Texas.

Key metrics:
- **Revenue vs. Target**: Current Quarter %, Last Quarter %, YTD %
- **Revenue vs. Prior Year**: Current Quarter %, Last Quarter %, YTD %
- **Sequential Quarterly Revenue**: Current Quarter %, Previous Quarter %, 90-Day Forecast vs. Target %
- **Monthly Revenue**: most recent closed month $ from bar chart hover

Note: South Texas = Austin + Houston. One Texas = Dallas + South Texas combined.

---

## Phase 0 — Cache Check (Run First)

Before touching PowerBI, check if a fresh snapshot already exists in Obsidian.

**Freshness threshold: 30 days** (revenue data updates monthly when a new month closes).
Additionally: if today is past the 10th of a new month, the prior month has likely closed
and any snapshot from the prior month or earlier is stale regardless of age.

1. Read the Obsidian file via `mcp__obsidian-local__get_vault_file`:
   - filename: `Mind/One Texas/Rock 1 - Revenue Snapshots.md`

2. Find the most recent `## [Month] [Year] — Revenue Snapshot` entry. Parse its
   `*Pulled: YYYY-MM-DD*` date.

3. Determine if the cached data is current:
   - If `pulled_date` >= today minus 30 days AND the `Most Recent Closed Month` in the
     snapshot matches the most recently closed calendar month: **use cache**.
   - Otherwise: **refresh from PowerBI** (proceed to Phase 1).

4. **If using cache:**
   - Extract the revenue tables from the most recent snapshot entry.
   - Output the data in the standard Output Format below, noting the snapshot date.
   - Report: `[Chase/Revenue]: Using cached data from {pulled_date} (within freshness window). Skipping PowerBI pull.`
   - **Stop here. Do not proceed to Phase 1.**

---

## Phase 1 — Navigate to Financial Outlook Page

Open the PowerBI page in Chrome:

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c7c59c7edecc090aa27?experience=power-bi
```

Wait 5 seconds for SSO and page load. Confirm by checking the page title:

```js
mcp__Control_Chrome__execute_javascript
code: document.title
```

Expected: contains "Scorecard" or "Power BI". If the page shows a login screen, SSO
has not completed — wait 3 more seconds and re-check. If still not loaded after two
attempts, abort and report the failure.

---

## Phase 2 — Filter to Dallas, Read Data

Run this single evaluate to open the dropdown, expand United States if needed, and
select Dallas. It handles all timing internally — no multi-step open/expand/reopen.

```js
mcp__Control_Chrome__execute_javascript
code: new Promise((resolve) => {
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
})
```

Close the dropdown:

```js
mcp__Control_Chrome__execute_javascript
code: document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))
```

Wait 2 seconds, then read KPI tile values from the DOM:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const tiles = [];
  document.querySelectorAll('[class*="kpiVisual"], [class*="kpi-"], [class*="card"]').forEach(el => {
    const text = el.innerText?.trim();
    if (text) tiles.push(text);
  });
  // Also grab all visible numeric text that looks like % or $
  const allText = document.body.innerText;
  return { tiles, allText: allText.substring(0, 3000) };
})()
```

Read the KPI values from the returned text. The page shows:
- Revenue vs. Target: Current Quarter %, Last Quarter %, YTD %
- Revenue vs. Previous Year: Current Quarter %, Last Quarter %, YTD %
- Sequential Quarterly Revenue: Current Quarter %, Previous Quarter %, 90-Day Forecast %

Now hover to get the most recent month's revenue dollar figure. Move mouse to the
bar chart hover position (x≈396, y≈265) and read the tooltip div:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  // Simulate mousemove to trigger PowerBI tooltip
  const el = document.elementFromPoint(396, 265);
  if (el) {
    el.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: 396, clientY: 265}));
    el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true, clientX: 396, clientY: 265}));
  }
  // Read tooltip after brief delay — call again in 1.5s if needed
  return new Promise(resolve => setTimeout(() => {
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      if (div.children.length > 0) continue;
      const text = (div.innerText || div.textContent || '').replace(/\s+/g, ' ').trim();
      if (text.includes('Month Name') && text.includes('Monthly Revenue')) return resolve(text);
    }
    resolve(null);
  }, 1500));
})()
```

If tooltip returns null, try reading the bar chart labels directly from DOM text instead.
The most recent month with a non-zero bar is the last closed month.

Record:
- Dallas Revenue vs. Target: CQ %, LQ %, YTD %
- Dallas Revenue vs. Prior Year: CQ %, LQ %, YTD %
- Dallas Sequential Quarterly: CQ %, PQ %, 90-Day %
- Dallas Monthly Revenue: $X (Month)

---

## Phase 3 — Filter to South Texas, Read Data

```js
mcp__Control_Chrome__execute_javascript
code: new Promise((resolve) => {
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
})
```

Close, wait 2 seconds, read KPI tiles and hover for monthly revenue the same way as Phase 2.

Record:
- South Texas Revenue vs. Target: CQ %, LQ %, YTD %
- South Texas Revenue vs. Prior Year: CQ %, LQ %, YTD %
- South Texas Sequential Quarterly: CQ %, PQ %, 90-Day %
- South Texas Monthly Revenue: $X (Month) — also read Austin and Houston separately if visible

---

## Phase 4 — Save to Obsidian and Output

Append the new snapshot to `Mind/One Texas/Rock 1 - Revenue Snapshots.md` using
`mcp__obsidian-local__append_to_vault_file`. Use this header format:

```
## [Month YYYY] — Revenue Snapshot
*Pulled: YYYY-MM-DD | Source: Enterprise Scorecard v4 | Most Recent Closed Month: [Month YYYY]*
```

Then output the report using the standard format below.

---

## Output Format

```
## Revenue Tracker — One Texas — [Today's Date]

### Revenue vs. Target

| Metric          | Dallas | South Texas | One Texas (simple avg) |
|-----------------|--------|-------------|------------------------|
| Current Quarter | X%     | X%          | X%                     |
| Last Quarter    | X%     | X%          | X%                     |
| YTD             | X%     | X%          | X%                     |

### Revenue vs. Prior Year

| Metric          | Dallas | South Texas | One Texas (simple avg) |
|-----------------|--------|-------------|------------------------|
| Current Quarter | X%     | X%          | X%                     |
| Last Quarter    | X%     | X%          | X%                     |
| YTD             | X%     | X%          | X%                     |

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

One Texas % columns = simple average of Dallas and South Texas. Monthly Revenue One Texas
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
- KPI tile values: read from DOM text if screenshot not available. Look for large % values
  adjacent to section headers like "Revenue vs. Target".
- Monthly Revenue tooltip: trigger via mousemove/mouseenter dispatch at (x≈396, y≈265).
  If mousemove doesn't trigger tooltip, read bar chart axis labels from DOM as fallback.
- Always use `.slicerCheckbox` for clicks — clicking the treeitem directly hits the expand toggle.
- South Texas = Austin + Houston selected simultaneously in a single evaluate pass.
- **Escape key**: use `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))` instead of `mcp__playwright__browser_press_key`.

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Financial Outlook (`3c7c59c7edecc090aa27`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 1 - Revenue Snapshots.md`
Freshness threshold: 30 days (or new month closed since last pull)
Auth: SSO (auto via Chrome session)

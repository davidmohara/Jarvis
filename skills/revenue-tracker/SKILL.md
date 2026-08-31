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
- **Monthly Revenue**: most recent closed month $ from bar chart — **actual only (black bars)**

Note: South Texas = Austin + Houston. One Texas = Dallas + South Texas combined.

This skill delegates dropdown navigation and cache-check to shared skills. **The bar-color
(actual vs. forecast) and tooltip-hover value read is NOT delegated to `powerbi-extract-kpis`**
— inspecting SVG `rect` `fill` attributes to distinguish actual/backlog/pipeline bars, then
dispatching a mouse-hover at a computed coordinate to read the tooltip, is a materially
different and more fragile mechanic than a plain innerText/regex read. That logic stays
inline below, same as in `new-clients` for its chart-hover step.

### Bar Chart Color Encoding — Critical

The Monthly Revenue bar chart uses color to distinguish revenue type:
- **Black bars** = Actual recognized revenue. This is the only number that counts.
- **Blue bars** = Backlog (contracted but not yet recognized)
- **Gold/yellow bars** = Pipeline (not yet contracted)

A month with blue or gold bars — even if it has a visible bar height — is **forecast, not
actual**. Do not report it as revenue. The most recent closed month is the last month whose
bar is entirely black (no blue/gold component). Months with mixed or blue/gold-only bars
are in-progress or future — ignore them for the Monthly Revenue figure.

---

## Phase 0 — Cache Check (Run First)

Call `skills/vault-freshness-check/SKILL.md` with:
```
vault_file: "Mind/One Texas/Rock 1 - Revenue Snapshots.md"
entry_heading_pattern: "^## \[?(\w+ \d{4})\]? — Revenue Snapshot"
date_field_pattern: "\*Pulled: (\d{4}-\d{2}-\d{2})"
freshness_threshold_days: 30
extra_staleness_rule: "if today is past the 10th of a new calendar month, treat any snapshot whose 'Most Recent Closed Month' field doesn't match the most recently closed calendar month as stale regardless of age — the prior month has likely closed since the snapshot was taken"
caller_label: "Chase/Revenue"
```

If `cache_status: "hit"` — output `extracted_text` in the standard format below, noting
the snapshot date, report the message the skill returns, and **stop here**.

If `"stale"` or `"not_found"` — proceed to Phase 1.

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

This is `skills/powerbi-navigate-slicer/SKILL.md`'s `dropdown-nested` pattern
(`select: [{label: "Dallas", parent: "United States"}]`) — reproduced here as the raw
script since a validation step immediately follows it:

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

**VALIDATION STEP — Verify Dallas filter is applied before proceeding:**

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const allText = document.body.innerText;
  const lines = allText.split('\n');
  const buLine = lines.find(l => l.includes('Business Unit') || l.includes('Dallas'));
  return buLine || allText.substring(0, 1000);
})()
```

Verify the returned text contains "Dallas" explicitly (should show "Dallas (Enterprise)" or
similar). If it shows "Multiple selections" or any city other than Dallas, **abort and retry
Phase 2**. Do not proceed to KPI extraction if the filter is not Dallas-only. (This is the
same filter-verification discipline `powerbi-navigate-slicer`'s `verify_after` option
provides generically — reproduced here inline because this report's specific validation
text — "Business Unit" — is report-specific.)

Wait 2 seconds, then read KPI tile values from the DOM. This part **can** use
`skills/powerbi-extract-kpis/SKILL.md` with `mode: "tile-scan"`:
```
mode: "tile-scan"
```
which returns the same shape as:
```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const tiles = [];
  document.querySelectorAll('[class*="kpiVisual"], [class*="kpi-"], [class*="card"]').forEach(el => {
    const text = el.innerText?.trim();
    if (text) tiles.push(text);
  });
  const allText = document.body.innerText;
  return { tiles, allText: allText.substring(0, 3000) };
})()
```

Read the KPI values from the returned text. The page shows:
- Revenue vs. Target: Current Quarter %, Last Quarter %, YTD %
- Revenue vs. Previous Year: Current Quarter %, Last Quarter %, YTD %
- Sequential Quarterly Revenue: Current Quarter %, Previous Quarter %, 90-Day Forecast %

Now identify the most recent **actual** (black bar) month and get its revenue figure.

**Step 1 — Identify actual vs. forecast bars by SVG fill color:**

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const svgs = document.querySelectorAll('svg');
  for (const svg of svgs) {
    if (!(svg.textContent || '').includes('Jan')) continue;
    const rects = Array.from(svg.querySelectorAll('rect'));
    const bars = rects
      .map(r => {
        const fill = (r.getAttribute('fill') || r.style?.fill || '').toLowerCase();
        const computedFill = window.getComputedStyle(r).fill || '';
        return {
          x: Math.round(parseFloat(r.getAttribute('x') || 0)),
          y: Math.round(parseFloat(r.getAttribute('y') || 0)),
          h: Math.round(parseFloat(r.getAttribute('height') || 0)),
          w: Math.round(parseFloat(r.getAttribute('width') || 0)),
          fill: fill || computedFill.substring(0, 40),
        };
      })
      .filter(b => b.h > 10 && b.w > 5 && b.w < 60)
      .sort((a, b) => a.x - b.x);
    if (bars.length > 0) return bars;
  }
  return 'no bar chart found';
})()
```

Inspect the `fill` values returned:
- Bars with dark/black fill (e.g. `rgb(0,0,0)`, `#000`, `#1a1a1a`, or similar dark colors) = **actual revenue** ✓
- Bars with blue fill (e.g. `rgb(0,112,192)`, `#0070c0`, or similar) = backlog — **skip**
- Bars with gold/yellow fill (e.g. `rgb(255,192,0)`, `#ffc000`, or similar) = pipeline — **skip**

The last month (rightmost x position) whose bar is black is the most recently closed month.
Record that month and its bar height for value calculation.

**Step 2 — Get the dollar value via tooltip hover on the black bar:**

Move mouse to the x-center of the most recent black bar (use its `x + w/2` and a
y-coordinate in the middle of the chart, approximately y≈265 in screen space):

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const el = document.elementFromPoint(396, 265);
  if (el) {
    el.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: 396, clientY: 265}));
    el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true, clientX: 396, clientY: 265}));
  }
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

**Step 3 — Fallback if tooltip returns null:**

If the tooltip doesn't render, estimate the value from bar height using the SVG scale:
- Determine the plot baseline (y-coordinate of the $0 line = max y+h of any bar)
- Determine the axis max from DOM text ($1M, $2M, $3M, etc.)
- Value ≈ `(bar.h / baseline_height) * axis_max`
- Flag the result as approximate: `~$X.XM (estimated from bar height)`
- **Only perform this calculation on black bars.** Do not estimate forecast bar values.

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
(This is `powerbi-navigate-slicer`'s `dropdown-nested` multi-leaf variant, reproduced here
inline alongside the report-specific validation step that follows.)

**VALIDATION STEP — Verify South Texas filter is applied before proceeding:**

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const allText = document.body.innerText;
  const lines = allText.split('\n');
  const buLine = lines.find(l => l.includes('Business Unit') || l.includes('Austin') || l.includes('Houston'));
  return buLine || allText.substring(0, 1000);
})()
```

Verify the returned text contains both "Austin" and "Houston" or shows a state like "Texas"
or similar (should indicate both cities are selected, not Dallas or "Multiple selections").
If it shows Dallas, "All", or "Multiple selections", **abort and retry Phase 3**. Do not
proceed to KPI extraction if the filter is not Austin + Houston only.

Close, wait 2 seconds, read KPI tiles and identify the most recent black bar for monthly
revenue the same way as Phase 2. Apply the same color rule: black = actual, blue/gold =
forecast, skip forecast.

Record:
- South Texas Revenue vs. Target: CQ %, LQ %, YTD %
- South Texas Revenue vs. Prior Year: CQ %, LQ %, YTD %
- South Texas Sequential Quarterly: CQ %, PQ %, 90-Day %
- South Texas Monthly Revenue: $X (Month, actual/black bar only) — also read Austin and Houston separately if visible

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
- **Black bars = actual. Blue/gold bars = forecast. Never report forecast bars as revenue.**
  The current in-progress month will have blue/gold bars because it hasn't closed yet. The most
  recently closed month is the last month with a fully black bar. If you're unsure which month
  that is, read SVG rect fill colors via `window.getComputedStyle(r).fill` and filter for dark/black.
- The single Promise-based evaluate handles open + expand + select with built-in retry.
  Do not break it into separate steps.
- KPI tile values: read from DOM text if screenshot not available. Look for large % values
  adjacent to section headers like "Revenue vs. Target".
- Monthly Revenue tooltip: trigger via mousemove/mouseenter dispatch at (x≈396, y≈265).
  If mousemove doesn't trigger tooltip, fall back to bar-height estimation — but only on black bars.
- Always use `.slicerCheckbox` for clicks — clicking the treeitem directly hits the expand toggle.
- South Texas = Austin + Houston selected simultaneously in a single evaluate pass.
- **Escape key**: use `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))` instead of `mcp__playwright__browser_press_key`.
- **CRITICAL — Filter Validation (from err-20260727T143315-NTKXRY):** Never assume filter application succeeded. After each filter selection (Phase 2 and Phase 3), validate the filter state by reading the Business Unit label from the DOM. If the filter does not match the intended enterprise or cities, abort and retry. Proceeding with KPI extraction from an incorrectly filtered view produces incorrect data. Always confirm "Dallas" (Phase 2) or "Austin + Houston" (Phase 3) before reading any KPI values.

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Financial Outlook (`3c7c59c7edecc090aa27`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Mechanics: `skills/powerbi-navigate-slicer/SKILL.md` (dropdown-nested navigation),
`skills/powerbi-extract-kpis/SKILL.md` (tile-scan mode for KPI %s),
`skills/vault-freshness-check/SKILL.md`, `skills/eval-signal-write/SKILL.md`.
Bar-color inspection and tooltip-hover value read stay inline in this skill (see scope note in Purpose).
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 1 - Revenue Snapshots.md`
Freshness threshold: 30 days (or new month closed since last pull)
Auth: SSO (auto via Chrome session)

## SKILL COMPLETE

After the skill's final output is delivered, call `skills/eval-signal-write/SKILL.md` with:
```
skill_name: "revenue-tracker"
agent: "chase"
trigger: "manual"   (or "boot"/"scheduled" per the calling context)
started: <actual start time of this run>
completed: <actual completion time>
status: "success"   (or "partial"/"failure" as appropriate)
tool_failures: 0
error_ids: []
```
This call is always the final action.

After that, also write a working memory file to `memory/working/` using this filename pattern:

```
revenue-tracker-YYYY-MM-DD-HHmmss.md
```

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chase-{YYYY-MM-DD}-{HHmmss}"
agent-source: chase
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Revenue tracker snapshot — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

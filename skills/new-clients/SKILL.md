---
name: new-clients
description: >
  Pull New Logos & Anchors YTD counts from the Improving Enterprise Scorecard v4 PowerBI
  report. Reports Dallas and South Texas (Austin + Houston) separately, then combines for
  One Texas total. Trigger on /new-clients, "new logos", "new anchors", "new clients",
  or "logos and anchors".
owning_agent: chase
model: sonnet
trigger_keywords: [new client, onboard, kickoff]
trigger_agents: [chase, chief]
---

# New Clients (New Logos & Anchors)

## Purpose

Pull YTD New Logos & Anchors counts for Dallas and South Texas from the Enterprise
Scorecard v4 Sales Momentum page. Report by enterprise, combine for One Texas total,
and compare against the current quarter's targets.

- **New Logo**: a brand-new client relationship
- **New Anchor**: a new strategic/anchor engagement
- South Texas = Austin + Houston

## Runtime: Determine Current Quarter and Latest Month

Before doing anything else, determine today's date and derive:

- `current_quarter` = Q1 (Jan–Mar), Q2 (Apr–Jun), Q3 (Jul–Sep), or Q4 (Oct–Dec)
- `latest_month` = the most recent completed month (e.g., if today is June 22, latest_month = May)
- `latest_month_name` = short name used in tooltip confirmation (e.g., "May")
- `latest_month_x` = approximate x-coordinate for that month on the cumulative chart at 71% zoom

**Chart x-coordinate map (71% zoom, cumulative bar chart):**

| Month | Approx x |
|-------|----------|
| Jan   | 340      |
| Feb   | 380      |
| Mar   | 420      |
| Apr   | 460      |
| May   | 500      |
| Jun   | 540      |
| Jul   | 580      |
| Aug   | 620      |
| Sep   | 660      |
| Oct   | 700      |
| Nov   | 740      |
| Dec   | 780      |

The y-coordinate is approximately 515 for all months. If the tooltip returns null at the computed x, scan ±20px on x and confirm via `Month Name {latest_month_name}` in the tooltip text.

Hover the **latest completed month** — that data point gives the YTD cumulative total.

**Annual targets (2026, One Texas):**

| Metric         | Q1 cumulative | Q2 cumulative | Q3 cumulative | Annual |
|----------------|---------------|---------------|---------------|--------|
| Dallas Logos   | 5             | 10 (est)      | 15 (est)      | 20     |
| STX Logos      | 4             | 8 (est)       | 12 (est)      | 16     |
| Dallas Anchors | 2             | 2             | 3             | 3      |
| STX Anchors    | 2             | 2             | 3             | 3      |

Use the cumulative target for the current quarter when reporting gap. If the PowerBI tooltip shows a `Target Logos` or `Target Anchors` value, use that in preference to the table above.

---

## Phase 0 — Cache Check (Run First)

**Freshness threshold: 30 days** (new logos/anchors update monthly with closed periods;
within a quarter the cumulative count only increases when a new logo/anchor closes).

1. Read `Mind/One Texas/One Texas Scorecard Tracking.md` via `mcp__obsidian-local__get_vault_file`.

2. Find the most recent dated entry (format: `## YYYY-MM-DD`). Look for the
   `### New Clients` section within it. Parse the entry date.

3. If `entry_date` >= today minus 30 days: **use cache**.
   - Extract the New Logos & Anchors data from that entry.
   - Output in standard format below, noting the snapshot date.
   - Report: `[Chase/NewClients]: Using cached data from {entry_date} (within 30-day window). Skipping PowerBI pull.`
   - **Stop here.**

4. If stale: proceed to Phase 1.

---

## Phase 1 — Navigate to Sales Momentum Page

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c72372fd0de36d82124?experience=power-bi
```

Wait 5 seconds. Confirm page title contains "Power BI" or "Scorecard".

---

## Phase 2 — Filter to Dallas, Read Data

Run the dropdown selector to choose Dallas:

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

Wait 2 seconds. Now hover over the **latest completed month** data point in the New Logos & Anchors chart.
Use `latest_month_x` computed above (e.g., May = x≈500, Jun = x≈540). Dispatch mouse events:

```js
mcp__Control_Chrome__execute_javascript
code: new Promise(resolve => {
  const el = document.elementFromPoint(420, 515);
  if (el) {
    el.dispatchEvent(new MouseEvent('mouseover', {bubbles: true, clientX: 420, clientY: 515}));
    el.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: 420, clientY: 515}));
  }
  setTimeout(() => {
    const allDivs = document.querySelectorAll('div');
    for (const div of allDivs) {
      const text = (div.innerText || '').replace(/\s+/g, ' ').trim();
      if (text.includes('Target Logos') && div.offsetWidth < 600) return resolve(text);
    }
    resolve(null);
  }, 1500);
})
```

The tooltip text contains:
- Company names prefixed with "Select Row" — count them per section for actual Logos/Anchors
- `Target Logos: N` — cumulative YTD logo target at that month
- `Target Anchors: N` — cumulative YTD anchor target at that month
- `Month Name {month}` — confirms you're reading the right month

If tooltip returns null at `latest_month_x`, step back one month (subtract ~40px on x) and retry.
The chart is cumulative — always hover the latest month with data to get the full YTD total.

If mouse dispatch doesn't trigger tooltips, fall back to reading all visible body text:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  // Look for tooltip-like divs with logo/anchor data
  const candidates = [];
  document.querySelectorAll('div').forEach(div => {
    const text = (div.innerText || '').trim();
    if (text.includes('Logo') || text.includes('Anchor')) candidates.push(text.substring(0, 300));
  });
  return candidates.slice(0, 20);
})()
```

Record:
- Dallas Logos YTD = count of "Select Row" entries in the Logo section
- Dallas Anchors YTD = count of "Select Row" entries in the Anchor section
- Dallas Logo Target (cumulative YTD) = value after "Target Logos:" in tooltip, or use runtime table above
- Dallas Anchor Target (cumulative YTD) = value after "Target Anchors:" in tooltip, or use runtime table above

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

Close and hover the same `latest_month_x` coordinate again for South Texas. Record South Texas Logos, Anchors, and targets.

---

## Phase 4 — Save to Obsidian and Output

Append the new clients data to `Mind/One Texas/One Texas Scorecard Tracking.md` under
a new dated entry section using `mcp__obsidian-local__append_to_vault_file`.

Output using the standard format below.

---

## Output Format

```
## New Clients — One Texas — [Today's Date]

### New Logos & Anchors YTD (through [latest_month_name] [YYYY])

| Metric              | Dallas | South Texas | One Texas | [current_quarter] Target  |
|---------------------|--------|-------------|-----------|---------------------------|
| New Logos YTD       | X      | X           | X         | X (DFW + STX)             |
| New Anchors YTD     | X      | X           | X         | X (DFW + STX)             |
| Total New Clients   | X      | X           | X         | —                         |

### Gap to Target

| Metric              | Dallas | South Texas | One Texas |
|---------------------|--------|-------------|-----------|
| Logo Gap            | X      | X           | X         |
| Anchor Gap          | X      | X           | X         |

**Dallas logos:** [list company names from tooltip, or "none"]
**South Texas logos:** [list company names, or "none"]
```

Substitute `[latest_month_name]`, `[YYYY]`, and `[current_quarter]` with actual runtime values before outputting.

Follow with 2-3 sentences of Chase-voice commentary. Lead with One Texas total vs target.
Call out any enterprise at zero — that is a funnel problem, not a timing problem.
Do not soften the numbers.

---

## Notes

- The chart is **cumulative YTD** — hover the latest completed month to get the full YTD total.
  Do not hover the current partial month — it will undercount.
- Count logos/anchors by counting "Select Row" entries in each section of the tooltip.
  Zero "Select Row" entries = zero clients that period.
- Chart x-coordinates (71% zoom, y≈515 for all): Jan≈340, Feb≈380, Mar≈420, Apr≈460, May≈500, Jun≈540, Jul≈580, Aug≈620, Sep≈660, Oct≈700, Nov≈740, Dec≈780.
  If coordinates drift, scan ±20px on x and confirm month via `Month Name {name}` in tooltip.
- Mouse dispatch via Chrome: use `mouseover` + `mousemove` events. If tooltip doesn't appear,
  try `mouseenter` at the same coordinates.
- Tooltip persists in DOM after hover — move mouse away before switching regions to clear stale data:
  ```js
  mcp__Control_Chrome__execute_javascript
  code: (() => {
    const el = document.elementFromPoint(100, 100);
    el?.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: 100, clientY: 100}));
  })()
  ```
- Annual targets (2026): Dallas Logos=20, STX Logos=16, Dallas Anchors=3, STX Anchors=3.
  Cumulative quarterly targets are in the Runtime section above. Always use tooltip `Target Logos/Anchors` values if present — they take precedence.
- **Escape key**: `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))`

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Sales Momentum (`3c72372fd0de36d82124`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/One Texas Scorecard Tracking.md`
Freshness threshold: 30 days
Auth: SSO (auto via Chrome session)

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/new-clients-latest.json
```

Content:
```json
{
  "skill": "new-clients",
  "agent": "chase",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

After writing the signal file, also write a working memory file to `memory/working/` using this filename pattern:

```
new-clients-YYYY-MM-DD-HHmmss.md
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
context: "New clients snapshot — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.


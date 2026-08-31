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
and compare against Q1 targets.

- **New Logo**: a brand-new client relationship
- **New Anchor**: a new strategic/anchor engagement
- South Texas = Austin + Houston

This skill delegates navigation and cache-check to shared skills. **KPI extraction is
NOT delegated to `powerbi-extract-kpis`** — this report requires hovering a chart data
point to trigger a tooltip and reading its rendered text, which is a materially different
mechanic (synthetic mouse-event dispatch at coordinates, not a plain innerText/regex read)
from the KPI-tile extraction that skill covers. That logic stays inline below.

---

## Phase 0 — Cache Check (Run First)

Call `skills/vault-freshness-check/SKILL.md` with:
```
vault_file: "Mind/One Texas/One Texas Scorecard Tracking.md"
entry_heading_pattern: "^## (\d{4}-\d{2}-\d{2})"
freshness_threshold_days: 30
extract_section_heading: "### New Clients"
caller_label: "Chase/NewClients"
```

If `cache_status: "hit"` — output `extracted_text` in the standard format below, noting
the snapshot date, report the message the skill returns, and **stop here**.

If `"stale"` or `"not_found"` — proceed to Phase 1.

---

## Phase 1 — Navigate to Sales Momentum Page

Call `skills/powerbi-navigate-slicer/SKILL.md` with:
```
report_url: "https://app.powerbi.com/groups/me/reports/ff2db561-1548-4c6f-ae43-a3a927bd73e3/3c72372fd0de36d82124?experience=power-bi"
connector: "chrome"
slicer_pattern: "dropdown-nested"
select: [{label: "Dallas", parent: "United States"}]
```
This performs the open-dropdown, expand-United-States-if-needed, select-Dallas sequence
in one call (see Phase 2 for the raw script this wraps, kept here for reference since the
chart-hover step immediately after needs the dropdown fully closed).

Wait 5 seconds. Confirm page title contains "Power BI" or "Scorecard".

---

## Phase 2 — Filter to Dallas, Read Data

`powerbi-navigate-slicer`'s `dropdown-nested` pattern handles the underlying script:

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

Wait 2 seconds. Now hover over the March data point in the New Logos & Anchors chart.
The chart position at 71% zoom is approximately (420, 515) for March. Dispatch mouse events:

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
- `Target Logos: N` — cumulative Q1 logo target at March
- `Target Anchors: N` — cumulative Q1 anchor target at March
- `Month Name Mar` — confirms you're reading March data

If tooltip returns null, try February (x≈380, y≈515) or January (x≈340, y≈525).
The chart is cumulative — most recent month with data = YTD total.

If mouse dispatch doesn't trigger tooltips, fall back to reading all visible body text
(this fallback *is* the shape `powerbi-extract-kpis`'s `tile-scan` mode covers, so you may
call that skill with `mode: "tile-scan"` here instead of hand-rolling the query):

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
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
- Dallas Q1 Logo Target = value after "Target Logos:"
- Dallas Q1 Anchor Target = value after "Target Anchors:"

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
(This is `powerbi-navigate-slicer`'s `dropdown-nested` multi-leaf variant — see that
skill's SKILL.md for the parameterized template if driving a different report's dropdown.)

Close and hover March again the same way. Record South Texas Logos, Anchors, and targets.

---

## Phase 4 — Save to Obsidian and Output

Append the new clients data to `Mind/One Texas/One Texas Scorecard Tracking.md` under
a new dated entry section using `mcp__obsidian-local__append_to_vault_file`.

Output using the standard format below.

---

## Output Format

```
## New Clients — One Texas — [Today's Date]

### New Logos & Anchors YTD (through March 2026)

| Metric              | Dallas | South Texas | One Texas | Q1 Target         |
|---------------------|--------|-------------|-----------|-------------------|
| New Logos YTD       | X      | X           | X         | 9 (5 DFW + 4 STX) |
| New Anchors YTD     | X      | X           | X         | 4 (2 DFW + 2 STX) |
| Total New Clients   | X      | X           | X         | —                 |

### Gap to Target

| Metric              | Dallas | South Texas | One Texas |
|---------------------|--------|-------------|-----------|
| Logo Gap            | X      | X           | X         |
| Anchor Gap          | X      | X           | X         |

**Dallas logos:** [list company names from tooltip, or "none"]
**South Texas logos:** [list company names, or "none"]
```

Follow with 2-3 sentences of Chase-voice commentary. Lead with One Texas total vs target.
Call out any enterprise at zero — that is a funnel problem, not a timing problem.
Do not soften the numbers.

---

## Notes

- The chart is **cumulative YTD** — the March data point is the YTD total through March.
  Hover the latest month with data to get the full YTD number.
- Count logos/anchors by counting "Select Row" entries in each section of the tooltip.
  Zero "Select Row" entries = zero clients that period.
- Confirmed chart coordinates (71% zoom): January ≈ (340, 525), February ≈ (380, 515), March ≈ (420, 515).
  If coordinates drift (page re-renders), scan ±15px on y-axis and confirm via `Month Name Mar`.
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
- Q1 targets (confirmed 2026): Dallas Logo Q1=5, South Texas Logo Q1=4; both Anchor Q1=2.
- **Escape key**: `document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))`

---

## Source

PowerBI report: Improving Enterprise Scorecard v4
Page: Sales Momentum (`3c72372fd0de36d82124`)
Report ID: `ff2db561-1548-4c6f-ae43-a3a927bd73e3`
Mechanics: `skills/powerbi-navigate-slicer/SKILL.md` (dropdown-nested navigation),
`skills/vault-freshness-check/SKILL.md`, `skills/eval-signal-write/SKILL.md`.
Chart-tooltip hover extraction stays inline in this skill (see scope note in Purpose).
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/One Texas Scorecard Tracking.md`
Freshness threshold: 30 days
Auth: SSO (auto via Chrome session)

## SKILL COMPLETE

After the skill's final output is delivered, call `skills/eval-signal-write/SKILL.md` with:
```
skill_name: "new-clients"
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

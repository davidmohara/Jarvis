---
name: co-sell-pipeline
description: >
  Pull live co-sell pipeline and won data from the Improving Sales Analytics PowerBI report.
  Reports pipeline revenue and opps by partner, won revenue and opps by partner, and gap to
  Rock 4's $15M co-sell pipeline target. Trigger on /co-sell-pipeline, "co-sell", "cosell",
  "partner pipeline", or "rock 4 pipeline".
owning_agent: chase
model: sonnet
trigger_keywords: [co-sell, partner pipeline, microsoft, cosell]
trigger_agents: [chase]
---

# Co-Sell Pipeline

## Purpose

Pull co-sell pipeline and won revenue data from the Improving Sales Analytics PowerBI
report. Surface partner-level breakdown, progress toward Rock 4's $15M target, and gap
remaining. David tracks this against two key partners: Microsoft (SME&C, John Yurewicz) and
Confluent (Nick Larson and Dante).

Rock 4 target: **$15M co-sell pipeline** by end of Q2 2026.

Gap formula: `$15M - Pipeline Revenue - Won Revenue = Remaining Gap`

---

## Phase 0 — Cache Check (Run First)

**Freshness threshold: 7 days** (co-sell pipeline changes weekly with deal activity).

1. Read `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` via `mcp__obsidian-local__get_vault_file`.

2. Find the most recent `## Week of YYYY-MM-DD — Pipeline Snapshot` entry. Parse its
   `*Pulled: YYYY-MM-DD*` date.

3. If `pulled_date` >= today minus 7 days: **use cache**.
   - Extract the Co-Sell Pipeline (Rock 4) section from the most recent snapshot.
   - Output in standard format below, noting the snapshot date.
   - Report: `[Chase/CoSell]: Using cached data from {pulled_date} (within 7-day window). Skipping PowerBI pull.`
   - **Stop here.**

4. If stale: proceed to Phase 1.

---

## Phase 1 — Navigate to Coselling Partner Pipeline Page

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/8a62865681ae18b5ec9b?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Navigate directly to this URL — do NOT use the mcas.ms variant. Wait 5 seconds for SSO
and page load. Confirm title contains "Power BI".

---

## Phase 2 — Read Pipeline Data

Read KPI tiles and partner table from the DOM:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const text = document.body.innerText;
  return text.substring(0, 4000);
})()
```

Read the following from the page text:
- **Pipeline Revenue w/ Coselling Partner** (total $ amount KPI tile)
- **Pipeline Opps w/ Coselling Partner** (total count KPI tile)
- **Partner breakdown table**: partner name, revenue amount, opp count for each row
  (Microsoft, Confluent, SAP, Scrum.org, and any others present)
- **Quarter/Year table** (bottom right) — confirms the report period

If KPI tiles are not visible in the text, wait 3 seconds and re-read.

---

## Phase 3 — Navigate to Won Coselling Partner Opps Page

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/57bac82f202223c91446?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 5 seconds.

---

## Phase 4 — Set Date Filter and Read Won Data

The Won page has an "Actual Close Date" slider. Set it to full-year 2026.
**Critical: change end date BEFORE start date** — changing start date first breaks the filter.

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const inputs = document.querySelectorAll('input.date-slicer-date');
  if (inputs.length >= 2) {
    // End date first
    inputs[1].focus();
    inputs[1].select();
    inputs[1].value = '12/31/2026';
    inputs[1].dispatchEvent(new Event('change', {bubbles: true}));
    inputs[1].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
    // Start date second
    setTimeout(() => {
      inputs[0].focus();
      inputs[0].select();
      inputs[0].value = '1/1/2026';
      inputs[0].dispatchEvent(new Event('change', {bubbles: true}));
      inputs[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
    }, 500);
    return 'date filter set';
  }
  return 'inputs not found: ' + inputs.length;
})()
```

Wait 2 seconds, then read Won data from DOM:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  return document.body.innerText.substring(0, 4000);
})()
```

Read:
- **Won Revenue w/ Coselling Partner** (total $ KPI tile)
- **Won Opps w/ Coselling Partner** (total count KPI tile)
- **Partner breakdown table**: partner name, won revenue, won opp count

---

## Phase 5 — Save to Obsidian and Output

Append the co-sell section to `Mind/One Texas/Rock 4 - Pipeline Snapshots.md` under
a new `## Week of [today] — Pipeline Snapshot` heading using
`mcp__obsidian-local__append_to_vault_file`.

Calculate gap: `$15,000,000 - Pipeline Revenue - Won Revenue = Remaining Gap`

Output using the standard format below.

---

## Output Format

```
## Co-Sell Pipeline — Rock 4 Progress — [Today's Date]
**Report period: [Quarter/Year from page filter]**

### Pipeline vs Won by Partner

| Partner       | Pipeline Revenue | Pipeline Opps | Won Revenue | Won Opps |
|---------------|-----------------|---------------|-------------|----------|
| Microsoft     | $XXX,XXX        | X             | $XXX,XXX    | X        |
| Confluent     | $XXX,XXX        | X             | $XXX,XXX    | X        |
| SAP           | $XXX,XXX        | X             | $XXX,XXX    | X        |
| Scrum.org     | $XXX,XXX        | X             | $XXX,XXX    | X        |
| **Total**     | **$X,XXX,XXX**  | **XX**        | **$XXX,XXX**| **XX**   |

### Rock 4 Gap

| Metric                        | Amount          |
|-------------------------------|-----------------|
| Target                        | $15,000,000     |
| Pipeline Revenue              | $X,XXX,XXX      |
| Won Revenue                   | $XXX,XXX        |
| **Remaining Gap**             | **$XX,XXX,XXX** |
| Gap % remaining               | XX%             |
```

Follow with 2-3 sentences of Chase-voice commentary. David owns the co-sell pipeline —
address gaps to him directly. If gap > $10M: call it critical and name which partner
channels need more activity. Do not soften numbers. Do not suggest partner contacts
(Nick Larson, John Yurewicz) are responsible — David is.

---

## Notes

- Both pages use direct URL navigation — no in-report nav clicks needed.
- If the page lands on the wrong tab, use DOM text-click fallback:
  ```js
  mcp__Control_Chrome__execute_javascript
  code: (() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.trim() === 'Coselling Partner Pipeline') { el.click(); return 'clicked'; }
    }
    return 'not found';
  })()
  ```
- Quarter/Year table in bottom right confirms the report period. Always include in output header.
- Gap = pipeline + won combined against $15M. Both count toward Rock 4.

---

## Source

PowerBI report: Improving Sales Analytics — Co-Sell Pipeline
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
Freshness threshold: 7 days
Auth: SSO (auto via Chrome session)
Rock 4 Target: $15M co-sell pipeline by end of Q2 2026

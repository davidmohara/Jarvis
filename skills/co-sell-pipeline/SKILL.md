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

## Phase 2 — Disaggregate Pipeline Data by One Texas Enterprise

**CRITICAL: Do NOT read the aggregate "Improving, Enterprise" KPI. Disaggregate by clicking each location filter.**

One Texas consists of three enterprises: **Dallas, Houston, and Austin**. The report's default view shows an aggregate that masks critical execution differences across enterprises. You MUST gather individual numbers for each enterprise and sum them.

### Phase 2a — Check Filter State

First, determine which location is currently selected:

```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  const locations = ['Dallas, TX', 'Houston, TX', 'Austin, TX'];
  const result = [];
  
  for (const location of locations) {
    for (const el of document.querySelectorAll('[class*="slicerText"]')) {
      if (el.textContent?.trim() === location) {
        const container = el.closest('[class*="slicerItemContainer"]');
        const checkbox = container?.querySelector('[class*="slicerCheckbox"]');
        const isSelected = checkbox?.className.includes('selected');
        result.push({location, isSelected});
        break;
      }
    }
  }
  
  return result;
})()
```

This returns array showing which location is currently selected. Note which one is selected (will have `isSelected: true`).

### Phase 2b — Click Each Location and Record Pipeline KPIs

For each location (Dallas, Houston, Austin), click its checkbox and read the KPI values:

**For Dallas, TX:**
```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  for (const el of document.querySelectorAll('[class*="slicerText"]')) {
    if (el.textContent?.trim() === 'Dallas, TX') {
      const container = el.closest('[class*="slicerItemContainer"]');
      const checkbox = container?.querySelector('[class*="slicerCheckbox"]');
      if (checkbox) checkbox.click();
      break;
    }
  }
  
  // Wait for update, then read KPIs
  return new Promise(resolve => {
    setTimeout(() => {
      const text = document.body.innerText;
      const revMatch = text.match(/Pipeline Revenue w\/.*?Partner\s*\$([\d,]+)/);
      const opsMatch = text.match(/Pipeline Opps w\/.*?Partner\s*(\d+)/);
      resolve({
        location: 'Dallas, TX',
        pipelineRevenue: revMatch ? revMatch[1] : 'not found',
        pipelineOpps: opsMatch ? opsMatch[1] : 'not found'
      });
    }, 2000);
  });
})()
```

**For Houston, TX:** (click Houston checkbox, wait 2s, read KPIs same way)

**For Austin, TX:** (click Austin checkbox, wait 2s, read KPIs same way)

Record all three readings. You will sum these at the end.

---

## Phase 3 — Navigate to Won Coselling Partner Opps Page

```
mcp__Control_Chrome__open_url
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/57bac82f202223c91446?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 5 seconds for page load.

---

## Phase 4 — Disaggregate Won Data by One Texas Enterprise

Same as Phase 2: the Won page shows an aggregate KPI by default. You MUST disaggregate by clicking each location filter and recording individual won revenue numbers.

### Phase 4a — Click Each Location and Record Won KPIs

**For Dallas, TX:**
```js
mcp__Control_Chrome__execute_javascript
code: (() => {
  for (const el of document.querySelectorAll('[class*="slicerText"]')) {
    if (el.textContent?.trim() === 'Dallas, TX') {
      const container = el.closest('[class*="slicerItemContainer"]');
      const checkbox = container?.querySelector('[class*="slicerCheckbox"]');
      if (checkbox) checkbox.click();
      break;
    }
  }
  
  return new Promise(resolve => {
    setTimeout(() => {
      const text = document.body.innerText;
      const revMatch = text.match(/Won Revenue w\/.*?Partner\s*\$([\d,]+)/);
      const opsMatch = text.match(/Won Opps w\/.*?Partner\s*(\d+)/);
      resolve({
        location: 'Dallas, TX',
        wonRevenue: revMatch ? revMatch[1] : '$0',
        wonOpps: opsMatch ? opsMatch[1] : '0'
      });
    }, 2000);
  });
})()
```

**For Houston, TX:** (click Houston checkbox, wait 2s, read KPIs same way)

**For Austin, TX:** (click Austin checkbox, wait 2s, read KPIs same way)

Record all three readings. You will sum these with the pipeline data to calculate the true Rock 4 gap.

---

## Phase 5 — Calculate and Output

### Sum Enterprise Data

Add the three enterprise readings:
- **Total Pipeline Revenue** = Dallas + Houston + Austin pipeline
- **Total Pipeline Opps** = Dallas + Houston + Austin opps  
- **Total Won Revenue** = Dallas + Houston + Austin won
- **Total Won Opps** = Dallas + Houston + Austin opps

### Calculate Rock 4 Gap

```
Remaining Gap = $15,000,000 - (Pipeline Revenue + Won Revenue)
Gap % = (Remaining Gap / $15,000,000) * 100
```

### Output Format

```
## Co-Sell Pipeline — Rock 4 Progress — [Today's Date]
**Report period: 2026 YTD (One Texas: Dallas + Houston + Austin disaggregated)**

### Pipeline vs Won by Enterprise

| Enterprise   | Pipeline Revenue | Pipeline Opps | Won Revenue | Won Opps |
|--------------|-----------------|---------------|------------|----------|
| Dallas       | $XXX,XXX        | X             | $XXX,XXX   | X        |
| Houston      | $XXX,XXX        | X             | $XXX,XXX   | X        |
| Austin       | $XXX,XXX        | X             | $XXX,XXX   | X        |
| **Total**    | **$X,XXX,XXX**  | **XX**        | **$XXX,XXX** | **XX**  |

### Rock 4 Gap (One Texas)

| Metric                        | Amount          |
|-------------------------------|-----------------|
| Target                        | $15,000,000     |
| Pipeline Revenue              | $X,XXX,XXX      |
| Won Revenue (2026 YTD)        | $X,XXX,XXX      |
| **Combined Progress**         | **$X,XXX,XXX**  |
| **Remaining Gap**             | **$XX,XXX,XXX** |
| Gap % remaining               | **XX%**         |
```

Follow with 2-3 sentences of Chase-voice commentary analyzing enterprise split (which is carrying pipeline, which is converting wins, which is dormant), and direct assessment of gap closure likelihood. David owns the co-sell pipeline — address gaps to him directly. Do not soften numbers. Do not suggest partner contacts are responsible — David is.

---

## Notes — Filter Selection (CRITICAL)

The location slicer on both PowerBI pages uses checkboxes styled with class `slicerCheckbox`. Selected items have the class `selected` appended (e.g., `class="slicerCheckbox selected"`).

**How to click a location:**
1. Find the `<span class="slicerText">` containing the location name (e.g., "Dallas, TX")
2. Get its parent container via `.closest('[class*="slicerItemContainer"]')`
3. Find the checkbox: `container?.querySelector('[class*="slicerCheckbox"]')`
4. Click it: `checkbox.click()`
5. Wait 2 seconds for the PowerBI dashboard to update with the filtered data
6. Read the KPI values from the page text

**Important:** Each location is exclusive (clicking one deselects the others). You MUST click each of the three One Texas locations separately, record the values, and sum them manually. Do NOT rely on the aggregate shown when "Improving, Enterprise" is selected.

- Both pages use direct URL navigation — no in-report nav clicks needed.
- Quarter/Year table confirms the report period (should always show 2026).
- Gap = pipeline + won combined against $15M. Both count toward Rock 4.
- One Texas = Dallas, TX + Houston, TX + Austin, TX. These are the ONLY locations David manages for Rock 4 — do not include other cities.

---

## Source

PowerBI report: Improving Sales Analytics — Co-Sell Pipeline
Connector: Chrome MCP (`mcp__Control_Chrome__*`) — primary
Obsidian cache: `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`
Freshness threshold: 7 days
Auth: SSO (auto via Chrome session)
Rock 4 Target: $15M co-sell pipeline by end of Q2 2026

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/co-sell-pipeline-latest.json
```

Content:
```json
{
  "skill": "co-sell-pipeline",
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
co-sell-pipeline-YYYY-MM-DD-HHmmss.md
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
context: "Co-sell pipeline snapshot — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.


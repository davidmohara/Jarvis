---
name: co-sell-pipeline
description: >
  Pull live co-sell pipeline and won data from the Improving Sales Analytics PowerBI report.
  Reports pipeline revenue and opps by partner, won revenue and opps by partner, and gap to
  Rock 4's $15M co-sell pipeline target. Trigger on /co-sell-pipeline, "co-sell", "cosell",
  "partner pipeline", or "rock 4 pipeline".
agent: chase
model: sonnet
---

# Co-Sell Pipeline

## Purpose

Pull live co-sell pipeline and won revenue data from the Improving Sales Analytics PowerBI
report. Surface partner-level breakdown, progress toward Rock 4's $15M target, and gap
remaining. David tracks this against two key partners: Microsoft (SME&C, John Yurewicz) and
Confluent (Nick Larson and Dante).

Rock 4 target: **$15M co-sell pipeline** by end of Q2 2026.

Gap formula: `$15M - Pipeline Revenue - Won Revenue = Remaining Gap`

---

## Execution

### Step 1 — Navigate to Coselling Partner Pipeline Page

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/8a62865681ae18b5ec9b?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

SSO auto-authenticates. No manual login needed. Navigate directly to this URL — do NOT use
the mcas.ms variant or click through nav. The report loads in 3-5 seconds.

### Step 2 — Screenshot and Read Pipeline Data

Take a screenshot to confirm the page has loaded and KPI tiles are visible:

```
mcp__playwright__browser_take_screenshot
```

Read the following values from the screenshot:

**KPI tiles:**
- Pipeline Revenue w/ Coselling Partner (total dollar amount)
- Pipeline Opps w/ Coselling Partner (total count)

**Partner breakdown table** (columns: Co-Selling Partners, Revenue Amount, Count Opps w/ Co-Seller):
- Read each partner row: partner name, revenue amount, opp count
- Capture all rows — typical partners include Microsoft, Confluent, SAP, Scrum.org

**Quarter/Year table** (bottom right): capture the current quarter and year filter active on the page.

If the KPI tiles are not visible, wait 2 seconds and take another screenshot before proceeding.

### Step 3 — Navigate to Won Coselling Partner Opps Page

Navigate to the Won page directly by URL:

```
mcp__playwright__browser_navigate
url: https://app.powerbi.com/groups/me/apps/bda222e8-2ca5-4f79-8713-c15ea283f95d/reports/9cba3eb6-e267-45a2-8c8b-747c20f5db21/57bac82f202223c91446?ctid=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e&experience=power-bi
```

Wait 3-5 seconds for the page to load.

### Step 4 — Screenshot and Read Won Data

Take a screenshot:

```
mcp__playwright__browser_take_screenshot
```

Read the following values:

**KPI tiles:**
- Won Revenue w/ Coselling Partner (total dollar amount)
- Won Opps w/ Coselling Partner (total count)

**Partner breakdown table** (same structure as pipeline page):
- Read each partner row: partner name, won revenue amount, won opp count

### Step 5 — Output Formatted Report

Calculate gap to target using live data:

```
Remaining Gap = $15,000,000 - Pipeline Revenue - Won Revenue
```

Output the report using the format below.

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

| Metric                        | Amount         |
|-------------------------------|----------------|
| Target                        | $15,000,000    |
| Pipeline Revenue              | $X,XXX,XXX     |
| Won Revenue                   | $XXX,XXX       |
| **Remaining Gap**             | **$XX,XXX,XXX**|
| Gap % remaining               | XX%            |
```

Follow the table with 2-3 sentences of Chase-voice commentary. David owns the co-sell
pipeline — address gaps to him directly. If the gap is greater than $10M: call it out as
critical and state what partner channels need more activity. Do not soften numbers that are
behind. Do not suggest that partner contacts (Nick Larson, John Yurewicz, etc.) are
responsible — David is.

Example at current trajectory: "Pipeline is $954K against a $15M target — 6.4% of goal
with Q2 just starting. Microsoft is the largest active partner at $587K; Confluent has $315K
in pipeline but nothing closed. This rock needs significant acceleration to be competitive
by June."

## Notes

- Both pages use direct URL navigation — no in-report nav clicks needed.
- If a page lands on a different tab than expected, use the DOM text-click fallback:
  ```js
  mcp__playwright__browser_evaluate
  function: () => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
      if (el.textContent.trim() === 'Coselling Partner Pipeline') { el.click(); return 'clicked'; }
    }
    return 'not found';
  }
  ```
- The Quarter/Year table in the bottom right of the pipeline page confirms which period the
  data covers. Always report this period in the output header.
- Gap calculation uses pipeline + won revenue combined against the $15M target. Pipeline is
  open opps; won is closed. Both count toward Rock 4 progress.
- **Date filter — Won Coselling page**: The page has an "Actual Close Date" slider with two
  date inputs. To see full-year 2026 data, set to 1/1/2026 - 12/31/2026. **Critical: change
  end date BEFORE start date** — changing start date first breaks the filter. Steps: (1) click
  end date input (second `input.date-slicer-date`), triple-select, type `12/31/2026`, Enter;
  (2) click start date input (first), triple-select, type `1/1/2026`, Enter; (3) screenshot to
  confirm. If the filter already shows the correct range, skip.

---

## Source

PowerBI report: Improving Sales Analytics — Co-Sell Pipeline
Connector: Playwright MCP (`mcp__playwright__*`)
Auth: SSO (auto)
Rock 4 Target: $15M co-sell pipeline by end of Q2 2026

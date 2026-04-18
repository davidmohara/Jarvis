---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Pro-rate the 2025 baseline.** For month M, baseline = ($72.2M × M/12). Compare YTD 2026 against pro-rated baseline, not full-year 2025.
2. **Recalculate GM% from sums.** Do not average. Account GM% = SUM(GP) / SUM(Revenue).
3. **Flag growth status clearly.** Below 6% growth is a bonus risk flag. Flag it for David to see.
4. **Never hide variance.** If growth is off-track, surface it immediately with the gap amount.
5. **Exclude Winnipeg and Canadian AT&T** — those exclusions were applied in Step 1, so don't re-apply here.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Open comp tracker Comp 2 sheet; retrieve accumulated-context from Steps 1-2 (one_texas_total_revenue, one_texas_total_cost, one_texas_gm_pct); current month | Updated Comp 2 - Region sheet with monthly revenue, cost, GP, GM%, and cumulative growth tracking; bonus qualification flag |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Opening the Comp 2 - Region sheet
- Writing monthly One Texas regional totals (revenue, cost, GP, GM%)
- Calculating and writing cumulative YTD revenue and growth %
- Comparing growth vs. 6% threshold
- Flagging bonus qualification status

**Out of scope:**
- Comp 1 (named account) data — that's step 3
- Commission calculations — that's step 6
- Strategic activities (Comp 3) — that's step 7

---

## YOUR TASK

### 1. Open the Comp 2 - Region sheet

The comp tracker should still be open from Step 3. Select the `Comp 2 - Region` tab.

**Expected structure:**
- Column A: Metric labels (Regional Revenue, Regional Cost, Regional GM%, Cumulative Revenue, YTD Growth %, etc.)
- Columns B onward: Monthly columns (Jan–Dec 2026)
- Summary row at the bottom for qualifications and flags

**Read the sheet structure first** to confirm layout before writing.

---

### 2. Identify the current month column

From accumulated-context, retrieve the update month (e.g., "2026-04" for April).

Locate the corresponding column in the sheet (e.g., April = column 5).

---

### 3. Write monthly One Texas regional totals

From accumulated-context, retrieve (from Steps 1-2):
- `one_texas_total_revenue`
- `one_texas_total_cost`
- `one_texas_total_gp` (calculated as Revenue - Cost if not provided)
- `one_texas_gm_pct` (from Step 2, or calculated as GP / Revenue)

Write to the Comp 2 sheet:
```
Row: "Regional Revenue"
  Column [Month]: [one_texas_total_revenue]
  
Row: "Regional Cost"
  Column [Month]: [one_texas_total_cost]
  
Row: "Regional Gross Profit"
  Column [Month]: [one_texas_total_gp]
  
Row: "Regional GM%"
  Column [Month]: [one_texas_gm_pct] formatted as percentage
```

---

### 4. Calculate and write cumulative YTD metrics

**Cumulative Revenue (YTD):**
```
YTD Revenue = SUM of Regional Revenue columns from Jan through current month
Write to row "Cumulative Revenue YTD", column [Month]
```

**Pro-Rated 2025 Baseline:**
```
For month M (1=Jan, 4=Apr, 12=Dec):
  Pro-Rated Baseline = $72,200,000 × (M / 12)
  
Example (April = month 4):
  Pro-Rated Baseline = $72,200,000 × (4 / 12) = $24,066,667
```

**YTD Growth vs. 2025 Baseline:**
```
YTD Growth % = (YTD Revenue / Pro-Rated Baseline) - 1

Example (April, YTD Revenue = $25,000,000):
  YTD Growth % = ($25,000,000 / $24,066,667) - 1 = 3.87%
```

Write to row "YTD Growth % vs 2025", column [Month]

---

### 5. Bonus qualification check

After writing all metrics, calculate:

```
Growth Target: ≥ 6%
GM% Target: ≥ 30% (if profitability data available)

If YTD Growth % ≥ 6% AND YTD GM% ≥ 30%:
  Status = "ON TRACK TO QUALIFY"
  
Else if YTD Growth % < 6%:
  Status = "BELOW THRESHOLD — BONUS AT RISK"
  Gap = 6% - (YTD Growth %)
  Flag = "Need $X additional revenue to hit 6% target"
  
Else if profitability_available = false:
  Status = "PENDING GM% DATA"
  
Else if YTD GM% < 30%:
  Status = "GM% AT RISK"
```

Write this status to a "Qualification Status" row or cell note:

```
Example (April):
  "YTD Growth: 3.87% | Target: 6% | Gap: 2.13% ($500K needed) | Status: BELOW THRESHOLD"
```

---

### 6. Document growth trajectory

For David's reference, add a note summarizing:
- Current month revenue
- YTD revenue
- Pro-rated baseline
- Growth %
- Gap to 6% target (in dollars and percentage points)

Example note:
```
April 2026:
  Monthly Revenue: $25M
  YTD Revenue: $25M (Jan-Apr)
  Pro-Rated 2025 Baseline: $24.1M
  YTD Growth: 3.87% (Target: 6%)
  Gap: 2.13% ($1.9M needed in remaining 8 months to hit 6%)
  GM%: Pending profitability data
  Qualification Status: Below Threshold
```

---

### 7. Save the spreadsheet

Use `mcp__Excel__By_Anthropic___save_workbook`.

---

### 8. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 4
accumulated-context:
  (all prior context, plus:)
  comp2_updated: true
  comp2_timestamp: "2026-04-17T10:00:00Z"
  monthly_revenue: 25000000.00
  ytd_revenue: 25000000.00
  pro_rated_baseline: 24066667.00
  ytd_growth_pct: 0.0387
  growth_gap_dollars: 1900000.00
  bonus_status: "Below Threshold"
  comp2_notes: "..."
```

---

## SUCCESS METRICS

✅ **Step 4 complete when:**
1. Comp 2 - Region sheet opened and verified
2. Monthly One Texas regional totals written (revenue, cost, GP, GM%)
3. YTD cumulative revenue calculated and written
4. Pro-rated 2025 baseline calculated correctly
5. YTD Growth % vs. 2025 baseline calculated and written
6. Bonus qualification status determined and documented
7. Growth gap (if below 6%) calculated and surfaced
8. Status flag (ON TRACK / BELOW THRESHOLD / PENDING) added to sheet for visibility
9. Spreadsheet saved
10. accumulated-context in state.yaml updated with comp2 details

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Comp 2 sheet structure unclear** | Read the sheet structure first. Ask David if layout differs from expected. Adapt and proceed. |
| **Profitability data not available** | Write revenue, cost, and GP. Mark GM% as "Pending". Set bonus_status to "PENDING GM% DATA". Continue. |
| **YTD revenue calculation incorrect** | Double-check: SUM of all months Jan through current month. Confirm no missing months. |
| **Growth is below 6%** | Do NOT hide it. Flag immediately: "Below Threshold. Gap: X%. Need $Y additional revenue." Surface to David for review. |
| **Pro-rated baseline calculation ambiguous** | Use: Baseline × (Month# / 12). Example: April (month 4) = $72.2M × (4/12) = $24.067M. |

---

## NEXT STEP

→ `step-05-sync-leads.md`

Pass all accumulated-context (including comp2 metrics and bonus status) to Step 5. Step 5 will sync My Leads.xlsx and identify commission-eligible opportunities.

<!-- system:end -->

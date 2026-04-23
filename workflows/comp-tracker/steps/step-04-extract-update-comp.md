---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Pro-rate the 2025 baseline.** For month M, baseline = ($72.2M × M/12). Compare YTD current year against pro-rated baseline.
2. **Recalculate GM% from sums.** Do not average. GM% = SUM(GP) / SUM(Revenue).
3. **Flag growth status clearly.** Below 6% YoY growth is a bonus risk. Surface gap in dollars.
4. **Never hide variance.** If below target, show exactly how far and what run rate is needed.
5. **VERIFY THE YEAR FILTER BEFORE READING ANY NUMBERS.** Only read rows labeled with the current year. Manual row filtering is acceptable — see Step 1 for protocol.
6. **Write to exact cells only.** The Comp 2 layout is verified below. Do not guess at cells.

---

## COMP 2 — REGION SHEET LAYOUT (verified 2026-04-22)

```
Row 1:  Header — "COMPONENT 2: ONE TEXAS REGIONAL GROWTH"
Row 2:  Threshold description
Row 3:  (blank)
Row 4:  B="2025 One Texas Total Revenue"  C=72200000
Row 5:  B="2025 Focused Accounts Baseline" C=14000000
Row 6:  B="6% Growth Target"  C=formula (=C4*1.06)
Row 7:  (blank)
Row 8:  Column headers:
          B = Metric
          C = Jan
          D = Feb
          E = Mar
          F = Apr
          G = May
          H = Jun
          I = Jul
          J = Aug
          K = Sep
          L = Oct
          M = Nov
          N = Dec
          O = YTD Total (formula: =SUM(C9:N9))

Data rows:
  Row 9:  Regional Revenue      ← WRITE TARGET: C9 through N9 (by month)
  Row 10: Regional Cost         ← WRITE TARGET: C10 through N10 (by month)
  Row 11: Regional Gross Profit (formula: =C9-C10 etc — DO NOT WRITE)
  Row 12: Regional GM %         (formula — DO NOT WRITE)
  Row 13: Cumulative Revenue    (formula — DO NOT WRITE)
  Row 14: Cumulative Growth vs 2025 (formula — DO NOT WRITE)

Row 16: BONUS QUALIFICATION header
Row 17: Regional YoY Growth %  (formula — DO NOT WRITE)
Row 18: Weighted Avg Regional GM % (formula — DO NOT WRITE)
Row 19: Bonus Earned (enter amount) — David fills manually
```

**Month → column map:**

| Month | Column | Revenue Cell | Cost Cell |
|-------|--------|-------------|-----------|
| January | C | C9 | C10 |
| February | D | D9 | D10 |
| March | E | E9 | E10 |
| April | F | F9 | F10 |
| May | G | G9 | G10 |
| June | H | H9 | H10 |
| July | I | I9 | I10 |
| August | J | J9 | J10 |
| September | K | K9 | K10 |
| October | L | L9 | L10 |
| November | M | M9 | M10 |
| December | N | N9 | N10 |

**Do NOT write to rows 11–14 or 17–18 — those are formula rows that calculate automatically.**

---

## YOUR TASK

### 1. Switch to the One Texas page — IN THE EXISTING TAB

**CRITICAL: Never open a new tab. Use POWERBI_TAB_ID from state.yaml for all actions.**

Read `accumulated-context.powerbi_tab_id` from state.yaml.

Take a screenshot to see the current state:
```
browser_batch: [
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Find "One Texas" in the left nav panel and click it:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [X, Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Confirm from screenshot that the page title shows "One Texas".

---

### 2. Set the Date slicer to current year — click it

The One Texas page has two slicers: **Date** and **Office**. Only change Date — leave Office as-is.

Take a screenshot to find the Date slicer coordinates. Click it, select the current year, verify:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [SLICER_X, SLICER_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Then click the current year option in the dropdown:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [YEAR_X, YEAR_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

**If slicer click is unavailable:** Fall back to manual row filtering — call `get_page_content` and only read rows labeled "2026, ..." — the One Texas page shows year labels in its table rows, making this reliable.

---

### 3. Read the data

Call `mcp__Control_Chrome__get_page_content` on POWERBI_TAB_ID.

The One Texas page shows tabular data (when "Show visuals as tables" is active) with rows like:
```
Year, Month    Austin        Dallas        Houston
2026, January  $1,456,127   $2,748,530   $1,235,959
2026, February $1,366,394   $2,911,328   $1,167,126
2026, March    $1,521,899   $3,074,539   $1,268,871
```

**ONLY read rows labeled with the current year.** Ignore all 2025 rows entirely.

Document in state.yaml:
```yaml
year_filter_method: "slicer_click" | "manual_row_filter"
year_filter_verified: true
```

---

### 4. Extract current-year monthly regional revenue and cost

From `get_page_content`, read **only rows labeled with the current year**.

The One Texas page shows two tables:
- **Project Revenue** table: columns = Year/Month, Austin, Dallas, Houston
- **Gross Profit** table: columns = Year/Month, Austin, Dallas, Houston, Gross Profit Margin %

For each current-year month present:

**Revenue per month** = Austin + Dallas + Houston (from Project Revenue table)
**Gross Profit per month** = Austin GP + Dallas GP + Houston GP (from Gross Profit table)
**Cost per month** = Revenue − Gross Profit

Example (using the data visible on 2026-04-22):
```
2026, January:  Austin $1,456,127 + Dallas $2,748,530 + Houston $1,235,959 = $5,440,616 revenue
                Austin GP $507,138 + Dallas GP $1,021,161 + Houston GP $557,515 = $2,085,814 GP
                Cost = $5,440,616 − $2,085,814 = $3,354,802

2026, February: Austin $1,366,394 + Dallas $2,911,328 + Houston $1,167,126 = $5,444,848 revenue
                Austin GP $448,921 + Dallas GP $1,126,638 + Houston GP $490,743 = $2,066,302 GP
                Cost = $5,444,848 − $2,066,302 = $3,378,546

2026, March:    Austin $1,521,899 + Dallas $3,074,539 + Houston $1,268,871 = $5,865,309 revenue
                Austin GP $425,116 + Dallas GP $964,262 + Houston GP $510,519 = $1,899,897 GP
                Cost = $5,865,309 − $1,899,897 = $3,965,412
```

For April and beyond: read from page if present, otherwise leave blank.

**Apply exclusions**: Remove Winnipeg revenue and Canadian AT&T revenue if they appear as separate line items. If they are not broken out separately, note this limitation.

---

### 5. Verify the comp tracker is open

The comp tracker should still be open from Step 3. If not, open it again using the path from state.yaml.

Select the **"Comp 2 - Region"** sheet.

**Verify structure before writing** — spot-check:
- B8 should return: "Metric"
- C8 should return: "Jan"
- F8 should return: "Apr"
- B9 should return: "Regional Revenue"
- B10 should return: "Regional Cost"

If any mismatch, stop and report.

---

### 6. Write monthly Regional Revenue to Row 9

For each month with current-year data, write the One Texas total revenue (Austin + Dallas + Houston) to the corresponding cell in Row 9:

```
January revenue   → C9
February revenue  → D9
March revenue     → E9
April revenue     → F9
(continue through current month)
```

Use `mcp__Excel__By_Anthropic___set_cell_value` for each cell:
```
set_cell_value(sheet="Comp 2 - Region", cell="C9", value=5440616)
set_cell_value(sheet="Comp 2 - Region", cell="D9", value=5444848)
set_cell_value(sheet="Comp 2 - Region", cell="E9", value=5865309)
```

**Do NOT write to months beyond the current month** — leave future months blank.

---

### 7. Write monthly Regional Cost to Row 10

For each month with current-year data, write the cost (Revenue − Gross Profit) to Row 10:

```
January cost   → C10
February cost  → D10
March cost     → E10
April cost     → F10
```

Example:
```
set_cell_value(sheet="Comp 2 - Region", cell="C10", value=3354802)
set_cell_value(sheet="Comp 2 - Region", cell="D10", value=3378546)
set_cell_value(sheet="Comp 2 - Region", cell="E10", value=3965412)
```

**Do NOT write to Rows 11–14 or 17–18** — those are formula rows. They calculate automatically from Rows 9–10.

---

### 8. Read calculated YTD growth from formula cells (do not write)

After writing Rows 9 and 10, the sheet's formulas will auto-calculate:
- Row 13 (Cumulative Revenue): running YTD sum
- Row 14 (Cumulative Growth vs 2025): compares cumulative to full-year $72.2M baseline

Read cell O9 (YTD Total Revenue) and O13 (Cumulative Revenue through Dec) to capture the YTD figure.
Read cell C17 (Regional YoY Growth %) to capture the growth percentage.

Report the growth status:
- If YoY Growth % ≥ 6%: "✅ ON TRACK"
- If YoY Growth % < 6%: "⚠️ BELOW TARGET — Gap: $[amount]"

Note: The formula compares cumulative revenue to the FULL 2025 baseline ($72.2M), not a pro-rated amount. If this produces a misleading comparison mid-year, flag it for David.

---

### 9. Save the workbook

Call `mcp__Excel__By_Anthropic___save_workbook`.

---

### 10. Update state.yaml

```yaml
current-step: 4
accumulated-context:
  (all prior context, plus:)
  comp2_updated: true
  comp2_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  year_filter_verified: true
  year_filter_method: "manual_row_filter"
  monthly_data:
    "2026-01": { revenue: 5440616, cost: 3354802, gp: 2085814 }
    "2026-02": { revenue: 5444848, cost: 3378546, gp: 2066302 }
    "2026-03": { revenue: 5865309, cost: 3965412, gp: 1899897 }
    "2026-04": { revenue: 0, cost: 0, gp: 0 }   # populate if available
  ytd_revenue: 0.00
  ytd_gm_pct: 0.00
  ytd_growth_pct: 0.00
  growth_vs_6pct_target: "on_track | below_target"
  bonus_flags: []
  cells_written:
    revenue: ["C9", "D9", "E9"]
    cost: ["C10", "D10", "E10"]
```

---

## SUCCESS METRICS

✅ **Step 4 complete when:**
1. One Texas page opened and confirmed
2. Year filter verified — only current-year rows read
3. Monthly revenue (Row 9) and cost (Row 10) written for all available months
4. Formula rows (11–14, 17–18) NOT touched
5. YTD growth % read from formula cell and reported
6. Growth flag set (on track / below target)
7. Workbook saved
8. state.yaml updated with exact cells written and monthly data

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **No year labels in page content** | Cannot filter by year — stop and report: "One Texas page data has no year labels. Manual export required." |
| **April data not yet visible in PowerBI** | Write Jan–Mar only. Note: "April not yet available in PowerBI as of [date]." Leave F9/F10 blank. |
| **Revenue figures differ from last month by >15%** | Flag for David: "Revenue variance detected — confirm before using for comp calculations." |
| **Structure mismatch on spot-check** | Stop. Do not write. Report exact mismatch. |

---

## NEXT STEP

→ `step-05-sync-leads.md`

<!-- system:end -->

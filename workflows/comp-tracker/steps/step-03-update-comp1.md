---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Only write named account revenue.** Non-matching accounts get no entry.
2. **Two separate write targets.** (A) Column F = "2026 Actual YTD" (one YTD total per account). (B) Row 30 = "BoB Revenue" monthly totals (one number per month = sum of all named account revenue for that month). Both must be populated.
3. **Read the sheet before writing.** Spot-check cells below to confirm layout matches before writing anything.
4. **Never touch formula rows or prior-year columns.** Columns C and D (2024/2025 Revenue) are read-only. Formula rows are listed explicitly below — do not write to them.
5. **Uncertain matches get written + flagged.** Write the value, add to `comp1_uncertain_matches` in state.yaml.
6. **Monthly data requires month-by-month PowerBI breakdown.** If PowerBI only shows a YTD total, write to F (YTD) only and leave Row 30 blank — do not estimate monthly splits.

---

## COMP 1 — BoB SHEET LAYOUT (verified 2026-04-22)

### Section A: Named Account YTD Table (rows 4–25)

```
Row 4 — Column headers:
  B4 = "Named Account"
  C4 = "2024 Revenue"      ← READ ONLY — never write
  D4 = "2025 Revenue"      ← READ ONLY — never write
  E4 = "2026 Target"       ← READ ONLY — never write
  F4 = "2026 Actual YTD"   ← WRITE TARGET A: one YTD total per account
  G4 = "Gross Margin %"    ← WRITE TARGET (if GM% available from Step 2)
  H4 = "YoY Growth %"      ← FORMULA — never write

Named account rows (B = account name, F = YTD write target, G = GM% write target):
  Row 5:  7-Eleven                  → F5, G5
  Row 6:  Charles Schwab & Co       → F6, G6
  Row 7:  McKesson Corporation      → F7, G7
  Row 8:  Wendy's International, LLC→ F8, G8
  Row 9:  Insperity Services, LP    → F9, G9
  Row 10: PriceSmart                → F10, G10
  Row 11: Autodesk, Inc             → F11, G11
  Row 12: Intuit, Inc               → F12, G12
  Row 13: Siemens Industry, Inc.    → F13, G13
  Row 14: ORIX Corporation USA      → F14, G14
  Row 15: AT&T Services, Inc.       → F15, G15
  Row 16: Constellation Energy      → F16, G16
  Row 17: Marriott                  → F17, G17
  Row 18: Kirby Corp                → F18, G18
  Row 19: Expedia                   → F19, G19
  Row 20: Massimo                   → F20, G20
  Row 21: CBRE                      → F21, G21
  Row 22: Tenet                     → F22, G22
  Row 23: Texas Instruments         → F23, G23
  Row 24: Builders First Source     → F24, G24
  Row 25: TOTALS                    → FORMULA ROW — never write (=SUM(F5:F24) etc)
```

### Section B: Monthly Revenue Tracking (rows 28–40)

```
Row 28: Section header "MONTHLY REVENUE TRACKING — BOOK OF BUSINESS"
Row 29: Month headers:
  B29 = "Metric"
  C29 = (blank — skip this column in monthly section)
  D29 = "Jan"   ← January
  E29 = "Feb"   ← February
  F29 = "Mar"   ← March
  G29 = "Apr"   ← April
  H29 = "May"   ← May
  I29 = "Jun"   ← June
  J29 = "Jul"   ← July
  K29 = "Aug"   ← August
  L29 = "Sep"   ← September
  M29 = "Oct"   ← October
  N29 = "Nov"   ← November
  O29 = "Dec"   ← December
  P29 = "YTD Total" ← FORMULA — never write (=SUM(C30:N30))

Row 30: BoB Revenue  ← WRITE TARGET B: monthly total of ALL named account revenue
Row 31: BoB Cost     ← WRITE TARGET B: monthly total of ALL named account cost
Row 32: BoB Gross Profit  ← FORMULA (=C30-C31 etc) — never write
Row 33: BoB Gross Margin % ← FORMULA — never write
Row 34: Cumulative Revenue ← FORMULA — never write
Row 35: Cumulative Growth % ← leave blank (David fills)
Rows 37–40: Bonus Qualification ← formulas or David fills — never write
```

**Monthly column map for Row 30 (BoB Revenue) and Row 31 (BoB Cost):**

| Month | Column | BoB Revenue Cell | BoB Cost Cell |
|-------|--------|-----------------|---------------|
| January | D | D30 | D31 |
| February | E | E30 | E31 |
| March | F | F30 | F31 |
| April | G | G30 | G31 |
| May | H | H30 | H31 |
| June | I | I30 | I31 |
| July | J | J30 | J31 |
| August | K | K30 | K31 |
| September | L | L30 | L31 |
| October | M | M30 | M31 |
| November | N | N30 | N31 |
| December | O | O30 | O31 |

---

## YOUR TASK

### 1. Open the comp tracker

Use `mcp__Excel__By_Anthropic___open_workbook` with the absolute path from `state.yaml` accumulated-context (`comp_tracker_file_path`). Do NOT hardcode the session prefix — read it from state.yaml.

### 2. Verify sheet structure before writing anything

Call `mcp__Excel__By_Anthropic___get_cell_value` on these spot-check cells. If any mismatch, **stop and report — do not write**:

| Cell | Expected value |
|------|---------------|
| B5 | "7-Eleven" (or close variant) |
| B8 | "Wendy's International, LLC" (or close variant) |
| B25 | "TOTALS" |
| F4 | "2026 Actual YTD" |
| B29 | "Metric" |
| D29 | "Jan" |
| G29 | "Apr" |
| B30 | "BoB Revenue" |
| B31 | "BoB Cost" |

### 3. Check the year-filter gate before writing ANYTHING

Read `accumulated-context.customer_distribution_slicer_set` from state.yaml.

**If `customer_distribution_slicer_set: false`:**
- Revenue figures in the revenue_map are ALL-TIME totals, not 2026 YTD
- **Do NOT write any values to cells F5–F24**
- Instead, output this message to David:
  > "⚠️ Comp 1 NOT updated — revenue data is all-time, not 2026 YTD. To fix: open PowerBI Customer Distribution page (https://app.powerbi.com/groups/me/reports/c5ce8a51-c79f-4461-9262-932885e44cec/e466d392806eb9e8943e), set the Date slicer to 2026, then re-run the workflow."
- Skip to step 8 (state.yaml update) and mark comp1 as blocked
- The monthly Row 30/31 entries also cannot be written

**If `customer_distribution_slicer_set: true`:**
- Proceed with writes below

---

### 4. Write "2026 Actual YTD" to column F (Section A)

From `revenue_map` in accumulated-context (Steps 1–2), for each account with `confidence: "high"` or `confidence: "medium"` AND `all_time_not_ytd: false`:

- The YTD value = sum of that account's revenue across all current-year months (Jan through current month)
- Write to the F column cell for that account's row

```
set_cell_value(sheet="Comp 1 - BoB", cell="F5",  value=[7-Eleven YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F6",  value=[Charles Schwab YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F7",  value=[McKesson YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F8",  value=[Wendy's YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F11", value=[Autodesk YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F12", value=[Intuit YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F13", value=[Siemens YTD])
set_cell_value(sheet="Comp 1 - BoB", cell="F14", value=[ORIX YTD])
... (continue for all matched accounts)
```

For accounts with NO match or confidence: "low" — leave F column cell blank. Do NOT write zero.

### 4. Write Gross Margin % to column G (Section A)

If `gm_pct` is available from Step 2, write it to column G as a decimal (e.g., 39.8% = 0.398):

```
set_cell_value(sheet="Comp 1 - BoB", cell="G5",  value=0.398)  # 7-Eleven 39.8%
set_cell_value(sheet="Comp 1 - BoB", cell="G11", value=0.35)   # Autodesk 35%
```

If GM% is not available (Step 2 deferred): leave G column blank. Do NOT write 0 or an estimate.

### 5. Write monthly BoB Revenue totals to Row 30 (Section B)

This requires **month-by-month** revenue from PowerBI — not just a YTD total.

For each month (Jan through current month), sum the revenue of ALL named accounts that had revenue in that month, and write the total to Row 30.

**How to get monthly breakdowns:**
- If PowerBI's Customer Distribution page shows month-by-month data per account: use those figures
- If PowerBI only shows a YTD total: leave Row 30 blank for now and note in state.yaml: `"bob_monthly_data_available": false` — do not estimate monthly splits

Assuming month-by-month data is available, example writes:
```
set_cell_value(sheet="Comp 1 - BoB", cell="D30", value=[sum of all named account revenue in Jan])
set_cell_value(sheet="Comp 1 - BoB", cell="E30", value=[sum of all named account revenue in Feb])
set_cell_value(sheet="Comp 1 - BoB", cell="F30", value=[sum of all named account revenue in Mar])
set_cell_value(sheet="Comp 1 - BoB", cell="G30", value=[sum of all named account revenue in Apr])
```

**Do NOT write to column C (blank in monthly section), P (YTD Total formula), or any month beyond the current month.**

### 6. Write monthly BoB Cost totals to Row 31 (Section B)

Same pattern as Row 30, using cost figures (Revenue − Gross Profit) per month:

```
set_cell_value(sheet="Comp 1 - BoB", cell="D31", value=[sum of named account cost in Jan])
set_cell_value(sheet="Comp 1 - BoB", cell="E31", value=[sum of named account cost in Feb])
set_cell_value(sheet="Comp 1 - BoB", cell="F31", value=[sum of named account cost in Mar])
set_cell_value(sheet="Comp 1 - BoB", cell="G31", value=[sum of named account cost in Apr])
```

If cost data is not available (Step 2 deferred): leave Row 31 blank.

**Do NOT write to Rows 32–35 or 37–40** — those are formulas or David fills manually.

### 7. Save the workbook

Call `mcp__Excel__By_Anthropic___save_workbook`.

### 8. Update state.yaml

```yaml
current-step: 3
accumulated-context:
  (all prior context, plus:)
  comp1_updated: true
  comp1_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  bob_monthly_data_available: true | false
  comp1_ytd_cells_written:
    "7-Eleven": "F5"
    "Charles Schwab & Co": "F6"
    "Autodesk Inc": "F11"
    ...
  comp1_monthly_cells_written:
    "Jan": "D30"
    "Feb": "E30"
    "Mar": "F30"
    "Apr": "G30"
  comp1_accounts_skipped: ["Constellation Energy", "Marriott", ...]
  comp1_uncertain_matches: ["AccountName — PowerBI name: 'X', confidence 85%"]
  comp1_gm_written: true | false
```

---

## SUCCESS METRICS

✅ **Step 3 complete when:**
1. Comp tracker opened
2. Sheet structure verified via spot-check (8 cells confirmed)
3. YTD revenue written to F5–F24 for all matched accounts (confidence ≥ 80%)
4. GM% written to G5–G24 where available from Step 2
5. Monthly BoB Revenue totals written to D30–O30 (Jan–Dec) for available months
6. Monthly BoB Cost totals written to D31–O31 where cost data is available
7. Formula rows (25, 32–35, 37–40) and P column NOT touched
8. Accounts with no data left blank — not zeroed out
9. Workbook saved
10. state.yaml updated with exact cells written

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Spot-check mismatch (e.g., B5 ≠ "7-Eleven")** | Stop. Do not write. Report exact mismatch — row map needs manual correction. |
| **Cell already has a non-zero value** | Do not overwrite. Report: "Cell F[N] ([account]) already has data: [value]. Overwrite?" Wait for David. |
| **No monthly breakdown available from PowerBI** | Write F column (YTD) only. Set `bob_monthly_data_available: false`. Leave Row 30–31 blank. This is the confirmed behavior: Customer Distribution shows YTD totals only, not month-by-month breakdowns. Row 30 and Row 31 cannot be populated from this source — leave them blank rather than estimating splits. |
| **revenue_map empty (Step 1 failed)** | Report: "No revenue data from Step 1 — Comp 1 not updated." Proceed to Step 4. |
| **GM% missing (Step 2 deferred)** | Write revenue only. Leave G column blank. Note in summary. |

---

## NEXT STEP

→ `step-04-extract-update-comp2.md`

<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never open a new tab.** All navigation uses POWERBI_TAB_ID from state.yaml. No exceptions.
2. **Use cliclick + execute_javascript for all clicks.** Do NOT use browser_batch — it is unreliable. See "Click Protocol" in step-01.
3. **"Show visuals as tables" MUST be verified active before reading any page.** Check `show_visuals_as_tables_enabled` in state.yaml. If false, re-run the View menu protocol from step-01 before proceeding.
4. **Pro-rate the 2025 baseline.** For month M, baseline = ($72.2M × M/12). Compare YTD current year against pro-rated baseline.
5. **Recalculate GM% from sums.** Do not average. GM% = SUM(GP) / SUM(Revenue).
6. **Flag growth status clearly.** Below 6% YoY growth is a bonus risk. Surface gap in dollars.
7. **Never hide variance.** If below target, show exactly how far and what run rate is needed.
8. **VERIFY THE YEAR FILTER BEFORE READING ANY NUMBERS.** Only read rows labeled with the current year. Manual row filtering is acceptable.
9. **Write to exact cells only.** The Comp 2 layout is verified below. Do not guess at cells.

---

## COMP 2 SHEET LAYOUT AND ROW 14 FORMULA

Read `references/comp2-sheet-layout.md` before reading or writing any cell on the "Comp 2 - Region" sheet. It holds the full row layout, the month-to-column map (Revenue row 9, Cost row 10, C through N; rows 11-14 and 17-18 are formula rows, never write), the structure spot-check values, and the pro-rated Row 14 formula spec.

---

## YOUR TASK

### 1. Navigate to One Texas page — IN THE EXISTING TAB

Read `accumulated-context.powerbi_tab_id` from state.yaml.

Verify "Show visuals as tables" is active (`show_visuals_as_tables_enabled: true`). If not, re-run the View menu protocol from step-01.

Use `execute_javascript` to find and JS-click the One Texas page tab:
```javascript
var buttons = document.querySelectorAll('button');
for (var i = 0; i < buttons.length; i++) {
  var text = buttons[i].getAttribute('aria-label') || buttons[i].innerText || '';
  if (text.trim().indexOf('One Texas') !== -1) {
    buttons[i].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
    break;
  }
}
```

Verify via `get_page_content` that the page title shows "One Texas".

---

### 2. Verify Date slicer filter

The slicer set in step-01 persists across pages. Verify via `get_page_content` that it still shows 2026.

The One Texas page has two slicers: **Date** and **Office**. Only change Date if needed — leave Office as-is.

**If the slicer reverted to "All":**

Find the Date slicer using execute_javascript:
```javascript
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length; i++) {
  var text = all[i].innerText ? all[i].innerText.trim() : '';
  if (text === 'Date\nAll' || text === 'Date\n2026') {
    var rect = all[i].getBoundingClientRect();
    // screen_x = rect.left + rect.width/2
    // screen_y = 154 + rect.top + rect.height/2
  }
}
```
Click with cliclick. Then find and click "2026" in the dropdown. Verify via `get_page_content`.

**Fallback if slicer cannot be set:** Call `get_page_content` and only read rows labeled "2026, ..." — the One Texas page shows year labels in its table rows, making this reliable.

---

### 3. Read the data

Call `mcp__Control_Chrome__get_page_content`.

The One Texas page shows tabular data (when "Show visuals as tables" is active); see `references/comp2-extraction-examples.md` (read it in this step) for the row format.

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

A worked example of the per-month calculation is in `references/comp2-extraction-examples.md` (read it in this step).

For April and beyond: read from page if present, otherwise leave blank.

**Apply exclusions**: Remove Winnipeg revenue and Canadian AT&T revenue if they appear as separate line items. If they are not broken out separately, note this limitation.

---

### 5. Verify the comp tracker is open

The comp tracker should still be open from Step 3. If not, open it again using the path from state.yaml.

Select the **"Comp 2 - Region"** sheet.

**Verify structure before writing** — spot-check against the values in `references/comp2-sheet-layout.md` (B8/C8/F8/B9/B10). If any mismatch, stop and report.

---

### 6. Check Row 14 formula — fix if needed

Before writing Row 9 and Row 10 data, read cell C14.

If C14 contains a formula that compares to the full $72.2M annual baseline (e.g., `=(C13-$C$4)/$C$4` or similar), it will show wildly negative values mid-year. Fix it: write the pro-rated formula from `references/comp2-sheet-layout.md` (Row 14 formula spec) to C14, then verify it auto-propagates across D14:N14. If it doesn't (Excel doesn't always auto-fill), write the same formula individually to D14 through N14.

**After writing Row 9 data, verify Row 14 shows sensible values** (e.g., Jan should be close to 0%, not -90%). If it's still wildly off, the formula needs checking.

---

### 7. Write monthly Regional Revenue to Row 9

For each month with current-year data, write the One Texas total revenue (Austin + Dallas + Houston) to the corresponding Row 9 cell per the month-to-column map in `references/comp2-sheet-layout.md` (January -> C9, February -> D9, and so on through the current month).

Use `mcp__Excel__By_Anthropic___set_cell_value` for each cell.

**Do NOT write to months beyond the current month** — leave future months blank.

---

### 8. Write monthly Regional Cost to Row 10

For each month with current-year data, write the cost (Revenue − Gross Profit) to the corresponding Row 10 cell per the same month-to-column map in `references/comp2-sheet-layout.md`.

**Do NOT write to Rows 11–14 or 17–18** — those are formula rows. They calculate automatically from Rows 9–10.

---

### 9. Read calculated YTD growth from formula cells (do not write)

After writing Rows 9 and 10, the sheet's formulas will auto-calculate:
- Row 13 (Cumulative Revenue): running YTD sum
- Row 14 (Cumulative Growth vs 2025): compares cumulative to pro-rated 2025 baseline

Read cell O9 (YTD Total Revenue) to capture the YTD figure.
Read cell C17 (Regional YoY Growth %) to capture the growth percentage.

Report the growth status:
- If YoY Growth % ≥ 6%: "✅ ON TRACK"
- If YoY Growth % < 6%: "⚠️ BELOW TARGET — Gap: $[amount]"

**Gap calculation:** `Gap = ($72.2M × 1.06) − (YTD Revenue × 12/month)` (annualized run rate)

---

### 10. Save the workbook

Call `mcp__Excel__By_Anthropic___save_workbook`.

---

### 11. Update state.yaml

```yaml
current-step: 4
accumulated-context:
  (all prior context, plus:)
  comp2_updated: true
  comp2_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  year_filter_verified: true
  year_filter_method: "manual_row_filter"
  monthly_data:
    "YYYY-MM": { revenue: 0, cost: 0, gp: 0 }   # one entry per month with data
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
1. One Texas page opened and confirmed via JS click (no new tab)
2. "Show visuals as tables" verified active
3. Year filter verified — only current-year rows read
4. Row 14 formula checked and fixed if needed (pro-rated formula in place)
5. Monthly revenue (Row 9) and cost (Row 10) written for all available months
6. Formula rows (11–14, 17–18) NOT touched
7. YTD growth % read from formula cell and reported
8. Growth flag set (on track / below target)
9. Workbook saved
10. state.yaml updated with exact cells written and monthly data

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **"Show visuals as tables" not active** | Re-run View menu protocol from step-01. Without it, all data is chart-only and unreadable. |
| **execute_javascript returns "missing value"** | Avoid await, template literals, and .length on large strings. Use var (not const/let). Slice strings with explicit bounds. |
| **cliclick misses slicer element** | Re-derive coordinates via execute_javascript getBoundingClientRect. Never hardcode — always compute. |
| **No year labels in page content** | Cannot filter by year — stop and report: "One Texas page data has no year labels. Manual export required." |
| **April data not yet visible in PowerBI** | Write Jan–Mar only. Note: "April not yet available in PowerBI as of [date]." Leave F9/F10 blank. |
| **Revenue figures differ from last month by >15%** | Flag for David: "Revenue variance detected — confirm before using for comp calculations." |
| **Structure mismatch on spot-check** | Stop. Do not write. Report exact mismatch. |
| **Row 14 shows wildly negative values after write** | Formula is comparing to full annual baseline instead of pro-rated. Fix with: `=(C13-($C$4*(COLUMN()-2)/12))/($C$4*(COLUMN()-2)/12)` |

---

## NEXT STEP

→ `step-05-sync-leads.md`

<!-- system:end -->

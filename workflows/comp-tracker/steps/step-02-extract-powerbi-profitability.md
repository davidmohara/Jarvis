---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never open a new tab.** All navigation uses POWERBI_TAB_ID from state.yaml. No exceptions.
2. **Every browser_batch action must include `"tabId": POWERBI_TAB_ID`.**
3. **Screenshot before every click.** Never click blind.
4. **Never average gross margin.** Recalculate: GM% = (Gross Profit / Revenue) × 100.
5. **Match every account back to revenue_map from Step 1.**
6. **Only read rows labeled with the current year** if year labels are present per row.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | POWERBI_TAB_ID → click to Project Consultant Profitability Dataset page → set slicer → read GM% | revenue_map updated with gm_pct, cost, gp per account |

---

## YOUR TASK

### 1. Get the PowerBI tab ID

Read `accumulated-context.powerbi_tab_id` from state.yaml. Use this for ALL browser actions.

---

### 2. Switch to Project Consultant Profitability Dataset page — click in left nav

Take a screenshot first to see the current page and left nav:
```
browser_batch: [
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Find "Project Consultant Profitability Dataset" in the left nav panel and click it:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [X, Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Confirm from the screenshot that the page title changed to "Project Consultant Profitability Dataset".

---

### 3. Set the Date slicer to current year

Same procedure as Step 1:
- Take a screenshot to find the Date slicer coordinates (top-left area of page, showing "All" or a year)
- Click the slicer to open it
- Click the current year (e.g., "2026")
- Take a screenshot and call `get_page_content` to verify the slicer now shows the current year

```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [SLICER_X, SLICER_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Then click the current year in the dropdown:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [YEAR_X, YEAR_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Verify via `get_page_content` that Date slicer shows current year. If after 3 attempts it still shows "All": document `profitability_slicer_set: false`, leave GM% blank, continue to Step 4 without profitability data.

---

### 4. Extract profitability data

Call `mcp__Control_Chrome__get_page_content` on POWERBI_TAB_ID.

If the page shows tabular data with year labels per row (e.g., "2026, January | Account | Revenue | Cost | GP | GM%"):
- **Only read rows labeled with the current year**

If the page shows a flat list without year labels:
- Note this as a limitation: `profitability_year_labels_present: false`
- Read all available data but flag as potentially multi-year

Expected columns (adapt to actual structure):
- Account Name
- Revenue (cross-check against Step 1 revenue_map)
- Cost / Direct Cost
- Gross Profit
- Gross Margin % (or calculate: GP / Revenue × 100)

---

### 5. Merge into revenue_map from Step 1

For each account in profitability data:
1. Look up in `revenue_map` from accumulated-context
2. If found: update `gm_pct`, `cost`, `gp` fields
3. If in profitability only (not in revenue_map): flag as `profitability_only`
4. If in revenue_map but not here: flag as `missing_profitability`

**Never average GM%.** Always recalculate from totals: GM% = GP / Revenue × 100.

---

### 6. Recalculate One Texas totals

```
one_texas_total_cost = SUM of cost for all included accounts
one_texas_total_gp = SUM of gp for all included accounts
one_texas_total_gm_pct = (one_texas_total_gp / one_texas_total_revenue) × 100
```

---

### 7. Update state.yaml

```yaml
current-step: 2
accumulated-context:
  powerbi_tab_id: POWERBI_TAB_ID
  profitability_slicer_set: true
  profitability_year_labels_present: true
  revenue_map: { ... updated with gm_pct, cost, gp ... }
  one_texas_total_cost: 0.00
  one_texas_total_gp: 0.00
  one_texas_total_gm_pct: 0.00
  missing_profitability: []
  profitability_only: []
```

---

## SUCCESS METRICS

✅ **Step 2 complete when:**
1. POWERBI_TAB_ID reused — no new tabs opened
2. Screenshot taken before every click
3. Profitability Dataset page reached via left nav click
4. Date slicer clicked to current year and confirmed (or documented as failed)
5. GM%, cost, GP extracted and merged into revenue_map
6. One Texas totals recalculated from sums (not averaged)
7. state.yaml updated

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Screenshot fails** | Stop. Extension disconnected. Report to David. |
| **Left nav click doesn't change page** | Try clicking again. If 3 attempts fail, try scrolling the left nav to find the page link. |
| **Slicer won't respond after 3 clicks** | Set `profitability_slicer_set: false`. Leave GM% column blank. Continue to Step 3. |
| **No profitability data visible** | Document in `missing_profitability`. Continue to Step 3 with revenue only. |

---

## NEXT STEP

→ `step-03-update-comp1.md`

<!-- system:end -->

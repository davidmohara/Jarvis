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
2. **Use cliclick + execute_javascript for all clicks.** Do NOT use browser_batch — it is unreliable. See "Click Protocol" in step-01.
3. **"Show visuals as tables" MUST be verified active before reading any page.** Check `show_visuals_as_tables_enabled` in state.yaml. If false, re-run the View menu protocol from step-01 before proceeding.
4. **Date slicer filter carries from step-01.** If `customer_distribution_slicer_set: true` in state.yaml, the slicer is already set to 2026. Do NOT re-set it — it persists across pages.
5. **Never average gross margin.** Recalculate: GM% = (Gross Profit / Revenue) × 100.
6. **Match every account back to revenue_map from Step 1.**

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | POWERBI_TAB_ID → JS-click to Project Consultant Profitability Dataset page → verify slicer still shows 2026 → read GM% | revenue_map updated with gm_pct, cost, gp per account |

---

## YOUR TASK

### 1. Get the PowerBI tab ID and verify "Show visuals as tables"

Read `accumulated-context.powerbi_tab_id` from state.yaml.

Check `accumulated-context.show_visuals_as_tables_enabled`. If false or not set, re-run the "Show visuals as tables" protocol from step-01 before proceeding.

---

### 2. Navigate to Project Consultant Profitability Dataset page

Use `execute_javascript` to find and JS-click the page tab:
```javascript
var buttons = document.querySelectorAll('button');
for (var i = 0; i < buttons.length; i++) {
  var text = buttons[i].getAttribute('aria-label') || buttons[i].innerText || '';
  if (text.trim().indexOf('Project Consultant Profitability Dataset') !== -1) {
    buttons[i].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
    break;
  }
}
```

Verify via `get_page_content` that the page title changed to "Project Consultant Profitability Dataset".

---

### 3. Verify the Date slicer is still set to current year

The slicer filter set in step-01 on Customer Distribution **persists across page navigations**. It should still show 2026.

Verify via `get_page_content`: look for "Date\n2026" or "Date 2026" in the output. If the slicer still shows 2026, proceed — do NOT re-click it.

**If the slicer has reverted to "All" (rare — occurs only if page was hard-reloaded):**

Use the same procedure from step-01:

**Step A — Find slicer position:**
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
Click with cliclick.

**Step B — Select 2026:**
```javascript
var spans = document.querySelectorAll('SPAN');
for (var i = 0; i < spans.length; i++) {
  if (spans[i].innerText && spans[i].innerText.trim() === '2026') {
    var rect = spans[i].getBoundingClientRect();
    // screen_x = rect.left + rect.width/2
    // screen_y = 154 + rect.top + rect.height/2
  }
}
```
Click "2026" with cliclick. Verify via `get_page_content`.

---

### 4. Extract profitability data

Call `mcp__Control_Chrome__get_page_content`.

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
  show_visuals_as_tables_enabled: true
  profitability_slicer_verified: true
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
2. "Show visuals as tables" verified active
3. Profitability Dataset page reached via JS click
4. Date slicer verified still showing 2026 (or re-set if reverted)
5. GM%, cost, GP extracted and merged into revenue_map
6. One Texas totals recalculated from sums (not averaged)
7. state.yaml updated

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **"Show visuals as tables" not active** | Re-run View menu protocol from step-01. Without it, all data is chart-only and unreadable. |
| **Page navigation JS click not working** | Check that the page tab button exists via execute_javascript first. Try `querySelectorAll('[aria-label*="Profitability"]')` as alternative selector. |
| **Slicer reverted to "All"** | Re-click slicer using cliclick (same as step-01 procedure). |
| **No profitability data visible** | Document in `missing_profitability`. Continue to Step 3 with revenue only. |
| **execute_javascript returns "missing value"** | Avoid await, template literals, and .length on large strings. Use var (not const/let). Slice strings with explicit bounds. |
| **cliclick misses element** | Re-derive coordinates via execute_javascript getBoundingClientRect. Never hardcode — always compute. |

---

## NEXT STEP

→ `step-03-update-comp1.md`

<!-- system:end -->

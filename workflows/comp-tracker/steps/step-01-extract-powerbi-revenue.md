---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never open a new tab.** All PowerBI navigation happens within POWERBI_TAB_ID from state.yaml. No exceptions.
2. **Use cliclick + execute_javascript for all clicks.** Do NOT use browser_batch — it is unreliable. See "Click Protocol" below.
3. **"Show visuals as tables" must be enabled before reading any page.** Set it once in Step 0 via the View menu — it persists across all page navigations.
4. **Never skip exclusions.** Winnipeg and Canadian AT&T revenue must be stripped.
5. **Fuzzy match named accounts.** PowerBI names may not exactly match the canonical list.
6. **Never write all-time figures to the YTD column.** Confirm slicer shows current year before writing to F5:F24.
7. **Slicer filter persists across pages.** Set it once on Customer Distribution — it carries to Profitability and other pages automatically.

---

## CLICK PROTOCOL (replaces browser_batch for all steps)

**Coordinate formula:**
```
screen_x = page_x  (no offset — window starts at x=0)
screen_y = window_y + chrome_ui_height + page_y
         = 33 + 121 + page_y
         = 154 + page_y
```

Chrome UI height = outerHeight(949) - innerHeight(828) = 121px. Window y = 33. These are confirmed values — store in state.yaml as `cliclick_offset_y: 154`.

**Finding element coordinates (always do this — never guess):**
```javascript
// Via execute_javascript:
var el = document.querySelector('[aria-label="Element Name"]');
// OR search by text:
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length; i++) {
  if (all[i].innerText && all[i].innerText.trim() === 'Target Text') {
    var rect = all[i].getBoundingClientRect();
    // screen_x = rect.left + rect.width/2
    // screen_y = 154 + rect.top + rect.height/2
  }
}
```

**Executing a click:**
```applescript
-- via mcp__Control_your_Mac__osascript:
tell application "Google Chrome" to activate
delay 0.5
do shell script "/opt/homebrew/bin/cliclick c:[screen_x],[screen_y]"
delay 1
```

**Verifying the click worked:** Call `mcp__Control_Chrome__get_page_content` immediately after. Check the expected UI change appears in the text output.

---

## "SHOW VISUALS AS TABLES" PROTOCOL (do once per session — Step 0)

This is the critical unlock. Without it, all pages show chart-only text with no numeric data.

1. Use `execute_javascript` to find the View button:
```javascript
var buttons = document.querySelectorAll('button');
for (var i = 0; i < buttons.length; i++) {
  if ((buttons[i].getAttribute('aria-label') || buttons[i].innerText || '').trim() === 'View') {
    var rect = buttons[i].getBoundingClientRect();
    // Returns: top:48, left:1339, centerX:1365, centerY:68
  }
}
```

2. Click View button: `cliclick c:1365,[154+68=222]`

3. Use `execute_javascript` to find "Show visuals as tables (preview)" in the dropdown:
```javascript
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length; i++) {
  if (all[i].innerText && all[i].innerText.indexOf('Show visuals as tables') !== -1) {
    var rect = all[i].getBoundingClientRect();
    // Returns approx: top:271, left:1178
  }
}
```

4. Click it: `cliclick c:[154+271=425],[1178]` (note: x=page_x, y=154+page_y)

5. Verify: `get_page_content` should show "Now showing visuals as tables" at the bottom.

Set `show_visuals_as_tables_enabled: true` in state.yaml.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | POWERBI_TAB_ID from state.yaml → switch to Customer Distribution page → click slicer to current year → read data | revenue_map keyed by canonical account name; year-filter flags |

---

## YOUR TASK

### 1. Get the PowerBI tab ID and verify "Show visuals as tables"

Read `accumulated-context.powerbi_tab_id` from state.yaml. If null, run Step 0 pre-flight first.

Check `accumulated-context.show_visuals_as_tables_enabled`. If false or not set, run the "Show visuals as tables" protocol above before proceeding.

---

### 2. Navigate to Customer Distribution page

Use `execute_javascript` to find and JS-click the page tab:
```javascript
var buttons = document.querySelectorAll('button');
for (var i = 0; i < buttons.length; i++) {
  var text = buttons[i].getAttribute('aria-label') || buttons[i].innerText || '';
  if (text.trim().indexOf('Customer Distribution') !== -1) {
    buttons[i].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
    break;
  }
}
```

Verify via `get_page_content` that the page now shows "Customer Distribution".

---

### 3. Set the Date slicer to the current year

**Step A — Click the slicer to open it:**
```javascript
// Find slicer position
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

**Step B — Select the current year from dropdown:**
After clicking, use `execute_javascript` to find "2026" in the dropdown:
```javascript
// After slicer opens, look for year options
var spans = document.querySelectorAll('SPAN');
for (var i = 0; i < spans.length; i++) {
  if (spans[i].innerText && spans[i].innerText.trim() === '2026') {
    var rect = spans[i].getBoundingClientRect();
    // screen_x = rect.left + rect.width/2
    // screen_y = 154 + rect.top + rect.height/2
  }
}
```
Click "2026" with cliclick.

**Step C — Verify:**
Call `get_page_content`. The slicer line should read "Date\n2026" or "Date 2026". If it still reads "All" after 2 attempts, document `customer_distribution_slicer_set: false` and see fallback below.

**Known confirmed coordinates (2026-04-23, may shift with window resize):**
- Slicer click: page coords approx (1264, 112) → screen (1264, 266)
- "2026" option: page coords approx (1286, 155) → screen (1286, 309)

Document in state.yaml: `customer_distribution_slicer_set: true`

---

### 4. Read Customer Distribution data

Call `mcp__Control_Chrome__get_page_content`.

The page shows four sub-tables when "Show visuals as tables" is enabled:
- **Dallas** — per-account revenue for Dallas
- **Houston** — per-account revenue for Houston
- **Austin** — per-account revenue for Austin
- **Combined** — all accounts across all offices (use this for YTD totals)

Read the **Combined** section for named account YTD revenue. Use per-city sections to confirm office assignment only.

**Confirmed 2026 data format:**
```
Customer Name    Dallas
MasterCard       $1,864,184
Wendy's International, LLC  $1,131,915
...
```
Values are exact dollars (not truncated) when "Show visuals as tables" is active.

---

### 5. Fallback — slicer could not be set

If `customer_distribution_slicer_set: false`:
- Navigate to Project Revenue Dataset page (JS click on page tab)
- Call `get_page_content` — shows flat per-account revenue table
- Flag ALL entries: `all_time_not_ytd: true`
- Set: `step1_data_source: "project_revenue_dataset_all_time"`
- These values MUST NOT be written to F5:F24 without David's confirmation

---

### 6. Apply exclusions

Remove rows where:
- Account Name contains "Winnipeg" OR
- Account Name contains "AT&T" AND region = Canada

---

### 7. Match to named account list and build revenue_map

| PowerBI name | Canonical name |
|-------------|----------------|
| "7-Eleven", "7-11" | 7-Eleven |
| "Schwab", "Charles Schwab" | Charles Schwab & Co |
| "McKesson" | McKesson Corporation |
| "Wendy's International" | Wendy's International LLC |
| "Insperity" | Insperity Services LP |
| "PriceSmart" | PriceSmart |
| "Autodesk" | Autodesk Inc |
| "Intuit" | Intuit Inc |
| "Siemens" | Siemens Industry Inc |
| "ORIX" | ORIX Corporation USA |
| "AT&T" (US only) | AT&T Services Inc |
| "Constellation" | Constellation Energy |
| "Marriott" | Marriott |
| "Kirby" | Kirby Corp |
| "Expedia" | Expedia |
| "Massimo" | Massimo |
| "CBRE" | CBRE |
| "Tenet" | Tenet |
| "Texas Instruments", "TI" | Texas Instruments |
| "Builders First", "BFS" | Builders First Source |

Confidence: ✅ High (>95%) | ⚠️ Medium (80–95%, flag) | ❌ Low/truncated (skip)

---

### 8. Update state.yaml

```yaml
current-step: 1
accumulated-context:
  powerbi_tab_id: [ID]
  show_visuals_as_tables_enabled: true
  cliclick_offset_y: 154
  customer_distribution_slicer_set: true
  step1_data_source: "customer_distribution"
  revenue_map: { ... }
  excluded_accounts: []
  uncertain_matches: []
  unmatched_accounts: []
```

---

## SUCCESS METRICS

✅ **Step 1 complete when:**
1. POWERBI_TAB_ID confirmed — no new tabs opened
2. "Show visuals as tables" verified active
3. Customer Distribution page reached via JS click
4. Date slicer confirmed set to current year
5. Revenue data extracted per named account (exact dollars, not truncated)
6. Exclusions applied
7. `all_time_not_ytd` correctly set
8. state.yaml updated

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **POWERBI_TAB_ID not in state.yaml** | Run Step 0 pre-flight. |
| **"Show visuals as tables" not active** | Run the View menu protocol before any data extraction. Without it, all data is chart-only and unreadable. |
| **Slicer won't respond after 2 attempts** | Use Project Revenue Dataset fallback. Flag all data as all_time_not_ytd. |
| **execute_javascript returns "missing value"** | Avoid await, template literals, and .length on large strings. Use var (not const/let). Slice strings with explicit bounds. |
| **cliclick misses element** | Re-derive coordinates via execute_javascript getBoundingClientRect. Never hardcode — always compute. |

---

## NEXT STEP

→ `step-02-extract-powerbi-profitability.md`

<!-- system:end -->

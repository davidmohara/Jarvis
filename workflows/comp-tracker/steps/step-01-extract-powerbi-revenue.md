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
2. **Every browser_batch action must include `"tabId": POWERBI_TAB_ID`.** Never omit it.
3. **Screenshot before every click.** You must see the page before clicking coordinates.
4. **Never skip exclusions.** Winnipeg and Canadian AT&T revenue must be stripped.
5. **Fuzzy match named accounts.** PowerBI names may not exactly match the canonical list.
6. **Never write all-time figures to the YTD column.** If slicer not confirmed set to current year, flag all entries `all_time_not_ytd: true` and do NOT write to F5:F24.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | POWERBI_TAB_ID from state.yaml → switch to Customer Distribution page → click slicer to current year → read data | revenue_map keyed by canonical account name; year-filter flags; One Texas totals |

---

## YOUR TASK

### 1. Get the PowerBI tab ID

Read `accumulated-context.powerbi_tab_id` from state.yaml. This is the tab ID for ALL browser actions in this step.

If `powerbi_tab_id` is not set, run workflow Step 0 (pre-flight) first — do not proceed without it.

---

### 2. Take a screenshot to see the current state

```
browser_batch: [
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Look at the screenshot:
- What page is currently shown? (One Texas / Customer Distribution / other?)
- Is the left nav panel visible with the page list?
- Is the Date slicer visible? What does it show?

---

### 3. Switch to Customer Distribution page — click in the left nav

In the left nav panel, find "Customer Distribution" and click it. Do NOT navigate to a URL — this would reload in the same tab but break the extension connection.

```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [X, Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Use coordinates from step 2's screenshot where "Customer Distribution" appears in the left panel. Confirm from the new screenshot that the page title changed to "Customer Distribution".

---

### 4. Set the Date slicer to the current year

Take a screenshot to find the Date slicer coordinates — it's near the top-left of the page, currently showing "All" or a year value.

**Click the slicer to open it:**
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [SLICER_X, SLICER_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

From the screenshot after clicking, identify the dropdown/options panel showing available years. Find "2026" (or current year) and click it:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [YEAR_X, YEAR_Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

**Verify:** After selecting, call `mcp__Control_Chrome__get_page_content` with the tabId. Confirm the Date slicer line now reads "2026" (not "All"). If it still reads "All", try once more. After 3 failed attempts, proceed with Project Revenue Dataset fallback (Step 5b).

Document in state.yaml: `customer_distribution_slicer_set: true` (or `false` if fallback used).

---

### 5a. Read Customer Distribution data (slicer confirmed = current year)

Call `mcp__Control_Chrome__get_page_content`. The page shows four bar chart sections: Dallas, Houston, Austin, Combined.

Read the **Combined** section — it shows per-account revenue totals across all offices:
```
$8.82M    MasterCard
$5.82M    Wendy's International, …
$5.07M    Autodesk, Inc
...
```

Values are in millions — convert: $5.07M = $5,070,000. Note any truncated values ("$1.3…") — flag them in `truncated_names`.

Also read per-office sections (Dallas, Houston, Austin) to build monthly breakdowns for Row 30 (BoB Revenue tracking). Note: the per-office charts may show the same accounts split by city — sum across cities for per-account total.

---

### 5b. Fallback — Use Project Revenue Dataset page (slicer could not be set)

**Stay in the same tab.** Click "Project Revenue Dataset" in the left nav:
```
browser_batch: [
  {"name": "computer", "input": {"action": "left_click", "coordinate": [X, Y], "tabId": POWERBI_TAB_ID}},
  {"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}
]
```

Call `get_page_content`. This page shows a flat table with exact per-account revenue (all-time, not filtered):
```
City    Revenue       Account Name
Austin  $3,531,308    Autodesk, Inc
Austin  $1,269,468    Intuit, Inc
Dallas  $5,820,xxx    Wendy's International, LLC
```

Sum by account across all cities.

**Flag every entry:** `all_time_not_ytd: true`
Set: `step1_data_source: "project_revenue_dataset_all_time"`

These values MUST NOT be written to F5:F24 without David's confirmation.

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

Build revenue_map:
```json
{
  "month": "2026-04",
  "powerbi_tab_id": 1863722226,
  "customer_distribution_slicer_set": true,
  "all_time_not_ytd": false,
  "step1_data_source": "customer_distribution",
  "revenue_map": {
    "Autodesk Inc": {"revenue": 5070000, "all_time_not_ytd": false, "powerbi_name": "Autodesk, Inc", "confidence": "high"}
  },
  "one_texas_total_revenue": 0,
  "excluded_accounts": [],
  "uncertain_matches": [],
  "unmatched_accounts": [],
  "truncated_names": []
}
```

---

### 8. Update state.yaml

```yaml
current-step: 1
accumulated-context:
  powerbi_tab_id: POWERBI_TAB_ID
  customer_distribution_slicer_set: true
  step1_data_source: "customer_distribution"
  revenue_map: { ... }
  one_texas_total_revenue: 0
  excluded_accounts: []
  uncertain_matches: []
  unmatched_accounts: []
  truncated_names: []
```

---

## SUCCESS METRICS

✅ **Step 1 complete when:**
1. POWERBI_TAB_ID confirmed — no new tabs opened
2. Screenshot taken before every click
3. Customer Distribution page reached via left nav click (not URL navigation)
4. Date slicer clicked to current year and confirmed, OR fallback documented
5. Revenue data extracted per named account
6. Exclusions applied
7. `all_time_not_ytd` correctly set on each entry
8. state.yaml updated

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **POWERBI_TAB_ID not in state.yaml** | Run Step 0 pre-flight. Do not proceed without it. |
| **Screenshot fails ("Browser connection unavailable")** | Stop. Report: "Claude in Chrome extension disconnected — cannot proceed." Do not attempt clicks blind. |
| **Left nav not visible in screenshot** | PowerBI may be loading. Wait 3 seconds, take another screenshot. If still not visible, report the blocker. |
| **Slicer won't respond after 3 click attempts** | Use Project Revenue Dataset fallback (Step 5b). Flag all data as all_time_not_ytd. |
| **All account names truncated** | Use Project Revenue Dataset fallback. |

---

## NEXT STEP

→ `step-02-extract-powerbi-profitability.md`

<!-- system:end -->

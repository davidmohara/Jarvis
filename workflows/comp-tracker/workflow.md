---
name: comp-tracker
description: Monthly update of the Regional Director Compensation Tracker from PowerBI reports and My Leads.xlsx
agent: chase
---

<!-- system:start -->

## INITIALIZATION

### STEP 0 — PRE-FLIGHT (run before anything else)

Before opening PowerBI or the comp tracker, establish the browser tab and enable "Show visuals as tables". **All PowerBI navigation must happen within this single tab — never open a new tab.**

**browser_batch is unreliable — do NOT use it.** The Claude in Chrome extension may be bound to a different session. The only reliable stack is: `execute_javascript` (via `mcp__Control_Chrome__execute_javascript`) + `cliclick` (via `mcp__Control_your_Mac__osascript`) + `get_page_content` (via `mcp__Control_Chrome__get_page_content`).

#### Step 0a — Establish tab

1. Call `mcp__Control_Chrome__list_tabs` to see what's open
2. If a PowerBI tab exists: note its `tabId` — this is the **POWERBI_TAB_ID** for all subsequent steps
3. If no PowerBI tab exists: call `mcp__Control_Chrome__open_url` with the report URL and `new_tab: false`
4. Store `POWERBI_TAB_ID` in state.yaml accumulated-context
5. Call `mcp__Control_Chrome__get_page_content` to verify the tab is responsive

#### Step 0b — Enable "Show visuals as tables" (MANDATORY — do once per session)

**This is the critical unlock for all PowerBI data extraction. Without it, every page returns chart-only text with no numeric data.**

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

4. Click it: `cliclick c:[centerX],[154+top+height/2]`

5. Verify: `get_page_content` should show "Now showing visuals as tables" at the bottom.

Set `show_visuals_as_tables_enabled: true` in state.yaml.

**TAB RULE — enforced throughout all steps:**
- Never use `mcp__Control_Chrome__open_url` with `new_tab: true` for PowerBI
- Always use POWERBI_TAB_ID when calling execute_javascript or get_page_content
- All clicks use cliclick via osascript — never browser_batch computer actions

### Data Sources Required

| Source | What It Feeds | Format | Canonical Location |
|--------|--------------|--------|-------------------|
| PowerBI One Texas page | Comp 2 regional monthly revenue & gross profit | PowerBI report (2026 year filter) | https://app.powerbi.com/groups/me/reports/c5ce8a51-c79f-4461-9262-932885e44cec (One Texas page) |
| PowerBI Customer Distribution page | Comp 1 named account revenue | PowerBI report (2026 year filter) | https://app.powerbi.com/groups/me/reports/c5ce8a51-c79f-4461-9262-932885e44cec (Customer Distribution page) |
| PowerBI Project Consultant Profitability Dataset | Comp 1 account gross margin %, Comp 1 account profitability | PowerBI report (2026 year filter) | https://app.powerbi.com/groups/me/reports/c5ce8a51-c79f-4461-9262-932885e44cec (Project Consultant Profitability Dataset page) |
| My Leads.xlsx (OneDrive canonical) | Leads sheet sync, commission eligibility | Excel via M365 MCP | `file:///b!ilmQNHdRSEuxhG1Y66o6s2pUiIQPYJdBpYjAjbtZ8aRPj2M3V6pnT7CvN3AYbbdR/01ZA7BKHDIRSDTOJSU5JF2L2KUC4DMNJMF` |

### State Keys Set at Initialization

These must be written to state.yaml in Step 0 before any other step runs:

```yaml
accumulated-context:
  month: "YYYY-MM"
  comp_tracker_file_path: "/sessions/{session-id}/mnt/IES/systems/compensation/2026 Comp Tracker.xlsx"
  powerbi_tab_id: null                   # Set in Step 0 — required before Steps 1, 2, 4
  show_visuals_as_tables_enabled: false  # Set to true after Step 0b completes
  cliclick_offset_y: 154                 # screen_y = 154 + page_y (window_y:33 + chrome_ui:121)
  chrome_ui_height: 121                  # outerHeight(949) - innerHeight(828)
  slicer_year: "2026"                    # Year filter applied in Step 1 — persists across pages
  customer_distribution_slicer_set: false # Set to true after Step 1 slicer confirmed
```

### File Paths

- **Comp Tracker**: `systems/compensation/2026 Comp Tracker.xlsx`
- **Staging Revenue Extract**: `/tmp/powerbi-revenue-extract-YYYY-MM.xlsx`
- **Staging Profitability Extract**: `/tmp/powerbi-profitability-extract-YYYY-MM.xlsx`
- **State File**: `workflows/comp-tracker/state.yaml`

### PowerBI Click Stack

**browser_batch is unreliable.** The only confirmed working click approach:

```
screen_x = page_x                          (no x offset — window starts at x=0)
screen_y = window_y + chrome_ui_height + page_y
         = 33 + 121 + page_y
         = 154 + page_y
```

Chrome UI height = `outerHeight(949) - innerHeight(828) = 121px`. Window y = 33. DevicePixelRatio = 2 (Retina) but cliclick uses logical pixels — no scaling needed.

**Workflow:**
1. `execute_javascript` → `getBoundingClientRect()` on target element → compute screen coords
2. `osascript` → `cliclick c:[screen_x],[screen_y]`
3. `get_page_content` → verify the click had the expected effect

### PowerBI Year Filter Protocol

**This applies to Steps 1, 2, and 4 — all three PowerBI extractions.**

#### Known behavior (confirmed 2026-04-22 with cliclick stack)

| Page | Table view available? | Year labels in rows? | Slicer clickable via cliclick? |
|------|----------------------|---------------------|-------------------------------|
| Customer Distribution | ✅ Yes (when "Show visuals as tables" enabled) — exact dollar values | ❌ No year per row | ✅ YES — confirmed working. Set once, persists across all pages. |
| Project Consultant Profitability Dataset | ✅ Yes (when "Show visuals as tables" enabled) | ❌ No year per row | ✅ Slicer carries from step 1 — no need to re-set |
| One Texas | ✅ Yes (tabular with year+month per row) | ✅ Yes — rows labeled "2026, January" etc | ✅ Slicer carries from step 1 — no need to re-set |
| Project Revenue Dataset | ✅ Yes (tabular, exact dollars) | ❌ No year per row — shows all-time flat list | Fallback only — use if Customer Distribution fails |

**"Show visuals as tables" PERSISTS across page navigations** within a session. Enable once in Step 0 — it stays active.

**Date slicer PERSISTS across page navigations** once set on Customer Distribution. Set it in Step 1 — it carries automatically to Profitability Dataset and One Texas pages.

#### Extraction strategy per page

**Step 1 — Customer Distribution page:**
- Enable "Show visuals as tables" (Step 0b, if not already done)
- Navigate to Customer Distribution page via JS click
- Set Date slicer to current year via cliclick (use JS to find coordinates)
- Call `get_page_content` — returns exact per-account revenue in tabular format
- Slicer persists: Steps 2 and 4 inherit this filter automatically

**Step 2 — Project Consultant Profitability Dataset page:**
- Navigate via JS click
- Verify slicer still shows current year (it should carry automatically)
- Call `get_page_content` — returns GM% and profitability data in tabular format

**Step 4 — One Texas page:**
- Navigate via JS click
- Verify slicer still shows current year
- Call `get_page_content` — rows are labeled "2026, January | Austin $X | Dallas $X | Houston $X"
- Filter by reading only rows starting with the current year label

**Fallback — if Customer Distribution slicer cannot be set:**
- Navigate to Project Revenue Dataset page
- Call `get_page_content` — shows all-time flat list (no year filter)
- Flag ALL data as `all_time_not_ytd: true`
- Do NOT write to F5:F24 without David's confirmation

---

### Key Metrics & Thresholds

- **Commission Rate**: 3% of Gross Margin
- **Commission Period**: First 12 months from client's first revenue date
- **Commission-Eligible Criteria**: All My Leads.xlsx entries where `Passed To ≠ "---"`, plus entries where `Passed To = "Me"` (David is AM)
- **Named Accounts (20)**: 7-Eleven, Charles Schwab & Co, McKesson Corporation, Wendy's International LLC, Insperity Services LP, PriceSmart, Autodesk Inc, Intuit Inc, Siemens Industry Inc, ORIX Corporation USA, AT&T Services Inc, Constellation Energy, Marriott, Kirby Corp, Expedia, Massimo, CBRE, Tenet, Texas Instruments, Builders First Source
- **One Texas 2025 Baseline**: $72,200,000 revenue; 6% growth target = $76,532,000
- **Exclusions**: Winnipeg revenue, Canadian AT&T revenue
- **Component 3 OTE**: $10,000/month (up to $5,000 Strategic Partnerships/GMS, up to $5,000 Exec Programs/Account Plans)

---

## STATE CHECK

Before starting, read `state.yaml` and apply the following 4-case handler:

**Case 1: status = in-progress**
→ Resume from `current-step`. Read the step file, check outputs so far, and continue where you left off. Do not restart.

**Case 2: status = not-started**
→ Proceed to EXECUTION. Begin at step 1.

**Case 3: status = complete**
→ Confirm with Master: "This workflow completed on [completion date]. Should I run it again?" Wait for confirmation before re-running. If re-running, reset status to not-started, clear accumulated context, and proceed.

**Case 4: status = aborted**
→ Surface immediately to Master: "This workflow was aborted at [current-step] on [date]. Original error: [notes]. Should I resume, restart, or discard?"

---

## EXECUTION

Run the 8 steps below in strict order. Each step is self-contained and reads its own file for detailed execution instructions.

| # | Step | File | What It Does |
|---|------|------|-------------|
| 1 | Extract Revenue from PowerBI | `steps/step-01-extract-powerbi-revenue.md` | Open PowerBI Customer Distribution page, set year filter to 2026, extract by-account revenue data (named accounts + totals), build revenue map, exclude Winnipeg/Canadian AT&T |
| 2 | Extract Profitability from PowerBI | `steps/step-02-extract-powerbi-profitability.md` | Open PowerBI Project Consultant Profitability Dataset, set year filter to 2026, extract account-level gross margin %, profitability metrics |
| 3 | Update Comp 1 | `steps/step-03-update-comp1.md` | Open comp tracker, write YTD revenue and GM% per named account into Comp 1 sheet, write monthly totals, flag uncertain matches |
| 4 | Extract & Update Comp 2 | `steps/step-04-extract-update-comp2.md` | Open PowerBI One Texas page, set year filter to 2026, extract monthly regional revenue/cost/GP, write into Comp 2 sheet, calculate cumulative growth vs. 6% baseline, flag if below threshold |
| 5 | Sync Leads | `steps/step-05-sync-leads.md` | Read My Leads.xlsx from canonical URI, sync new rows into comp tracker Leads sheet, build commission-eligible list |
| 6 | Match Commissions | `steps/step-06-match-commissions.md` | Cross-reference commission-eligible leads vs. PowerBI revenue, open commission records, calculate 12-month commission windows, write Commissions sheet |
| 7 | Prompt Comp 3 | `steps/step-07-prompt-comp3.md` | Scan calendar and Plaud transcripts for qualifying strategic activities, present prompt to David, write confirmed entries to Comp 3 sheet |
| 8 | Close | `steps/step-08-close.md` | Deliver one-screen summary, write state.yaml, delete staging files |

---

<!-- system:end -->

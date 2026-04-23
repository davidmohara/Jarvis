---
name: comp-tracker
description: Monthly update of the Regional Director Compensation Tracker from PowerBI reports and My Leads.xlsx
agent: chase
---

<!-- system:start -->

## INITIALIZATION

### STEP 0 — PRE-FLIGHT (run before anything else)

Before opening PowerBI or the comp tracker, establish the browser tab that will be used for the entire workflow. **All PowerBI navigation must happen within this single tab — never open a new tab.**

1. Call `mcp__Control_Chrome__list_tabs` to see what's open
2. If a PowerBI tab exists: note its `tabId` — this is the **POWERBI_TAB_ID** for all subsequent steps
3. If no PowerBI tab exists: open one by navigating the current active tab to the report URL — do NOT use `new_tab: true`
4. Store `POWERBI_TAB_ID` in state.yaml accumulated-context
5. Test the browser_batch connection: take a screenshot of the tab using `mcp__Claude_in_Chrome__browser_batch` with `{"name": "screenshot", "input": {"tabId": POWERBI_TAB_ID}}`
6. If screenshot succeeds: proceed to Step 1
7. If screenshot fails with "Browser connection is unavailable": **stop immediately** and report: "Claude in Chrome extension not connected — cannot proceed. Ask David to reconnect the extension, then re-run." Do NOT attempt PowerBI steps without a working screenshot.

**TAB RULE — enforced throughout all steps:**
- Every `navigate` action must include `"tabId": POWERBI_TAB_ID` — never omit it
- Every `computer` click action must include `"tabId": POWERBI_TAB_ID`
- Every `screenshot` must include `"tabId": POWERBI_TAB_ID`
- Never use `mcp__Control_Chrome__open_url` with `new_tab: true` for PowerBI
- Never call `navigate` without a tabId — this opens a new tab and breaks the connection

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
  powerbi_tab_id: null        # Set in Step 0 pre-flight — required before Steps 1, 2, 4
  browser_batch_verified: false  # Set to true after first successful screenshot in Step 0
```

### File Paths

- **Comp Tracker**: `systems/compensation/2026 Comp Tracker.xlsx`
- **Staging Revenue Extract**: `/tmp/powerbi-revenue-extract-YYYY-MM.xlsx`
- **Staging Profitability Extract**: `/tmp/powerbi-profitability-extract-YYYY-MM.xlsx`
- **State File**: `workflows/comp-tracker/state.yaml`

### PowerBI Year Filter Protocol

**This applies to Steps 1, 2, and 4 — all three PowerBI extractions.**

#### Known behavior (confirmed 2026-04-22)

The three PowerBI pages behave differently for data extraction:

| Page | Table view available? | Year labels in rows? | Slicer interactive? |
|------|----------------------|---------------------|-------------------|
| One Texas | ✅ Yes (tabular with year+month per row) | ✅ Yes — rows labeled "2026, January" etc | ❌ Cannot click via automation |
| Customer Distribution | ❌ No — chart only, values truncated with "…" | ❌ No year per row | ❌ Cannot click via automation |
| Project Revenue Dataset | ✅ Yes (tabular, exact dollars) | ❌ No year per row — shows all-time flat list | ❌ Cannot click via automation |
| Project Consultant Profitability Dataset | Unknown — not yet confirmed | Unknown | ❌ Cannot click via automation |

**"Show visuals as tables" does NOT persist across page navigations.** It must be enabled fresh on each page.

#### Extraction strategy per page

**Step 4 — One Texas page (WORKS):**
- Navigate to the page, call `get_page_content`
- Rows are labeled "2026, January | Austin $X | Dallas $X | Houston $X"
- Filter by reading only rows starting with the current year label
- This works reliably

**Step 1 — Customer Distribution page (BLOCKED — chart only):**
- Page renders as a visual chart with truncated values ("$1.3…", "$0.6…")
- Cannot read exact per-account revenue from page content
- **Workaround**: Use the Project Revenue Dataset page instead — it shows exact per-account YTD totals in table format, but without year filtering
- **Known limitation**: Project Revenue Dataset shows all-time totals when Date=All. Cannot filter to current year via automation.
- **Required action**: David must manually set the Date slicer to current year in the browser, THEN Chase reads the content. OR: use the export-to-Excel approach from the visual's "..." menu.

**Step 2 — Project Consultant Profitability Dataset page:**
- Not yet successfully read in table format
- Same limitation expected — slicer interaction not possible via automation

#### Recommended workaround for Steps 1 and 2

Since Chase cannot set the slicer programmatically, there are two options:

**Option A — Manual slicer assist (preferred):**
1. David opens PowerBI in Chrome
2. David sets Date slicer to current year on Customer Distribution and Profitability pages
3. Chase reads `get_page_content` immediately after — data will reflect the current year filter
4. This is a one-time manual step per run

**Option B — Use Project Revenue Dataset with known limitation:**
- Read Project Revenue Dataset (shows all-time, but exact figures)
- Cross-reference against prior year's known totals to estimate current-year portion
- Flag all figures as "estimated — year filter could not be applied"
- Do not use for comp calculations — use only as a directional reference

**If neither option is available: do not write Comp 1 data. Leave cells blank. Report the blocker clearly.**

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

---
name: comp-tracker
description: Monthly update of the Regional Director Compensation Tracker from WorkDay email reports and My Leads.xlsx
agent: chase
---

<!-- system:start -->

## INITIALIZATION

### Data Sources Required

| Source | What It Feeds | Format | Canonical Location |
|--------|--------------|--------|-------------------|
| WorkDay Revenue Report (Jarvis inbox email) | Comp 1 named account revenue, Comp 2 regional revenue | Email + Excel attachment | `Jarvis` folder in Outlook |
| WorkDay Profitability Report (Jarvis inbox email) | Comp 1 GM%, Comp 2 regional cost | Email + Excel attachment | `Jarvis` folder in Outlook |
| My Leads.xlsx (OneDrive canonical) | Leads sheet sync, commission eligibility | Excel via M365 MCP | `file:///b!ilmQNHdRSEuxhG1Y66o6s2pUiIQPYJdBpYjAjbtZ8aRPj2M3V6pnT7CvN3AYbbdR/01ZA7BKHDIRSDTOJSU5JF2L2KUC4DMNJMF` |

### File Paths

- **Comp Tracker**: `systems/compensation/2026_Regional_Director_Comp_Tracker__David_OHara.xlsx`
- **Staging Revenue**: `/tmp/workday-revenue-YYYY-MM.xlsx`
- **Staging Profitability**: `/tmp/workday-profitability-YYYY-MM.xlsx`
- **State File**: `workflows/comp-tracker/state.yaml`

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
| 1 | Ingest Revenue | `steps/step-01-ingest-revenue.md` | Find WorkDay revenue email in Jarvis inbox, download Excel attachment, parse by account, build revenue map, exclude Winnipeg/Canadian AT&T |
| 2 | Ingest Profitability | `steps/step-02-ingest-profitability.md` | Find WorkDay profitability email, download Excel, pivot project-level data to account-level GM%, recalculate (never average) |
| 3 | Update Comp 1 | `steps/step-03-update-comp1.md` | Open comp tracker, write monthly revenue and GM% per named account into Comp 1 sheet, write monthly totals, flag uncertain matches |
| 4 | Update Comp 2 | `steps/step-04-update-comp2.md` | Write One Texas regional totals (revenue, cost, GP, GM%) into Comp 2 sheet, calculate cumulative growth vs. 6% baseline, flag if below threshold |
| 5 | Sync Leads | `steps/step-05-sync-leads.md` | Read My Leads.xlsx from canonical URI, sync new rows into comp tracker Leads sheet, build commission-eligible list |
| 6 | Match Commissions | `steps/step-06-match-commissions.md` | Cross-reference commission-eligible leads vs. WorkDay revenue, open commission records, calculate 12-month commission windows, write Commissions sheet |
| 7 | Prompt Comp 3 | `steps/step-07-prompt-comp3.md` | Scan calendar and Plaud transcripts for qualifying strategic activities, present prompt to David, write confirmed entries to Comp 3 sheet |
| 8 | Close | `steps/step-08-close.md` | Deliver one-screen summary, mark WorkDay emails processed, write state.yaml, delete staging files |

---

<!-- system:end -->

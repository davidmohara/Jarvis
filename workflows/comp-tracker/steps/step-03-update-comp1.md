---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Only write named account revenue.** If an account doesn't match the 20-account list, leave its row blank. Do not create new rows for non-named accounts.
2. **Flag all uncertain matches.** Any account matched with confidence < 95% gets a cell note with the recommendation.
3. **Write monthly, not cumulative.** Each cell in the monthly grid shows that month's revenue/GM%, not YTD.
4. **Never overwrite prior months** without explicit confirmation from David.
5. **Document uncertain accounts.** Create an audit trail (cell notes, sidebar notes) for David to verify.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Open comp tracker; retrieve accumulated-context from Steps 1-2 (revenue_map, profitability_map, named_account_matches, uncertain_matches) | Updated Comp 1 - BoB sheet with monthly revenue and GM% per named account; flagged uncertain matches; revenue summary |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Opening the comp tracker spreadsheet
- Writing monthly revenue and GM% for each named account into the Comp 1 sheet
- Adding cell notes to flag uncertain account matches
- Writing monthly totals and summary rows
- Documenting any non-named accounts (unmatched) for David

**Out of scope:**
- Comp 2 (regional) data — that's step 4
- Commission calculations — that's step 6
- Strategic activities (Comp 3) — that's step 7

---

## YOUR TASK

### 1. Open the comp tracker

Open the spreadsheet:
```
systems/compensation/2026_Regional_Director_Comp_Tracker__David_OHara.xlsx
```

Use `mcp__Excel__By_Anthropic___open_workbook`.

Confirm the sheet tabs are present:
- `Comp 1 - BoB`
- `Comp 2 - Region`
- `Leads`
- `Commissions`
- `Comp 3 - Strategic`

---

### 2. Locate the Comp 1 - BoB sheet

Select the `Comp 1 - BoB` tab. This sheet has the named account list and monthly revenue grid.

**Expected structure:**
- Column A: Account names (20 rows for the 20 named accounts)
- Columns B onward: Monthly columns (e.g., "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026")
- Each cell (Account, Month): Revenue and GM%
- Format: Single cell with revenue value, cell note with GM% and context

OR

- Separate sections: Revenue grid and GM% grid (confirm with actual sheet structure)

**Adapt to the actual spreadsheet layout.** Read the current sheet structure first if unsure.

---

### 3. Write monthly revenue for each named account

From accumulated-context, retrieve `revenue_map` and `named_account_matches`.

For each of the 20 named accounts:

**If matched (confidence ≥ 95%):**
- Find the account's row in the Comp 1 sheet
- Locate the column for this month
- Write the revenue value from revenue_map
- If profitability_available, add cell note: `"Revenue: $X | GM%: Y% | Source: WorkDay [date]"`

**If matched but confidence < 95% (uncertain):**
- Write the revenue value
- Add cell note: `"⚠️  UNCERTAIN MATCH: WorkDay name: [workday_name]. David to confirm. GM%: [gm%]"`

**If no match (unmatched_accounts):**
- Leave the cell blank
- Add a sidebar note (or separate log) documenting the unmatched account name and its revenue
- Output example: `"Unmatched: [workday_name], Revenue: $X. Confirm with David which named account this belongs to."`

---

### 4. Add GM% in cell notes or supplementary column

For each account with profitability data:

- If cell note format: Include GM% in the note: `"Revenue: $X | GM%: Y.YY%"`
- If separate column: Write GM% in a dedicated GM% column adjacent to or below the revenue grid
- If profitability not available: Mark as "Pending" or leave blank

---

### 5. Write monthly totals row

At the bottom of the revenue grid, create summary rows:

```
Row: "Total Named Account Revenue"
  Columns: Sum of revenue for all 20 accounts, by month
  
Row: "Total One Texas Revenue" (from state.yaml accumulated-context)
  Columns: Sum of all included revenue (matching Step 1's one_texas_total_revenue)
  
Row: "Total One Texas GM%"
  Columns: One Texas GM% by month (from Step 2's one_texas_gm_pct)
```

**Formula example (Excel):** For April revenue total:
```
=SUM(B2:B21)  // Assuming accounts are rows 2-21, revenue column is B
```

---

### 6. Document non-named accounts

Create an output log (in state.yaml or as a sidebar note in the spreadsheet) listing:

```
Non-Named Accounts (Not in Comp 1):
  - Unmatched Account Name: [workday_name], Revenue: $X
  - Recommendation: [Manual classification or leave blank]
```

This log will be reviewed by David to determine if any unmatched accounts should be added to the named account list or reassigned.

---

### 7. Flag uncertain matches

For any account matched with confidence < 95%, add a cell note:

```
⚠️  UNCERTAIN MATCH
  WorkDay Name: [workday_name]
  Confidence: [confidence%]
  Recommendation: David to confirm
  Revenue: $X | GM%: Y%
```

Example:
```
⚠️  UNCERTAIN MATCH
  WorkDay Name: "Charles Schwab Institutional"
  Confidence: 85%
  Recommendation: Likely Charles Schwab & Co
  Revenue: $125,000 | GM%: 32.5%
```

---

### 8. Save the spreadsheet

Use `mcp__Excel__By_Anthropic___save_workbook` to save changes.

---

### 9. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 3
accumulated-context:
  (all prior context, plus:)
  comp1_updated: true
  comp1_timestamp: "2026-04-17T10:00:00Z"
  comp1_uncertain_matches: [ ... ]
  comp1_unmatched_revenue: 0.00
  comp1_notes: "..."
```

---

## SUCCESS METRICS

✅ **Step 3 complete when:**
1. Comp 1 - BoB sheet opened and verified
2. Monthly revenue written for all 20 named accounts (matched with confidence ≥ 95%)
3. All uncertain matches (confidence < 95%) flagged with cell notes
4. GM% added in cell notes (if profitability_available) or marked as "Pending"
5. Monthly totals row calculated and written
6. One Texas revenue and GM% rows populated with accumulated totals from Steps 1-2
7. Unmatched accounts documented in sidebar/notes for David
8. Spreadsheet saved
9. accumulated-context in state.yaml updated with comp1 details

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Comp 1 sheet structure unclear** | Read the sheet structure first (row labels, column headers). Ask David if layout differs from expected. Adapt and proceed. |
| **Account match confidence ambiguous** | Use ≥ 95% as the threshold. Below that, flag as uncertain and ask David to confirm. |
| **Multiple WorkDay accounts map to same named account** | Sum their revenue together and note the rollup: "Revenue includes [workday_name1] + [workday_name2]". |
| **Revenue or GM% cell already has data** | Do not overwrite. Ask David: "This cell already contains data from [prior month]. Should I replace it with this month's data?" |
| **Profitability not available** | Write revenue only. Mark GM% cells as "Pending — profitability not yet provided." Continue to step 4. |

---

## NEXT STEP

→ `step-04-update-comp2.md`

Pass all accumulated-context (including comp1_updated flag) to Step 4. Step 4 will update the Comp 2 - Region sheet with One Texas regional totals.

<!-- system:end -->

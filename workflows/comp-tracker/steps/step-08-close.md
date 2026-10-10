---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Deliver summary to Master.** Output the one-screen summary at the end. This is the only output David should see.
2. **Update state.yaml before exiting.** Set status: complete, capture all pending items and uncertainties.
3. **Delete staging files.** Remove `/tmp/powerbi-revenue-extract-*.xlsx` and `/tmp/powerbi-profitability-extract-*.xlsx` after confirmation.
4. **Capture all uncertainties for next run.** List GM% pending, uncertain matches, and leads not yet in WorkDay.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline

| Role | Input | Output |
|------|-------|--------|
| **Chase** | All accumulated-context from Steps 1-7 | One-screen comp summary; state.yaml updated; staging files deleted |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Synthesizing one-screen summary from all comp component data
- Updating state.yaml with completion status and pending items
- Deleting staging Excel files
- Finalizing the workflow run

**Out of scope:**
- Re-calculating any component data (that was done in steps 1-7)

---

## YOUR TASK

### 1. Retrieve all accumulated-context from Steps 1-7

From state.yaml, gather:
- `comp1_*` data (named account revenue, uncertain matches)
- `comp2_*` data (regional revenue, growth %, bonus status)
- `commissions_*` data (new commissions, ongoing, expiring, not-yet-matched)
- `comp3_*` data (strategic items logged, total)
- Current month being processed
- Key thresholds and flags

---

### 2. Build the one-screen summary

Synthesize all data into this exact format:

```
================================================================================
  COMP TRACKER UPDATE — [FULL MONTH NAME] [YEAR]
================================================================================

COMPENSATION AT A GLANCE
┌─────────────────────────────┬──────────────────┬──────────────────┐
│ Component                   │ Status           │ YTD / This Month │
├─────────────────────────────┼──────────────────┼──────────────────┤
│ Base Salary                 │ —                │ $180K (annualized)
│ Comp 1 (Book of Business)   │ [Status]         │ $[amount]        │
│ Comp 2 (Regional Growth)    │ [Status]         │ $[amount]        │
│ Comp 3 (Strategic Impact)   │ [Status]         │ $[amount]        │
│ Commissions                 │ —                │ $[amount]        │
├─────────────────────────────┼──────────────────┼──────────────────┤
│ TOTAL YTD                   │ —                │ $[TOTAL]         │
└─────────────────────────────┴──────────────────┴──────────────────┘

COMPONENT 1 — BOOK OF BUSINESS (Named Accounts)
  Total Revenue This Month: $[comp1_monthly_revenue]
  Named Accounts Updated: [count]/20
  Uncertain Matches: [count] [requires David confirmation on account names]

COMPONENT 2 — REGIONAL GROWTH (One Texas)
  This Month Revenue: $[monthly_revenue]
  YTD Revenue: $[ytd_revenue]
  vs. 2025 Pro-Rated Baseline: $[baseline]
  YTD Growth: [X.XX]% (Target: 6%)
  Bonus Qualification: [ON TRACK / BELOW THRESHOLD by X%]
  
  Gap Analysis (if below 6%):
    - Needed to hit 6%: $[gap_dollars] in remaining [months] months
    - Monthly run rate: $[monthly_run_rate]

COMMISSIONS
  New This Month: [count] clients
    → [ClientName: $amount (Month 1 of 12, expires [Month Year])]
  Ongoing: [count] clients
    → [ClientName: $amount (Month X of 12, [months] remaining)]
  Expiring Next Month: [count]
    → [ClientName — final commission in [Month Year]]
  Not Yet in WorkDay: [count] leads pending revenue
    → [VestMed (45 days), OtherProspect (30 days), ...]
  
  Monthly Commission Total: $[amount]
  YTD Commission Total: $[amount]

COMPONENT 3 — STRATEGIC IMPACT
  Item 1 (Strategic Partnerships/GMS): [Logged $X / Nothing logged]
  Item 2 (Exec Programs/Account Plans): [Logged $X / Nothing logged]
  Total Component 3 This Month: $[amount]

DATA STATUS & FLAGS
  ⚠️  Profitability Data Missing For: [account names, if any]
  ⚠️  Uncertain Account Matches: [account names needing confirmation]
  ⚠️  Leads Not Yet in WorkDay Revenue: [client names and days pending]
  ⚠️  Growth Below Threshold: [X% short of 6% target]

WORKFLOW COMPLETION
  Comp Tracker Updated: [MONTH YEAR]
  Commissions: Open, ongoing, and expiring reviewed
  All components: Current through [MONTH YEAR]
  
  Next Run: [First week of NEXT MONTH]

================================================================================
```

---

### 3. Fill in all placeholders

Using accumulated-context:

**Comp 1 values:**
- `comp1_monthly_revenue`: Sum of named account revenue for this month
- `comp1_accounts_updated`: Count of accounts with new data
- `comp1_uncertain_matches`: List of accounts needing confirmation

**Comp 2 values:**
- `monthly_revenue`: `one_texas_total_revenue` from Step 1
- `ytd_revenue`: Cumulative YTD from Step 4
- `baseline`: Pro-rated 2025 baseline from Step 4
- `ytd_growth`: YTD Growth % from Step 4
- `bonus_status`: "ON TRACK" (if ≥ 6% growth AND ≥ 30% GM) or "BELOW THRESHOLD" (gap in %)
- `gap_dollars`: (if below threshold) dollars needed to hit 6%
- `monthly_run_rate`: YTD Revenue / months elapsed (approximation)

**Commissions values:**
- `new_commissions`: List from Step 6 (client, amount, period end)
- `ongoing_commissions`: List from Step 6 (client, amount, months remaining)
- `expiring_next_month`: List from Step 6
- `not_yet_in_workday`: List from Step 6 (client, days pending)
- `monthly_commission_total`: Sum of new + ongoing commissions for this month
- `ytd_commission_total`: Cumulative commission YTD

**Comp 3 values:**
- `item1_logged`: "Logged $X" or "Nothing logged"
- `item2_logged`: "Logged $X" or "Nothing logged"
- `comp3_total`: Sum of both items (if any)

**Flags:**
- `profitability_missing_for`: Account names (if profitability_available = false)
- `uncertain_matches`: Account names needing David confirmation
- `not_yet_in_workday`: Lead names with days pending
- `growth_below_threshold`: "X% short of 6% target" (if applicable)

---

### 4. Output the summary

Present the formatted summary to Master. This is the primary output of the entire workflow.

```
[Formatted one-screen summary as built in step 2]
```

---

### 5. Update state.yaml

Write the final state to `workflows/comp-tracker/state.yaml`:

```yaml
workflow: comp-tracker
agent: chase
status: complete
session-started: [original session start date/time]
session-id: [session ID from runtime]
current-step: 8
original-request: [original trigger request text, if any]
accumulated-context:
  month: "2026-04"
  comp1_revenue: 0.00
  comp2_revenue: 0.00
  comp2_growth_pct: 0.0
  comp3_total: 0.00
  commissions_this_month: 0.00
  commissions_ytd: 0.00
last_run: "2026-04-17"
last_month_processed: "2026-04"
next_run: "first week of May 2026"
pending_items:
  profitability_missing_for: []
  uncertain_matches: []
  not_yet_in_workday: []
  notes: "Workflow complete. All components updated. Commissions reviewed. Ready for next month."
```

---

### 6. Delete staging files

After confirming the comp tracker has been saved (steps 3-7 already saved it), delete the temporary PowerBI extract files:

```bash
rm /tmp/powerbi-revenue-extract-YYYY-MM.xlsx
rm /tmp/powerbi-profitability-extract-YYYY-MM.xlsx
```

Use `Bash` to execute the delete commands. If files do not exist, that's fine — continue.

---

### 7. Confirm completion to Master

Output a completion message:

```
[Master]: Comp Tracker updated for [MONTH YEAR].
  ✅ Comp 1 (BoB): [count] named accounts updated
  ✅ Comp 2 (Region): [growth %] YTD growth (target: 6%)
  ✅ Commissions: [count] new, [count] ongoing
  ✅ Comp 3: [Item 1 / Item 2] logged
  
  Workflow Status: COMPLETE
  Next Run: [First week of NEXT MONTH]
```

---

## SUCCESS METRICS

✅ **Step 8 complete when:**
1. One-screen summary generated with all placeholder values filled
2. Summary output to Master
3. state.yaml updated with status: complete, last_run, last_month_processed, and all pending items captured
4. Staging files deleted (/tmp/powerbi-*-extract-*.xlsx)
5. Completion confirmation output
6. Workflow exits cleanly

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Summary has missing values** | Fill with available data. Use "Pending" or "N/A" for unavailable values. Note in summary: "Some data unavailable — [reason]". |
| **state.yaml write fails** | Use Bash to write the YAML manually. Ensure file is created with correct schema. |
| **Staging files not found** | Proceed. Files may have already been deleted or never created. Not a failure. |

---

## WORKFLOW END

This is the final step. Workflow is complete. Ready for next month's trigger.

<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never average GM%.** Always recalculate from summed GP and summed revenue: `Account GM% = SUM(GP) / SUM(Revenue)`. Averaging GM% by project biases the result.
2. **Reconcile with revenue.** Revenue figures in profitability report must match Step 1 within 2%. If variance > 2%, flag and ask David before proceeding.
3. **Exclude Winnipeg and Canadian AT&T** from all calculations, same as Step 1.
4. **If profitability email missing:** Do not stop. Log `profitability_available: false`. Continue to Step 3 with GM% marked as pending. David will run the report manually if needed.
5. **Handle project-to-account grouping carefully.** One account may have multiple projects. Sum all their project financials before calculating account-level GM%.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Find WorkDay profitability email in Jarvis inbox; download Excel attachment to `/tmp/workday-profitability-YYYY-MM.xlsx`; retrieve Step 1's accumulated-context | Profitability map keyed by account name; account-level GM%; reconciliation check vs. Step 1 revenue; flag if data unavailable |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Finding and downloading the WorkDay profitability report email from Jarvis inbox
- Parsing project-level profitability Excel data
- Grouping projects by account
- Recalculating account-level GM% from summed financials (never averaging)
- Reconciling revenue figures against Step 1
- Documenting `profitability_available: true/false`

**Out of scope:**
- Writing data to the comp tracker — that's step 3
- Commission calculations — that's step 6

---

## YOUR TASK

### 1. Find the WorkDay profitability email

Search the Jarvis inbox for the WorkDay profitability report:

- Query: "WorkDay" AND ("profitability" OR "Profitability Report" OR "project profitability" OR "cost")
- Folder: `Jarvis`
- Expected subject pattern: Contains "WorkDay", "profitability", "cost", or "report"
- Expected month: Same month as the revenue report from Step 1

Use: `mcp__b8c41a14__outlook_email_search` with `folderName: "Jarvis"` and `query: "WorkDay profitability"`.

**If multiple emails exist:** Select the most recent one matching the current month.

**If NO email found:**
- Do NOT stop. Log `profitability_available: false` in accumulated-context.
- Continue to Step 3 with all GM% fields marked as pending.
- Note: "WorkDay profitability data unavailable. David to provide separately or run manual report."

---

### 2. Download the Excel attachment

If found, read the full email via `read_resource` to access the attachment.

Download the Excel attachment to local staging:
```
/tmp/workday-profitability-YYYY-MM.xlsx
```

---

### 3. Parse profitability data

Open the file using `mcp__Excel__By_Anthropic___open_workbook`:
```
path: /tmp/workday-profitability-YYYY-MM.xlsx
```

Read the entire data range. Expected columns (adapt if structure differs):
- **Account Name** or **Customer Name**
- **Project Name** or **Project ID**
- **Revenue** (YTD or monthly — must match Step 1's time period)
- **Cost** (YTD or monthly)
- **Gross Profit** (Revenue - Cost, or supplied directly)
- **Gross Margin %** (may be pre-calculated, but we will recalculate for accuracy)

Read all data rows.

---

### 4. Apply exclusions

Remove all rows where:
- Account Name contains "Winnipeg" OR
- Account Name contains "AT&T" AND Location/Region contains "Canada" OR "CA"

Same exclusion logic as Step 1.

---

### 5. Pivot project-level data to account-level

Group all project rows by Account Name. For each account, calculate:

```
Account Totals:
  - Total Revenue = SUM(Revenue across all projects for this account)
  - Total Cost = SUM(Cost across all projects for this account)
  - Total Gross Profit = SUM(Gross Profit across all projects)
  
Account-Level GM% = Total Gross Profit / Total Revenue
```

**Never average GM% by project.** Always recalculate from sums.

Example:
```
Account: "7-Eleven"
  Project A: Revenue $100K, Cost $70K, GP $30K, GP% = 30%
  Project B: Revenue $50K, Cost $30K, GP $20K, GP% = 40%
  
Correct Account GM%: ($30K + $20K) / ($100K + $50K) = $50K / $150K = 33.33%
WRONG: Average of 30% and 40% = 35% ❌
```

---

### 6. Build profitability map

```json
{
  "month": "2026-04",
  "profitability_available": true,
  "profitability_map": {
    "7-Eleven": {
      "revenue": 49816.00,
      "cost": 35000.00,
      "gp": 14816.00,
      "gm_pct": 0.2972
    },
    "Charles Schwab & Co": {
      "revenue": 0.00,
      "cost": 0.00,
      "gp": 0.00,
      "gm_pct": null
    },
    ...
  },
  "one_texas_total_revenue": 0.00,
  "one_texas_total_cost": 0.00,
  "one_texas_total_gp": 0.00,
  "one_texas_gm_pct": 0.00,
  "excluded_accounts": ["Winnipeg Services", "AT&T Canada"]
}
```

---

### 7. Reconcile with Step 1 revenue

For each account in the profitability_map, compare its revenue against the corresponding revenue in Step 1's revenue_map:

```
Variance = ABS(Profitability Revenue - Step1 Revenue) / Step1 Revenue
```

**Rule:**
- ✅ Variance < 2%: Accept as reconciled
- ⚠️  Variance 2-5%: Flag and ask David if variance is acceptable (timing differences are common)
- ❌ Variance > 5%: Flag as discrepancy. Note: "Do not proceed without confirming revenue sources."

Document all variances in accumulated-context. If any variance > 5%, output the comparison and ask David before continuing.

---

### 8. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 2
accumulated-context:
  (all context from Step 1, plus:)
  profitability_map: { ... }
  profitability_available: true/false
  one_texas_gm_pct: 0.00
  revenue_reconciliation: {
    "7-Eleven": { "step1_revenue": 49816.00, "profitability_revenue": 49816.00, "variance_pct": 0.0 },
    ...
  }
  staging_file_profitability: "/tmp/workday-profitability-2026-04.xlsx"
  notes: "..."
```

---

## SUCCESS METRICS

✅ **Step 2 complete when:**
1. WorkDay profitability email found (or `profitability_available: false` if missing)
2. Excel attachment downloaded to `/tmp/workday-profitability-YYYY-MM.xlsx`
3. All project-level data rows parsed
4. Winnipeg and Canadian AT&T rows removed
5. All accounts grouped and account-level GM% recalculated (not averaged)
6. One Texas totals calculated (sum of revenue, cost, GP, and recalculated GM%)
7. Revenue reconciliation vs. Step 1 completed; all variances < 5% (or flagged)
8. accumulated-context in state.yaml fully populated with profitability_map and reconciliation results

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **WorkDay profitability email not in Jarvis inbox** | Do NOT stop. Set `profitability_available: false` and continue to Step 3. Note in state.yaml. |
| **Excel attachment corrupted or unreadable** | Flag. If revenue-only is acceptable, continue with `profitability_available: false`. Otherwise, ask David. |
| **Revenue variance > 5% for any account** | Flag in accumulated-context and ask David: "Revenue variance detected for [account]. Confirm source before proceeding." |
| **Projects don't roll up to accounts clearly** | Ask David for account mapping or clarification before pivoting. |
| **GM% calculation ambiguous (negative GP, zero revenue, etc.)** | Document the exception. Mark GM% as null for that account. Flag for David. |

---

## NEXT STEP

→ `step-03-update-comp1.md`

Pass all accumulated-context (both Step 1 and Step 2 outputs) to Step 3. Step 3 will write merged data into the comp tracker spreadsheet.

<!-- system:end -->

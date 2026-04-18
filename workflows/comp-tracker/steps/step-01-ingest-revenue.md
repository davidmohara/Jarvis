---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never skip exclusions.** Winnipeg and Canadian AT&T revenue must be stripped before building any maps.
2. **Fuzzy match named accounts.** Use partial name matching — WorkDay project names may not exactly match the canonical account list.
3. **Flag uncertain matches.** Any account match with confidence < 95% gets a cell note in step 3.
4. **Sum, never average.** All totals are sums of individual accounts.
5. **Preserve exact figures.** Do not round or estimate revenue; use exact values from the Excel export.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Search Jarvis inbox for WorkDay revenue email; download Excel attachment to `/tmp/workday-revenue-YYYY-MM.xlsx` | Structured revenue map keyed by account name and month; one-texas totals; list of excluded accounts |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Finding and downloading the WorkDay revenue report email from Jarvis inbox
- Parsing Excel data into structured format
- Fuzzy-matching account names to the canonical named account list
- Calculating One Texas totals (excluding Winnipeg and Canadian AT&T)
- Documenting any uncertain matches for David's review in step 3

**Out of scope:**
- Writing data to the comp tracker — that happens in step 3
- Profitability calculations — that's step 2
- Commission calculations — that's step 6

---

## YOUR TASK

### 1. Find the WorkDay revenue email

Search the Jarvis inbox folder in Outlook for the WorkDay revenue report email:

- Query: "WorkDay" AND ("revenue" OR "Revenue Report" OR "account revenue")
- Folder: `Jarvis`
- Expected subject pattern: Contains "WorkDay", "revenue", "report"
- Expected month: Current or previous month (determine by context or ask)

Use: `mcp__b8c41a14__outlook_email_search` with `folderName: "Jarvis"` and `query: "WorkDay revenue"`.

**If multiple emails exist:** Select the most recent one whose attachment date or subject matches the current update month.

**If NO email found → STOP.** Output:
```
ERROR: WorkDay revenue email not found in Jarvis inbox.
Action: Cannot proceed until the automated WorkDay report is configured.
Contact: Confirm with Master that WorkDay is sending monthly revenue reports to david.ohara@improving.com / Jarvis folder.
```

---

### 2. Download the Excel attachment

Once you've identified the email, read the full email message via `read_resource` to access the attachment.

Download the Excel attachment to local staging:
```
/tmp/workday-revenue-YYYY-MM.xlsx
```
where `YYYY-MM` is the month being reported (e.g., `/tmp/workday-revenue-2026-04.xlsx`).

Use `Desktop Commander` process to copy the file, or request the attachment directly from the email body if supported by the MCP.

---

### 3. Parse the Excel file

Open the file using `mcp__Excel__By_Anthropic___open_workbook`:
```
path: /tmp/workday-revenue-YYYY-MM.xlsx
```

Read the data. Expected columns (adapt if WorkDay structure differs):
- **Account Name** or **Customer Name**
- **Project Name** or **Project ID**
- **Month** or **Date Range** (or infer from file metadata)
- **Revenue** (billed/recognized)
- **Cost** (optional, may be in profitability report only)
- **Gross Profit** (optional)
- **Gross Margin %** (optional)

Read the entire data range to identify all rows. Get the header row first, then all data rows.

---

### 4. Apply exclusions

Remove all rows where:
- Account Name contains "Winnipeg" OR
- Account Name contains "AT&T" AND Location/Region contains "Canada" OR "CA"

Document excluded accounts in the output.

---

### 5. Build revenue map

Construct the following JSON structure:

```json
{
  "month": "2026-04",
  "revenue_map": {
    "7-Eleven": {
      "revenue": 49816.00,
      "cost": 0.00,
      "gp": 0.00,
      "gm_pct": null
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
  "excluded_accounts": ["Winnipeg Consulting", "AT&T Canada"]
}
```

- **revenue_map**: Keyed by account name (use canonical named account names where matched)
- **one_texas_total_***: Sum of all included accounts (revenue, cost, GP)
- **excluded_accounts**: List of accounts removed due to exclusion rules

---

### 6. Match accounts to canonical named account list

For each account in the revenue_map, determine if it matches one of the 20 named accounts:

**Named Accounts:**
1. 7-Eleven
2. Charles Schwab & Co
3. McKesson Corporation
4. Wendy's International LLC
5. Insperity Services LP
6. PriceSmart
7. Autodesk Inc
8. Intuit Inc
9. Siemens Industry Inc
10. ORIX Corporation USA
11. AT&T Services Inc
12. Constellation Energy
13. Marriott
14. Kirby Corp
15. Expedia
16. Massimo
17. CBRE
18. Tenet
19. Texas Instruments
20. Builders First Source

Use **fuzzy matching** (partial name overlap, case-insensitive). Document match confidence:
- ✅ **High (>95%)**: Exact match or very clear partial match (e.g., "7-Eleven Inc" → "7-Eleven")
- ⚠️  **Medium (80-95%)**: Partial match but potential ambiguity (e.g., "Charles Schwab" → "Charles Schwab & Co")
- ❌ **Low (<80%)**: Unclear or no match — flag for David to confirm

Build a separate map for named account matches:

```json
{
  "named_account_matches": {
    "7-Eleven": {
      "matched": true,
      "confidence": "high",
      "workday_name": "7-Eleven Inc",
      "revenue": 49816.00
    },
    "Massimo": {
      "matched": false,
      "confidence": "none",
      "workday_name": null,
      "revenue": 0.00,
      "note": "Not found in this month's WorkDay report"
    },
    ...
  },
  "unmatched_revenue": 0.00,
  "uncertain_matches": [
    {
      "workday_name": "Charles Schwab Institutional",
      "candidates": ["Charles Schwab & Co"],
      "recommendation": "Likely Charles Schwab & Co; David to confirm"
    }
  ]
}
```

---

### 7. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 1
accumulated-context:
  month: "2026-04"
  revenue_map: { ... }
  named_account_matches: { ... }
  unmatched_accounts: []
  uncertain_matches: [ ... ]
  one_texas_total_revenue: 0.00
  excluded_accounts: [ ... ]
  staging_file: "/tmp/workday-revenue-2026-04.xlsx"
```

---

## SUCCESS METRICS

✅ **Step 1 complete when:**
1. WorkDay revenue email found in Jarvis inbox (or error reported if not)
2. Excel attachment downloaded to `/tmp/workday-revenue-YYYY-MM.xlsx`
3. All data rows parsed into revenue_map
4. Winnipeg and Canadian AT&T rows removed
5. One Texas totals calculated (sum of all included accounts)
6. All accounts matched (or flagged as uncertain) against named account list
7. Uncertain matches documented with recommendations
8. accumulated-context in state.yaml fully populated with all outputs

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **WorkDay email not in Jarvis inbox** | STOP. Report: "WorkDay revenue email not found. Cannot proceed until email is configured." |
| **Excel attachment corrupted or unreadable** | STOP. Report: "Excel attachment cannot be opened. Please redownload from WorkDay." |
| **Revenue figures differ from prior month by >20%** | Flag in accumulated-context. Note: "Revenue variance — confirm with David before proceeding to step 3." |
| **No accounts match any named account list** | Continue. Document all as unmatched. David will review in step 3. |
| **Winnipeg/Canadian AT&T exclusion rule unclear on a row** | Flag and ask David for clarification before excluding. |

---

## NEXT STEP

→ `step-02-ingest-profitability.md`

Pass along all accumulated-context from this step to step 2. Step 2 will read the profitability report and merge GM% back into the revenue map.

<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **ALWAYS read from canonical OneDrive URI.** Never read from a local IES copy. If a local copy exists in IES/systems/, flag it for deletion after this step.
2. **Match on Date + Client.** When comparing against the comp tracker Leads sheet, use Date and Client as the composite key.
3. **Commission-eligible = Passed To ≠ "---".** Including entries where Passed To = "Me" (David is the AM).
4. **Check commission windows.** Any client already in the Commissions sheet must have its 12-month window rechecked. If expired (> 12 months from Date Closed), mark as expired.
5. **Never overwrite existing Leads.** Preserve all existing rows. Only append new entries.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Read My Leads.xlsx from canonical OneDrive URI; open comp tracker Leads sheet | Updated Leads sheet with new entries synced; commission-eligible list (passed_lead + am_account); expired commission list |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Reading My Leads.xlsx from canonical OneDrive source
- Comparing new entries against comp tracker Leads sheet
- Appending new rows to Leads sheet
- Identifying all commission-eligible leads (Passed To ≠ "---")
- Checking expiration dates on known commissions
- Building the eligible leads list for Step 6

**Out of scope:**
- Commission calculations — that's step 6
- Strategic activities (Comp 3) — that's step 7

---

## YOUR TASK

### 1. Read My Leads.xlsx from canonical OneDrive URI

Use the M365 MCP to read the file from the canonical location:

**OneDrive URI:** `file:///b!ilmQNHdRSEuxhG1Y66o6s2pUiIQPYJdBpYjAjbtZ8aRPj2M3V6pnT7CvN3AYbbdR/01ZA7BKHDIRSDTOJSU5JF2L2KUC4DMNJMF`

**Web URL (fallback):** `https://improving-my.sharepoint.com/personal/david_ohara_improving_com/Documents/Sales/My Leads.xlsx`

Use `mcp__b8c41a14__read_resource` to fetch the file. Parse all rows from the Leads sheet.

**Expected columns:**
- Year
- Date (format: YYYY-MM-DD or MM/DD/YYYY)
- Client (company name)
- Passed To (Account Manager name, "Me", or "---")

Read ALL rows (do not limit to recent).

---

### 2. Check for local IES copy

After reading from OneDrive, search the IES for any local copy of My Leads.xlsx:
```
Location: systems/compensation/ or similar
```

If a local copy exists, flag it in the output: "Local copy found at [path]. Delete after sync confirmation."

---

### 3. Read current Leads sheet from comp tracker

The comp tracker should still be open from Steps 3-4. Select the `Leads` tab.

**Expected columns (match My Leads.xlsx):**
- Year
- Date
- Client
- Passed To

Read all existing rows to build a comparison map.

---

### 4. Identify new entries

Compare My Leads.xlsx against the comp tracker Leads sheet using **Date + Client** as the composite key:

```
For each row in My Leads.xlsx:
  If (Date, Client) pair NOT found in comp tracker Leads sheet → NEW
  Else → EXISTING (already synced)
```

Count new entries.

---

### 5. Append new entries to Leads sheet

For each new entry identified in step 4:
- Write the new row to the comp tracker Leads sheet
- Preserve all existing rows (do NOT overwrite or delete)
- Maintain the same column order and formatting

Write to the end of the current data range in the Leads sheet.

Example append:
```
Original Leads sheet (rows 1-50): Existing entries
New entries from My Leads.xlsx: Append as rows 51+
```

---

### 6. Build commission-eligible list

From My Leads.xlsx, identify all commission-eligible entries:

**Eligibility rule:**
```
Commission-Eligible = Passed To ≠ "---"

That includes:
  - Passed To = [Account Manager name] → "passed_lead" type
  - Passed To = "Me" → "am_account" type (David is AM)

NOT eligible:
  - Passed To = "---" → dead lead
```

For each eligible entry, document:
```json
{
  "client": "VestMed",
  "date_logged": "2026-01-28",
  "passed_to": "Stephen Johnson",
  "commission_type": "passed_lead",
  "year": 2026,
  "in_workday": false
}
```

The `in_workday` field will be populated in Step 6 after matching against WorkDay revenue.

---

### 7. Separate AM accounts (Passed To = "Me")

From the commission-eligible list, extract a separate sub-list of accounts where Passed To = "Me":

```json
{
  "client": "ProspectCorp",
  "date_logged": "2026-02-15",
  "commission_type": "am_account",
  "year": 2026
}
```

These are David's direct AM accounts (ongoing revenue relationships). They take priority for commission matching in Step 6.

---

### 8. Check commission expiration windows

Open the comp tracker Commissions sheet. For any client already listed with a Date Closed:

```
Commission Window = Date Closed + 12 months

If Date Closed + 12 months > today → ACTIVE (still in 12-month window)
If Date Closed + 12 months ≤ today → EXPIRED (no further commission)
```

Build a list of expired commissions:
```json
{
  "expired_clients": [
    { "client": "OldClient", "date_closed": "2024-12-15", "window_end": "2025-12-15" }
  ]
}
```

These entries are passed to Step 6 as informational (no further action needed in Step 6).

---

### 9. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 5
accumulated-context:
  (all prior context, plus:)
  leads_synced: true
  new_leads_count: 0
  commission_eligible: [ ... ]
  am_accounts: [ ... ]
  passed_leads: [ ... ]
  expired_commissions: [ ... ]
  leads_timestamp: "2026-04-17T10:00:00Z"
```

---

## SUCCESS METRICS

✅ **Step 5 complete when:**
1. My Leads.xlsx read from canonical OneDrive URI (not local copy)
2. Comp tracker Leads sheet compared against My Leads.xlsx
3. New entries identified and appended to Leads sheet
4. Commission-eligible list built (all rows where Passed To ≠ "---")
5. AM accounts (Passed To = "Me") separated and documented
6. Expired commissions identified and listed
7. Spreadsheet saved
8. accumulated-context in state.yaml fully populated with leads data

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Cannot read from canonical OneDrive URI** | Try web URL as fallback. If both fail, ask David: "My Leads.xlsx at canonical URI is not accessible. Is the file still at [URI]?" |
| **My Leads.xlsx file not found** | Stop with: "My Leads.xlsx not found at canonical location. Check OneDrive / David's Documents / Sales folder." |
| **Leads sheet structure in comp tracker unclear** | Read the sheet structure first. Match to My Leads.xlsx columns. Ask David if layout differs. |
| **Date/Client format differs between sources** | Normalize both to YYYY-MM-DD format for matching. Note any discrepancies. |
| **Commission expiration date ambiguous** | Use Date Closed + 12 months as the window end. If Date Closed is missing, flag and ask David. |

---

## NEXT STEP

→ `step-06-match-commissions.md`

Pass all accumulated-context (commission_eligible list, am_accounts, expired_commissions) to Step 6. Step 6 will cross-reference these leads against WorkDay revenue and calculate commission amounts.

<!-- system:end -->

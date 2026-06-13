---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Commission Rate: 3% of Gross Margin, period 12 months from Date Closed.** Date Closed = first month client appears in WorkDay revenue.
2. **Match client names fuzzy.** WorkDay account names may differ from My Leads entries. Use best-match logic and flag uncertain matches.
3. **Use actual GM from profitability data.** If profitability unavailable, estimate using historical GM% from Comp 1 named accounts and flag as estimated.
4. **Check 12-month expiration window.** If Commission Period End ≤ today, no further commission. If Period End > today, commission applies this month.
5. **Flag new commissions, expiring commissions, and not-yet-matched leads.** Do not silently write to the sheet — surface all events to David.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Retrieved from Step 5: commission_eligible list, am_accounts; from Steps 1-2: revenue_map, profitability_map; current comp tracker Commissions sheet | Updated Commissions sheet with new commission records, ongoing commission updates, and flagged events (new, expiring, not-yet-matched) |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Cross-referencing commission-eligible leads vs. WorkDay revenue
- Identifying new commission events (first revenue appearance)
- Checking expiration windows on existing commissions
- Calculating monthly commissions (GM% × 3%)
- Writing commission rows to the Commissions sheet
- Flagging new events, expiring events, and unmatched eligible leads

**Out of scope:**
- Strategic activities (Comp 3) — that's step 7
- Final summary and delivery — that's step 8

---

## YOUR TASK

### 1. Retrieve commission-eligible leads from Step 5

From accumulated-context, get:
- `commission_eligible`: All leads where Passed To ≠ "---" (passed_lead type)
- `am_accounts`: Leads where Passed To = "Me" (David is AM)
- `expired_commissions`: Clients whose 12-month window has passed (no further action needed)

Combine commission_eligible + am_accounts into a single working list for this step.

---

### 2. Retrieve revenue and profitability maps from Steps 1-2

From accumulated-context, get:
- `revenue_map`: Client → revenue by month
- `profitability_map`: Client → GM% by month
- `named_account_matches`: Account fuzzy-matching results

---

### 3. Open the Commissions sheet

The comp tracker should still be open from prior steps. Select the `Commissions` tab.

**Expected columns:**
- Deal / Client
- Date Closed (first revenue month)
- Commission Period Start
- Commission Period End
- Monthly Commission (this month)
- YTD Commission
- Notes (e.g., "Month 3 of 12 — expires MM/DD/YYYY")

**Read the sheet structure first.** Adapt if columns differ.

---

### 4. Identify new commission events

For each lead in the combined commission_eligible + am_accounts list:

**Check 1: Is this client in the WorkDay revenue map?**
```
If client name found in revenue_map:
  → Potential new commission event
  
Else:
  → No revenue yet for this client
  → Mark as "not_yet_in_workday" for later reporting
```

**Check 2: If client is in revenue_map, does a Commissions row already exist?**
```
Search Commissions sheet for a row matching this client name

If row exists AND Period End > today:
  → ONGOING COMMISSION (update with this month's data — see step 6 below)
  
If row exists AND Period End ≤ today:
  → EXPIRED COMMISSION (skip, no further action)
  
If row does NOT exist:
  → NEW COMMISSION EVENT (create a new row — see step 5 below)
```

---

### 5. Create new commission records

For each lead that meets the new commission criteria:

```json
{
  "client": "ClientName",
  "date_closed": "2026-04",
  "commission_period_start": "2026-04",
  "commission_period_end": "2027-03",
  "revenue_this_month": 0.00,
  "gm_this_month": 0.00,
  "gm_pct_this_month": 0.0,
  "commission_this_month": 0.00,
  "notes": "NEW — Month 1 of 12. Window: Apr 2026 - Mar 2027"
}
```

**Calculation:**
```
Date Closed = first month client appears in revenue_map (e.g., "2026-04" for April)
Commission Period End = Date Closed + 12 months (e.g., "2027-03" for April + 12 months)
Revenue This Month = revenue_map[client]["revenue"]
GM This Month = profitability_map[client]["gp"] (gross profit in dollars)
GM% This Month = profitability_map[client]["gm_pct"]
Commission This Month = GM This Month × 3%

Example:
  Revenue: $100,000
  GM%: 35%
  GM (dollars): $35,000
  Commission (3% of GM): $1,050
```

**If profitability data missing:**
```
Use historical GM% from Comp 1 named account or estimate 30% GM (conservative).
Example: Revenue $100K × 30% estimated GM × 3% rate = $900 commission (estimated)
Flag in Notes: "Estimated commission — GM% pending"
```

---

### 6. Update ongoing commission records

For each existing Commissions row where Period End > today:

```
Retrieve this month's GM for that client from profitability_map
Commission This Month = GM × 3%

Update the Commissions sheet row:
  - Monthly Commission [this month column] = [commission amount]
  - Add to YTD Commission total
  - Update Notes: "Month X of 12 — expires [Period End date]"

Calculate months remaining:
  Months Remaining = months between today and Period End
```

---

### 7. Write new and updated commissions to Commissions sheet

For each new or updated commission:

| Column | Value | Example |
|--------|-------|---------|
| Deal / Client | Client name | "VestMed Inc" |
| Date Closed | First revenue month | "2026-04" |
| Commission Period Start | Same as Date Closed | "2026-04" |
| Commission Period End | Date Closed + 12 months | "2027-03" |
| Monthly Commission (Apr) | GM × 3% | $1,050 |
| YTD Commission | Running sum (if April is first month, = monthly) | $1,050 |
| Status | "Active" or "Expiring Next Month" | "Active" |
| Notes | "Month X of 12 — window ends [date]" | "Month 1 of 12 — expires Mar 31, 2027" |

Write to the Commissions sheet:
- New commissions: Append as new rows
- Ongoing commissions: Update existing rows with this month's data

---

### 8. Compile event flags

After writing, compile three lists for David's review:

**List 1: New Commissions (opened this month)**
```json
{
  "new_commissions": [
    { "client": "VestMed", "date_closed": "2026-04", "commission": 1050.00, "period_end": "2027-03" },
    ...
  ],
  "count": 0,
  "total_new_commission": 0.00
}
```

**List 2: Commissions Expiring Next Month**
```json
{
  "expiring_next_month": [
    { "client": "OldClient", "period_end": "2026-05", "ytd_commission": 12000.00 },
    ...
  ],
  "count": 0
}
```

**List 3: Eligible Leads Not Yet in WorkDay Revenue**
```json
{
  "not_yet_in_workday": [
    { "client": "Prospect1", "passed_to": "Stephen Johnson", "days_pending": 45 },
    ...
  ],
  "count": 0
}
```

---

### 9. Save the spreadsheet

Use `mcp__Excel__By_Anthropic___save_workbook`.

---

### 10. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 6
accumulated-context:
  (all prior context, plus:)
  commissions_updated: true
  new_commissions: [ ... ]
  ongoing_commissions: [ ... ]
  expiring_commissions: [ ... ]
  not_yet_in_workday: [ ... ]
  total_commission_this_month: 0.00
  total_commission_ytd: 0.00
  commissions_timestamp: "2026-04-17T10:00:00Z"
  commissions_notes: "..."
```

---

## SUCCESS METRICS

✅ **Step 6 complete when:**
1. Commission-eligible leads retrieved from Step 5
2. Revenue and profitability maps retrieved from Steps 1-2
3. Commissions sheet opened and verified
4. New commission events identified (first revenue appearance)
5. Existing commissions checked for 12-month expiration
6. Monthly commissions calculated (GM × 3%)
7. New and updated commission rows written to Commissions sheet
8. New commissions flagged for David
9. Expiring commissions flagged for David
10. Eligible leads not yet in WorkDay flagged for awareness
11. Spreadsheet saved
12. accumulated-context in state.yaml fully populated with commission data

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Client name fuzzy-match ambiguous** | Use highest-confidence match from Step 1's named_account_matches. If confidence < 80%, flag as uncertain and ask David to confirm client identity. |
| **Profitability data missing for new commission** | Use historical GM% from Comp 1 named account or estimate 30% GM. Flag commission as "Estimated — GM% pending". |
| **Commission Period End calculation unclear** | Use: Date Closed + 12 months. Example: Apr 2026 + 12 months = Apr 2027 (period end Mar 31, 2027). |
| **Revenue in WorkDay but no corresponding profitability data** | Calculate commission on revenue × estimated GM%. Flag: "Profitability data pending. Commission estimated." |
| **Client in Commissions sheet but not in commission_eligible list** | Check if client is in expired_commissions. If expired, skip. If not expired and not eligible, ask David: "Client [name] has active commission but is not in commission-eligible list. Update My Leads or Commissions sheet?" |

---

## NEXT STEP

→ `step-07-prompt-comp3.md`

Pass all accumulated-context (including new_commissions, expiring_commissions, not_yet_in_workday lists) to Step 7. Step 7 will prompt David for Component 3 strategic activity entries.

<!-- system:end -->

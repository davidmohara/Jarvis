<!-- system:start -->
# Commissions Schema and Rules (comp-tracker)

Used by step-06 tasks 5-7 when creating, updating, and writing commission records.

## New record schema and calculation (task 5)

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

## Ongoing record update procedure (task 6)

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

## Commissions sheet column map (task 7)

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
<!-- system:end -->

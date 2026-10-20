<!-- system:start -->
# One-Screen Summary Template (comp-tracker)

Used by step-08 task 2. Fill every placeholder from accumulated-context; the format is exact.

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
<!-- system:end -->

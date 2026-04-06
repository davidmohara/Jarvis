---
step: step-01-revenue
workflow: one-texas-scorecard
description: Pull Revenue Tracker data for One Texas via Chase skill.
---

# Step 1 — Revenue Tracker

Execute the revenue-tracker skill in full:

```
Read and follow: skills/revenue-tracker/SKILL.md
```

This pulls Revenue vs. Target (QTD/LQ/YTD), Revenue vs. Prior Year (QTD/LQ/YTD),
Sequential Quarterly Revenue, and Monthly Revenue for Dallas and South Texas from the
Enterprise Scorecard v4 Financial Outlook page.

## On Completion

Store the full formatted revenue output in `accumulated-context.revenue` in `state.yaml`.
Update `current-step: step-02-co-sell`.

Proceed to `steps/step-02-co-sell.md`.

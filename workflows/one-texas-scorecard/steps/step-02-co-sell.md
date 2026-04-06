---
step: step-02-co-sell
workflow: one-texas-scorecard
description: Pull Co-Sell Pipeline data via Chase skill.
---

# Step 2 — Co-Sell Pipeline

Execute the co-sell-pipeline skill in full:

```
Read and follow: skills/co-sell-pipeline/SKILL.md
```

This pulls live co-sell pipeline and won revenue by partner, gap to Rock 4's $15M target,
from the Improving Sales Analytics PowerBI report.

## On Completion

Store the full formatted co-sell output in `accumulated-context.co_sell` in `state.yaml`.
Update `current-step: step-03-pipeline`.

Proceed to `steps/step-03-pipeline.md`.

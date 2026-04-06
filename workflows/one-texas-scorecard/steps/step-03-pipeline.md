---
step: step-03-pipeline
workflow: one-texas-scorecard
description: Pull Pipeline Snapshot data for One Texas via Chase skill.
---

# Step 3 — Pipeline Snapshot

Execute the pipeline-snapshot skill in full:

```
Read and follow: skills/pipeline-snapshot/SKILL.md
```

This pulls 90-day weighted pipeline (Rock 1 metric), total pipeline, and pipeline by
probability stage for Dallas and South Texas from the Improving Sales Analytics PowerBI report.

## On Completion

Store the full formatted pipeline output in `accumulated-context.pipeline` in `state.yaml`.
Update `current-step: step-04-new-clients`.

Proceed to `steps/step-04-new-clients.md`.

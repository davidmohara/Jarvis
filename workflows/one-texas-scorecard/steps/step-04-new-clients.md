---
step: step-04-new-clients
workflow: one-texas-scorecard
description: Pull New Logos & Anchors YTD counts via Chase skill.
---

# Step 4 — New Clients

Execute the new-clients skill in full:

```
Read and follow: skills/new-clients/SKILL.md
```

This pulls New Logos & Anchors YTD counts for Dallas and South Texas from the Enterprise
Scorecard v4 Sales Momentum page, with gap to Q1 targets.

## On Completion

Store the full formatted new-clients output in `accumulated-context.new_clients` in `state.yaml`.
Update `current-step: step-05-save-to-obsidian`.

Proceed to `steps/step-05-save-to-obsidian.md`.

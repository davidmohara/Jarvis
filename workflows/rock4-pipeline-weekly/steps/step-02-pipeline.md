---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Pull Pipeline Snapshot

## MANDATORY EXECUTION RULES

1. You MUST read and follow `skills/pipeline-snapshot/SKILL.md` in full before pulling any data.
2. You MUST collect Dallas and South Texas separately.
3. You MUST store the formatted output in `state.yaml` under `accumulated-context.pipeline` before advancing.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Live Sales Analytics pipeline data via `skills/pipeline-snapshot/SKILL.md`
**Output:** Formatted pipeline output stored in `state.yaml` under `accumulated-context.pipeline`

---

## YOUR TASK

Read and follow `skills/pipeline-snapshot/SKILL.md` in full.

Collect for Dallas and South Texas separately:
- 90-Day Weighted Pipeline (primary Rock 1 metric)
- Total Pipeline Revenue + Opp Count
- Pipeline by Probability Stage
- Pipeline by Opportunity Type

Store formatted output in `state.yaml` under `accumulated-context.pipeline`.

Update `state.yaml`: `current-step: step-03-save`

## NEXT STEP

Read fully and follow: `step-03-save.md`
<!-- system:end -->

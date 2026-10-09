---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Pull Co-Sell Pipeline Data

## MANDATORY EXECUTION RULES

1. You MUST read and follow `skills/co-sell-pipeline/SKILL.md` in full before pulling any data.
2. You MUST store the formatted output in `state.yaml` under `accumulated-context.cosell` before advancing.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Live Sales Analytics co-sell data via `skills/co-sell-pipeline/SKILL.md`
**Output:** Formatted co-sell output stored in `state.yaml` under `accumulated-context.cosell`

---

## YOUR TASK

Read and follow `skills/co-sell-pipeline/SKILL.md` in full.

Collect:
- Pipeline Revenue w/ Co-Selling Partner (total + by partner)
- Won Revenue w/ Co-Selling Partner (total + by partner)
- Rock 4 gap calculation: `$15M - Pipeline Revenue - Won Revenue`

Store formatted output in `state.yaml` under `accumulated-context.cosell`.

Update `state.yaml`: `current-step: step-02-pipeline`

## NEXT STEP

Read fully and follow: `step-02-pipeline.md`
<!-- system:end -->

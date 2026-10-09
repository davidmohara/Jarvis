---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Pull Revenue Data

## MANDATORY EXECUTION RULES

1. You MUST read and follow `skills/revenue-tracker/SKILL.md` in full before pulling any data.
2. You MUST collect Dallas and South Texas separately.
3. You MUST store the formatted output in `state.yaml` under `accumulated-context.revenue` before advancing.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Live Enterprise Scorecard v4 data via `skills/revenue-tracker/SKILL.md`
**Output:** Formatted revenue output stored in `state.yaml` under `accumulated-context.revenue`

---

## YOUR TASK

Read and follow `skills/revenue-tracker/SKILL.md` in full.

Collect for Dallas and South Texas separately:
- Revenue vs. Target (CQ %, LQ %, YTD %)
- Revenue vs. Prior Year (CQ %, LQ %, YTD %)
- Sequential Quarterly Revenue (CQ %, PQ %, 90-Day Forecast %)
- Monthly Revenue (most recent closed month, dollar figure)

Compile the formatted output per the skill's output format.

Store in `state.yaml` under `accumulated-context.revenue`.

Update `state.yaml`: `current-step: step-02-save`

## NEXT STEP

Read fully and follow: `step-02-save.md`
<!-- system:end -->

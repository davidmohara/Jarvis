---
name: card-which
description: Full-optimization card selection for any purchase
agent: chase
model: sonnet
---

<!-- system:start -->
# Card Optimizer — Which Card?

**Goal:** Identify the single best card for a given purchase, with full optimization across category rates, caps, rotating categories, spend thresholds, card-linked offers, and available credits.

**Agent:** Chase

**Output:** One direct recommendation — best card, earn rate, why, and any stacking opportunities. 2-4 sentences max unless a nuance requires more.
<!-- system:end -->

---

<!-- system:start -->
## INITIALIZATION

### Input Required

- `purchase` — What David is buying (vendor name and/or spend category)
- `amount` — Purchase amount if known (affects cap and threshold math)

### Data Sources Required

| Source | What to Pull | File |
|--------|-------------|------|
| Optimization guide | Category → best card mapping | `systems/credit-cards/optimization-guide.json` |
| Card registry | Rotating categories, caps, spend structure | `systems/credit-cards/card-registry.json` |
| Benefits tracker | Card-linked offers, credits, spend threshold progress | `systems/credit-cards/benefits-tracker.json` |

Read all three files before answering. Never answer from memory alone — data changes monthly.
<!-- system:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read and follow the step file. It maps the purchase to a category, applies the base rate, checks constraints (caps, rotating categories, spend thresholds, card-linked offers, active credits, international FTX), and delivers one direct recommendation.

Read fully and follow: `steps/step-01-recommend.md` to begin.
<!-- system:end -->

---

<!-- system:start -->
## NEVER DO

- Answer without reading all three data files first
- Recommend Amex BCP for international purchases (2.7% FTX fee)
- Use stale memory — data is only valid as of `last_updated` in each file
- Give a list of options when one answer is correct
- Forget to check card-linked offers — they frequently change the answer
<!-- system:end -->

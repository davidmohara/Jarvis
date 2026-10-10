---
name: card-review
description: Monthly benefits audit — credit usage, expiring deadlines, spend threshold pace, card-linked offer savings
agent: chase
model: sonnet
---

<!-- system:start -->
# Card Optimizer — Monthly Benefits Review

**Goal:** Full audit of benefit extraction across all cards. Surface unused credits, expiring deadlines, spend pace, and card-linked offer savings. Produce a dashboard with prioritized action items.

**Agent:** Chase

**Cadence:** 1st of each month (scheduled) or on-demand via "card review."

**Routing:** Expiring-credit alerts → route data to Chief for integration into morning briefing.
<!-- system:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | File |
|--------|-------------|------|
| Benefits tracker | Credit usage, card-linked offers, spend threshold, deadlines | `systems/credit-cards/benefits-tracker.json` |
| Card registry | Full credit/benefit structure, caps, reset cadences | `systems/credit-cards/card-registry.json` |

Read both files fully before building the review. Check `last_updated` in benefits-tracker — if >30 days old, flag that a site walkthrough is needed to refresh data.
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

Read and follow each step file in order. The step files own the detailed process.

| Step | File | What It Does |
|------|------|-------------|
| 1 | `steps/step-01-audit.md` | Read all card data files and build the monthly dashboard: per-card credit usage, zero-usage flags, Discover rotating category, Amex Plat $75K threshold, card-linked offer savings, upcoming deadlines, annual fee ROI |
| 2 | `steps/step-02-actions.md` | Present action items grouped by urgency and get David's decisions; check data freshness |
| 3 | `steps/step-03-update.md` | Write new information back to the tracker files; route time-sensitive alerts to Chief |

Read fully and follow: `steps/step-01-audit.md` to begin.
<!-- system:end -->

---

<!-- system:start -->
## OUTPUT FORMAT

Dashboard-style. Use tables for the credit status section. Use bullet lists for action items. Keep it scannable — David should be able to read this in 60 seconds and know exactly what to do.

Lead with the most urgent item, not the most comprehensive one.
<!-- system:end -->

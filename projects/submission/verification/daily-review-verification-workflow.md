---
name: daily-review-verification
description: Adversarial verification of a daily review. Ralph cross-checks the review output against source data and checks every completion claim against recorded state before the day is committed.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Daily Review Verification Workflow

**Goal:** Confirm that the daily review's narrative matches the source data it claims to summarize, and that every "done today" claim is backed by recorded state, before the review is committed to git and the knowledge system.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the review manifest (review file path, step-01/02 capture outputs, delegation tracker) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (daily-review):** Output vs source data cross-check, completion claims vs state. The producing agent (Chief) synthesizes the narrative from what it believes happened; Ralph re-derives each completion claim from recorded state (`workflows/daily-review/steps/step-01-capture.md` frontmatter outputs, `delegations/tracker.md`, `data/omnifocus-unified.json`) and marks any claim the record does not support as ⚠️ Unverified. This is the daily-review lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Review manifest | Review file path + capture outputs | Passed from Chief as accumulated-context |
| Daily review output | `reviews/daily/{date}.md` (or `auto-{date}.md`) | File system read |
| Capture data | `workflows/daily-review/steps/step-01-capture.md` frontmatter `outputs` | File system read |
| Delegation tracker | `delegations/tracker.md` | File system read |
| Task data | `data/omnifocus-unified.json` | File system read |
| Workflow state | `workflows/daily-review/state.yaml` | File system read |

### Paths

- `daily_review_output` = `reviews/daily/{run-date}.md`
- `capture_step` = `workflows/daily-review/steps/step-01-capture.md`
- `delegation_tracker` = `delegations/tracker.md`
- `omnifocus_data` = `data/omnifocus-unified.json`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `daily-review-verification`; agent: `ralph`.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

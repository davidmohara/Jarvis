---
name: golf-booking-verification
description: Adversarial verification of a golf booking. Ralph cross-checks every success claim against the confirmation evidence, window calculated correctly, no double-booking, actual confirmation recorded before any claim of success.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Golf Booking Verification Workflow

**Goal:** Confirm that a golf booking is real before it is reported as done: the target date was inside the 8-day window and was never substituted, the Gate 3 confirmation and Gate 4 visual verification both actually passed, no prior booking was left live (double-booking), and the success claims match the recorded evidence.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the booking manifest (step outputs, state.yaml, preview-output.json) and returns a verdict table. The caller acts on the results; Ralph never books or cancels anything.

**Adversarial lens (golf-booking):** Booking claims vs confirmation evidence. The producing agent (Sterling) reports what it believes it booked; Ralph re-derives each claim from the recorded evidence: the Gate 1 window arithmetic against `preview-output.json`, the Gate 3 `BOOKING-SUCCESS` result, the Gate 4 visual-verification outcome, and the Gate 6 Slack confirmation. A success claimed with no confirmation, a silently substituted date, or a live prior booking alongside a new one is the failure this lens exists to catch. This is the golf-booking lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Booking manifest | Step output paths + run-date | Passed from Sterling as accumulated-context |
| Step outputs | `workflows/golf-booking/steps/step-0{0..7}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/golf-booking/state.yaml` | File system read |
| Preview output | `workflows/golf-booking/preview-output.json` | File system read |

### Paths

- `state` = `workflows/golf-booking/state.yaml`
- `preview_output` = `workflows/golf-booking/preview-output.json`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK: Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context`: this is data already gathered. Do not re-gather it.
   - Notify: "[Golf Booking Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Golf Booking Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

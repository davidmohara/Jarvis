---
name: golf-preview-verification
description: Adversarial verification of a golf preview. Ralph cross-checks the target dates, per-day calendar status, drought flag, and weather claims against the source data before the preview is trusted by the midnight booking workflow.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Golf Preview Verification Workflow

**Goal:** Confirm that the preview's claims match the source data before golf-booking acts on them at midnight: the target weekend is the correct Friday/Saturday/Sunday at least 8 days out, no day is marked available against a hard calendar block, and the weather and drought claims match the weather and calendar source data.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the preview manifest (step outputs, state.yaml, preview-output.json) and returns a verdict table. The caller acts on the results; Ralph never re-scores anything.

**Adversarial lens (golf-preview):** Preview claims vs weather/course source data. The producing agent (Sterling) reports the weekend's viability; Ralph re-derives each claim from the recorded source: the calendar pull (per-day status), the weather source data, the drought check, and `workflows/golf-booking/preview-output.json`. A wrong target date, a day marked available against a hard block, or a weather claim that contradicts the source is the failure this lens exists to catch. This is the golf-preview lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Preview manifest | Step output paths + run-date | Passed from Sterling as accumulated-context |
| Step outputs | `workflows/golf-preview/steps/step-0{1..5}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/golf-preview/state.yaml` | File system read |
| Preview output | `workflows/golf-booking/preview-output.json` | File system read |
| Weather source | Open-Meteo response for the target weekend | Passed in the manifest, or re-read |

### Paths

- `state` = `workflows/golf-preview/state.yaml`
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
   - Notify: "[Golf Preview Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Golf Preview Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

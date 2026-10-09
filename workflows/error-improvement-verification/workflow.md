---
name: error-improvement-verification
description: Adversarial verification of an error-improvement cycle. Ralph cross-checks every applied-fix claim against the real error log entries and the target files, so no correction is fabricated and no entry is marked resolved without a matching fix.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Error Improvement Verification Workflow

**Goal:** Confirm that every fix the error-improvement cycle claims to have applied traces to a real error entry, that the target-file change is actually present, and that no entry is marked `applied` without a corresponding fix, before the cycle is closed.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the improvement manifest (state.yaml, error entries, pending-changes) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (error-improvement):** Fix claims vs the error log entries. The producing agent (Rigby) reports what it believes it fixed and which entries it resolved; Ralph re-derives each claim from the recorded state: the error entries under `systems/error-tracking/entries/`, the target files named in `files_modified`, and `evolutions/.pending-changes.json`. Each applied fix must trace to a real entry, and each entry marked `applied` must have a matching fix. This is the error-improvement lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Improvement manifest | Run-date + eval-record-id | Passed from Rigby as accumulated-context |
| Workflow state | `workflows/error-improvement/state.yaml` | File system read |
| Error entries | `systems/error-tracking/entries/err-*.json` | File system read |
| Target files | Paths named in `accumulated-context.files_modified` | File system read |
| Pending changes | `evolutions/.pending-changes.json` | File system read |

### Paths

- `state` = `workflows/error-improvement/state.yaml`
- `error_entries` = `systems/error-tracking/entries/`
- `pending_changes` = `evolutions/.pending-changes.json`
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
   - Notify: "[Error Improvement Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Error Improvement Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: morning-briefing-verification
description: Adversarial verification of a delivered morning briefing. Ralph cross-checks every claim in the briefing against the source data files (calendar, email, OmniFocus) and returns a verdict table before the workflow closes.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Morning Briefing Verification Workflow

**Goal:** Confirm that every claim in the delivered morning briefing is traceable to a real source-data file, not asserted from memory, not carried over from a prior day, not invented to fill a section.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the briefing manifest (the briefing file path plus the source-data file paths), reads both sides, and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (morning-briefing):** Calendar / email / OmniFocus cross-check. The producing agent (Chief) knows what it intended to say; Ralph only knows what the briefing says and what the source files contain. He re-derives each factual claim (meeting count and times, due/overdue/flagged task counts, inbox state, delegation status) from `data/calendar-unified.json`, `data/email-unified.json`, and `data/omnifocus-unified.json`, and marks any briefing claim that the data does not support as ⚠️ Unverified. This is the morning-briefing lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Briefing manifest | Briefing file path + claimed source files | Passed from Chief as accumulated-context |
| Delivered briefing | The briefing text as delivered | File system read (`memory/working/morning-briefing-*.md`) |
| Calendar data | `data/calendar-unified.json` | File system read |
| Email data | `data/email-unified.json` | File system read |
| Task data | `data/omnifocus-unified.json` | File system read |
| Delegation tracker | `delegations/tracker.md` | File system read |
| Briefing state | `workflows/morning-briefing/state.yaml` | File system read |

### Paths

- `briefing_working_memory` = `memory/working/morning-briefing-*.md` (most recent)
- `calendar_data` = `data/calendar-unified.json`
- `email_data` = `data/email-unified.json`
- `omnifocus_data` = `data/omnifocus-unified.json`
- `delegation_tracker` = `delegations/tracker.md`
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
   - Notify: "[Morning Briefing Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Morning Briefing Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

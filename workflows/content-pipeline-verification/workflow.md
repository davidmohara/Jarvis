---
name: content-pipeline-verification
description: Adversarial verification of a content-pipeline run. Ralph accounts for every item end to end, from discovered through approved to published, and flags any silent drop.
agent: ralph
model: sonnet
---

<!-- personal:start -->
# Content Pipeline Verification Workflow

**Goal:** Confirm that every item the content pipeline touched is accounted for end to end: discovered items reach `pending-drafts.json`, approved items reach a published or explicitly-explained terminal state, and no item is silently dropped between stages.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the pipeline manifest (step outputs, `pending-drafts.json`, state.yaml) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (content-pipeline):** End-to-end accounting. The producing agent (Harper) reports what it believes it discovered, approved, and published; Ralph re-derives each item's journey from the recorded state: the #content Slack pull, the shared `workflows/content-approval/pending-drafts.json`, and the live Ghost post records. Any item that enters one stage and does not appear in the next, with no recorded explanation, is a silent drop. This is the content-pipeline lens in `agents/adversarial-isolation.md`.
<!-- personal:end -->

---

<!-- personal:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Pipeline manifest | Step output paths + run-date | Passed from Harper as accumulated-context |
| Step outputs | `workflows/content-pipeline/steps/step-0{1,2}-*.md` frontmatter `outputs` | File system read |
| Pending drafts | `workflows/content-approval/pending-drafts.json` (shared state file) | File system read |
| Workflow state | `workflows/content-pipeline/state.yaml` | File system read |
| Ghost post state | `mcp__ghost-blog__get_post` per referenced post id | Ghost API read |
| Slack source | The #content pull for this run | Passed in the manifest, or re-read via `systems/slack-bot/read.py` |

### Paths

- `discover_step` = `workflows/content-pipeline/steps/step-01-discover.md`
- `approve_step` = `workflows/content-pipeline/steps/step-02-approve.md`
- `pending_drafts` = `workflows/content-approval/pending-drafts.json`
- `state` = `workflows/content-pipeline/state.yaml`
<!-- personal:end -->

---

<!-- personal:start -->
## STATE CHECK: Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context`: this is data already gathered. Do not re-gather it.
   - Notify: "[Content Pipeline Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Content Pipeline Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- personal:end -->

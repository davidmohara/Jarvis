---
name: content-discovery-verification
description: Adversarial verification of a content-discovery run. Ralph cross-checks every draft and skip claim against the #content Slack pull and the digest source before the run is closed.
agent: ralph
model: sonnet
---

<!-- personal:start -->
# Content Discovery Verification Workflow

**Goal:** Confirm that every draft content-discovery claims to have produced traces to a real item in the #content Slack pull (or a real digest message), that every claimed skip has a matching source message, and that no angle or post was invented, before the run is closed.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the discovery manifest (step-01 outputs, `pending-drafts.json`, state.yaml) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (content-discovery):** Draft claims vs the Slack/digest source. The producing agent (Harper) reports what it believes it drafted and skipped; Ralph re-derives each claim from the recorded source: the #content pull, the digest text, `workflows/content-approval/pending-drafts.json`, and the Ghost post records. Every draft must trace to a real digest item or source URL; no invented angles. This is the content-discovery lens in `agents/adversarial-isolation.md`.
<!-- personal:end -->

---

<!-- personal:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Discovery manifest | Step-01 output path + run-date | Passed from Harper as accumulated-context |
| Step-01 outputs | `workflows/content-discovery/steps/step-01-discover.md` frontmatter `outputs` | File system read |
| Pending drafts | `workflows/content-approval/pending-drafts.json` | File system read |
| Workflow state | `workflows/content-discovery/state.yaml` | File system read |
| Slack source | The #content pull for this run (message ts + text) | Passed in the manifest, or re-read via `systems/slack-bot/read.py` |

### Paths

- `discovery_step` = `workflows/content-discovery/steps/step-01-discover.md`
- `pending_drafts` = `workflows/content-approval/pending-drafts.json`
- `state` = `workflows/content-discovery/state.yaml`
<!-- personal:end -->

---

<!-- personal:start -->
## STATE CHECK: Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context`: this is data already gathered. Do not re-gather it.
   - Notify: "[Content Discovery Verification]: Resuming from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to the caller:
     "[Content Discovery Verification]: Workflow was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- personal:end -->

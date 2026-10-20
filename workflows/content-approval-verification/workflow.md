---
name: content-approval-verification
description: Adversarial verification of a content-approval run. Ralph cross-checks every resync/cleanup/editorial-edit claim against the live Ghost post state and the Slack thread replies before the run is closed.
agent: ralph
model: sonnet
---

<!-- personal:start -->
# Content Approval Verification Workflow

**Goal:** Confirm that every claim the content-approval run reports matches Ghost's actual state: every tracker entry's status matches the live Ghost post, no entry tracked as `pending` is actually published or scheduled-past, and every claimed editorial edit actually landed in the post.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the run manifest (step-01 outputs, `pending-drafts.json`, state.yaml) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (content-approval):** Tracker state vs Ghost reality. The producing agent (Harper) reports what it resynced, removed, or edited; Ralph re-derives each claim from the recorded state: the live Ghost post records, the #content Slack thread replies, and `workflows/content-approval/pending-drafts.json`. A tracker entry whose status contradicts Ghost, or an edit claim the post does not reflect, is the failure this lens exists to catch. This is the content-approval lens in `agents/adversarial-isolation.md`.
<!-- personal:end -->

---

<!-- personal:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Run manifest | Step-01 output path + run-date | Passed from Harper as accumulated-context |
| Step-01 outputs | `workflows/content-approval/steps/step-01-approve.md` frontmatter `outputs` | File system read |
| Pending drafts | `workflows/content-approval/pending-drafts.json` | File system read |
| Workflow state | `workflows/content-approval/state.yaml` | File system read |
| Ghost post state | `mcp__ghost-blog__get_post` per tracked post id | Ghost API read |
| Slack thread replies | The #content thread replies for this run | Passed in the manifest, or re-read via `systems/slack-bot/read.py` |

### Paths

- `approve_step` = `workflows/content-approval/steps/step-01-approve.md`
- `pending_drafts` = `workflows/content-approval/pending-drafts.json`
- `state` = `workflows/content-approval/state.yaml`
<!-- personal:end -->

---

<!-- personal:start -->
## STATE CHECK: Run Before Any Execution

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `content-approval-verification`; agent: Ralph.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- personal:end -->

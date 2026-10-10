---
name: content-approval-verification
description: Adversarial verification of a content-approval run. Ralph cross-checks every publish/reject/edit status claim against the live Ghost post state and the Slack approval replies before the run is closed.
agent: ralph
model: sonnet
---

<!-- personal:start -->
# Content Approval Verification Workflow

**Goal:** Confirm that every status the content-approval run reports matches Ghost's actual state: approved drafts are actually published, rejected drafts are actually deleted, and no post is claimed `published` while Ghost still shows it as a draft.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the approval manifest (step-01 outputs, `pending-drafts.json`, state.yaml) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (content-approval):** Approval state vs Ghost reality. The producing agent (Harper) reports what it believes it published, rejected, or edited; Ralph re-derives each claim from the recorded state: the live Ghost post records, the #content Slack approval replies, and `workflows/content-approval/pending-drafts.json`. An approved draft that was not actually published, or a status claim that contradicts Ghost, is the failure this lens exists to catch. This is the content-approval lens in `agents/adversarial-isolation.md`.
<!-- personal:end -->

---

<!-- personal:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Approval manifest | Step-01 output path + run-date | Passed from Harper as accumulated-context |
| Step-01 outputs | `workflows/content-approval/steps/step-01-approve.md` frontmatter `outputs` | File system read |
| Pending drafts | `workflows/content-approval/pending-drafts.json` | File system read |
| Workflow state | `workflows/content-approval/state.yaml` | File system read |
| Ghost post state | `mcp__ghost-blog__get_post` per claimed post id | Ghost API read |
| Slack approvals | The #content thread replies for this run | Passed in the manifest, or re-read via `systems/slack-bot/read.py` |

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

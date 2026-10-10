---
name: content-pipeline
description: End-to-end content pipeline orchestrator. Runs content-discovery (draft) then content-approval (publish decision) as one continuous cycle by delegating to those two gated workflows. Both sub-workflows also run standalone on their own schedules.
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "personal content drafting and blog publishing workflow: no decisions about individuals' access to opportunity or resources"
---

<!-- personal:start -->
# Content Pipeline Workflow

**Goal:** Run the full content cycle end to end: discover and draft, then act on David's approval decisions, published to driventodevelop.com. Zero manual drafting.

**Agent:** Harper, Storyteller, Communication & Thought Leadership

**Trigger:** Regular scheduled runs and on-demand controller requests.

**Role:** This workflow is the end-to-end orchestrator. All drafting and publishing logic lives in the two gated sub-workflows; this file only sequences them:

1. `workflows/content-discovery/workflow.md` drafts Ghost posts from #content URLs and digests. Owns GATE 1 (Source Integrity) and GATE 2 (Content Schema Validation).
2. `workflows/content-approval/workflow.md` acts on David's Slack replies: publish, reject, or apply edits/regeneration. Owns GATE 3 (Approval Decision), GATE 4 (Publishing Pre-flight), and GATE 5 (Delivery Verification).

Both sub-workflows also run standalone on their own schedules (`config/scheduled-tasks.json`, task ids `content-discovery` and `content-approval`). Standalone runs and orchestrator runs share one state file, so the dedup rules in each sub-workflow make overlap safe.

**Shared state:** `workflows/content-approval/pending-drafts.json`. Single shared file; discovery appends entries, approval owns the entry lifecycle. Format is documented in content-discovery's STATE TRACKING section.

**Conventions:** Channel, digest format, Slack integration, Ghost blog conventions, voice, and dedup rules are owned by `workflows/content-discovery/workflow.md`. Read that file before executing this pipeline; do not duplicate its conventions here.

---

## STATE CHECK — Run Before Any Execution

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `content-pipeline`; agent: Harper.

## EXECUTION

| # | File | Executed by | Produces |
|---|------|-------------|----------|
| 1 | `steps/step-01-discover.md` (delegates to content-discovery step-01) | spawned subagent (Harper) | Ghost draft posts + Slack notifications |
| 2 | `steps/step-02-approve.md` (delegates to content-approval step-01) | spawned subagent (Harper) | Published/rejected/edited Ghost posts + updated pending-drafts.json |
| 3 | `steps/step-03-git-finalize.md` | spawned subagent (Rigby, git via `skills/git/SKILL.md`) | Committed pipeline state |
| 4 | `steps/step-04-adversarial-verify.md` | spawned subagent (Harper) spawning **Ralph** | `adversarial-verification` guardrail result + verdict |

1. Read and follow `steps/step-01-discover.md`.
2. After completion, read and follow `steps/step-02-approve.md`.
3. After completion, run `steps/step-03-git-finalize.md` to commit all changes.
4. Then run `steps/step-04-adversarial-verify.md`, which spawns **Ralph** with `workflows/content-pipeline-verification/workflow.md` (the end-to-end accounting lens). Ralph re-derives every discovered, approved, and published claim from the recorded state and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/content-pipeline/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate.
<!-- personal:end -->

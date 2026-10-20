---
name: content-pipeline
description: End-to-end content pipeline orchestrator. Runs content-discovery (draft + tracker custodianship) then content-approval (resync + editorial edits) as one continuous cycle by delegating to those two workflows. Publishing is external — David publishes directly in Ghost. Content-discovery also runs standalone on its daily schedule; content-approval runs on demand.
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "personal content drafting and blog publishing workflow: no decisions about individuals' access to opportunity or resources"
---

<!-- personal:start -->
# Content Pipeline Workflow

**Goal:** Run the full content cycle end to end: discover and draft, then resync the tracker with Ghost and apply David's editorial feedback. Zero manual drafting. Publishing is external — David publishes, schedules, and deletes drafts directly in Ghost.

**Agent:** Harper, Storyteller, Communication & Thought Leadership

**Trigger:** Regular scheduled runs and on-demand controller requests.

**Role:** This workflow is the end-to-end orchestrator. All drafting and tracker logic lives in the two sub-workflows; this file only sequences them:

1. `workflows/content-discovery/workflow.md` drafts Ghost posts from #content URLs and digests, and runs the daily tracker resync + cleanup (its step-01 Step 1a). Owns GATE 1 (Source Integrity) and GATE 2 (Content Schema Validation).
2. `workflows/content-approval/workflow.md` resyncs the tracker against live Ghost state, cleans stale entries, and applies David's surgical editorial edits from #content thread replies. It never publishes — the former approve-keyword publish flow (GATE 3/4/5) is retired.

Content-discovery also runs standalone on its daily schedule (`config/scheduled-tasks.json`, task id `content-discovery`); content-approval runs on demand. Standalone runs and orchestrator runs share one state file, so the dedup rules in each sub-workflow make overlap safe.

**Shared state:** `workflows/content-approval/pending-drafts.json`. Single shared file; discovery appends entries and is the custodian of the entry lifecycle (daily resync + cleanup). Format is documented in `workflows/content-discovery/references/pending-drafts-schema.md`.

**Conventions:** Channel, digest format, Slack integration, Ghost blog conventions, voice, and dedup rules are owned by `workflows/content-discovery/workflow.md` and its `references/` files. Read that file before executing this pipeline; do not duplicate its conventions here.

---

## STATE CHECK — Run Before Any Execution

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `content-pipeline`; agent: Harper.

## EXECUTION

| # | File | Executed by | Produces |
|---|------|-------------|----------|
| 1 | `steps/step-01-discover.md` (delegates to content-discovery step-01) | spawned subagent (Harper) | Ghost draft posts + Slack notifications |
| 2 | `steps/step-02-approve.md` (delegates to content-approval step-01) | spawned subagent (Harper) | Resynced/cleaned pending-drafts.json + edited Ghost drafts |
| 3 | `steps/step-03-git-finalize.md` | spawned subagent (Rigby, git via `skills/git/SKILL.md`) | Committed pipeline state |
| 4 | `steps/step-04-adversarial-verify.md` | spawned subagent (Harper) spawning **Ralph** | `adversarial-verification` guardrail result + verdict |

1. Read and follow `steps/step-01-discover.md`.
2. After completion, read and follow `steps/step-02-approve.md`.
3. After completion, run `steps/step-03-git-finalize.md` to commit all changes.
4. Then run `steps/step-04-adversarial-verify.md`, which spawns **Ralph** with `workflows/content-pipeline-verification/workflow.md` (the end-to-end accounting lens). Ralph re-derives every discovered, resynced, and edited claim from the recorded state and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/content-pipeline/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate.
<!-- personal:end -->

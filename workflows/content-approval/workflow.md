---
name: content-approval
description: Resyncs the shared pending-drafts tracker with live Ghost state, cleans stale entries, and executes surgical editorial edits from #content thread replies. Publishing is external — David publishes, schedules, and deletes drafts directly in Ghost; no workflow publishes on his behalf. Runs on demand. workflows/content-pipeline orchestrates content-discovery and this workflow end to end.
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "personal content publishing workflow — no decisions about individuals' access to opportunity or resources"
---

<!-- personal:start -->
# Content Approval Workflow

**Goal:** Keep `pending-drafts.json` in sync with Ghost reality and turn David's #content thread feedback into surgical editorial edits on pending drafts. Nothing more. The approve-keyword publish flow is retired: David publishes (or schedules, or deletes) drafts directly in Ghost, and this workflow's resync picks the new state up from Ghost rather than acting on Slack approval signals.

**Agent:** Harper — Storyteller, Communication & Thought Leadership

**Trigger:** On demand. The former 9 AM / 11 AM / 1 PM / 3 PM scheduled sweep is retired — it never executed reliably, and `workflows/content-discovery` (scheduled daily 6 AM) is now the primary tracker custodian via its step-01 Step 1a, which runs the same resync and cleanup. This workflow remains the on-demand pass when an immediate resync or editorial edit is needed between discovery runs.

**Relationship:** `workflows/content-discovery/workflow.md` is the drafting half of the content pipeline and the custodian of the shared tracker. `workflows/content-pipeline/workflow.md` orchestrates both halves end to end when a full cycle is needed; all read and write one shared state file.

**Companion workflow:** `workflows/content-discovery/workflow.md` drafts new posts, appends to the shared `pending-drafts.json`, and runs the daily resync/cleanup (see STATE TRACKING below).
<!-- personal:end -->

---

<!-- personal:start -->
## CHANNEL

| Channel | ID | Purpose |
|---------|-----|---------|
| #content | C0B160MA3EK | David replies here with editorial feedback on drafts. Approve/reject replies need no action — publishing is external. |

---

## SLACK INTEGRATION

> **CRITICAL — Desktop Commander MUST be loaded before any Slack operations.** See `workflows/content-discovery/references/slack-integration.md` for the full initialization/retry protocol — it applies identically here.

**Reading:** `systems/slack-bot/read.py` via Desktop Commander. **Writing:** `systems/slack-bot/post.py` via Desktop Commander (the `master-slack` skill). No Slack MCP connector is used.

---

## GHOST BLOG CONVENTIONS

This workflow never publishes. It needs Ghost Admin API access for exactly two things: reading post state (`mcp__ghost-blog__get_post`) during resync, and PATCHing drafts during editorial edits.

### Post Status Flow
1. `workflows/content-discovery/workflow.md` creates the post with `status: draft`.
2. David publishes, schedules, or deletes it directly in Ghost — external to all workflows.
3. This workflow (and content-discovery's Step 1a) resyncs `pending-drafts.json` against live Ghost state and cleans out entries whose Ghost lifecycle is complete.

### Ghost Admin API access

Get Admin API key: read `~/Library/Application Support/Claude/claude_desktop_config.json`, find server `ghost-blog`, read `GHOST_ADMIN_API_KEY` (`{key_id}:{hex_secret}`). Generate JWT: header `{"alg": "HS256", "kid": "{key_id}", "typ": "JWT"}`, payload `{"exp": now+300, "iat": now, "aud": "/admin/"}`, signed with `bytes.fromhex(hex_secret)` via PyJWT. The editorial-edit protocols in `references/editorial-edits.md` use this.

---

## STATE TRACKING

**`pending-drafts.json` lives in this directory: `workflows/content-approval/pending-drafts.json`.** It is the single shared file both `content-discovery` and this workflow read and write — see `workflows/content-discovery/references/pending-drafts-schema.md` for the full reasoning on why it is shared, and why it stays at this path even though custodianship moved.

Custodianship sits with content-discovery (daily scheduled resync + cleanup). This workflow runs the same resync + cleanup when invoked on demand, plus editorial-edit execution. Neither workflow publishes.

Format:
```json
[
  {
    "ghost_post_id": "abc123",
    "slack_thread_ts": "1234567890.123456",
    "slack_channel": "C0B160MA3EK",
    "title": "Post title",
    "source_url": "https://...",
    "created_at": "2026-05-04T06:00:00Z",
    "status": "pending",
    "source_type": "url",
    "content_type": "post"
  }
]
```

---

## GATES

None remain. The publish flow this workflow used to gate (GATE 3 approval decision, GATE 4 publishing pre-flight, GATE 5 delivery verification, and the `publish-preflight` guardrail checkpoint) was retired with the approve-keyword flow — this workflow has no irreversible external action. Editorial edits are PATCHes to unpublished drafts and are verified by re-reading the post after the edit.

---

## STATE CHECK — Run Before Any Execution

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `content-approval`; agent: Harper.

## EXECUTION

| # | File | Executed by | Produces |
|---|------|-------------|----------|
| 1 | `steps/step-01-approve.md` (resync + cleanup + editorial edits) | spawned subagent (Harper) | Resynced/cleaned pending-drafts.json + edited Ghost drafts |
| 2 | `steps/step-02-git-finalize.md` | spawned subagent (Rigby, git via `skills/git/SKILL.md`) | Committed tracker state |
| 3 | `steps/step-03-adversarial-verify.md` | spawned subagent (Harper) spawning **Ralph** | `adversarial-verification` guardrail result + verdict |

1. Read and follow `steps/step-01-approve.md`.
2. After completion, run `steps/step-02-git-finalize.md` to commit all changes.
3. Then run `steps/step-03-adversarial-verify.md`, which spawns **Ralph** with `workflows/content-approval-verification/workflow.md` (the tracker-state-vs-Ghost-reality lens). Ralph re-derives every resync/cleanup/edit claim from the live Ghost post state and the Slack thread replies and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/content-approval/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate.
<!-- personal:end -->

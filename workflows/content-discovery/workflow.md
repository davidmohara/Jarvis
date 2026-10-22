---
name: content-discovery
description: Scans #content Slack channel for new URLs and digests, drafts blog posts in David's voice, submits them to Ghost as drafts, and notifies David in Slack for review. Runs daily at 6am. Drafting half of the content pipeline; workflows/content-pipeline orchestrates this workflow and content-approval end to end.
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "personal content drafting and blog publishing workflow — no decisions about individuals' access to opportunity or resources"
---

<!-- personal:start -->
# Content Discovery Workflow

**Goal:** Turn URLs and digests dropped in #content Slack into Ghost draft posts, in David's voice, ready for his approval. Zero manual drafting.

**Agent:** Harper — Storyteller, Communication & Thought Leadership

**Trigger:** Scheduled daily at 6:00 AM (`config/scheduled-tasks.json`, task id `content-discovery`).

**Relationship:** This workflow is the drafting half of the content pipeline, and the custodian of the shared `pending-drafts.json` tracker (its step-01 runs a Ghost-status resync and cleanup on every daily run). Publishing is external — David publishes, schedules, and deletes drafts directly in Ghost. `workflows/content-approval/workflow.md` is an on-demand resync/cleanup/editorial-edit pass over the same tracker. `workflows/content-pipeline/workflow.md` orchestrates both end to end when a full cycle is needed; both read and write the same shared state file.

**Companion workflow:** `workflows/content-approval/workflow.md` resyncs the tracker with live Ghost state and executes surgical editorial edits from thread replies when run on demand. Both workflows read and write the same shared `pending-drafts.json` — see `references/pending-drafts-schema.md` for its location and the reasoning for keeping it shared.
<!-- personal:end -->

---

<!-- personal:start -->
## CHANNEL

| Channel | ID | Purpose |
|---------|-----|---------|
| #content | C0B160MA3EK | Drop URLs here. David replies here with editorial feedback on drafts (handled at step-01 Step 1b). Approve/reject replies need no action — David publishes and deletes directly in Ghost. |

> **Note:** If the channel ID is wrong, David must correct it manually in this file. The channel ID for #content is C0B160MA3EK.

---

## REFERENCES

- Read `references/digest-format.md` before classifying or drafting from a #content message — it holds the digest detection rule, section mapping, missing-section rule, and bot skip rule.
- Read `references/ghost-conventions.md` before any Ghost API call — it holds the author ID, image rules, and the locked tag list (tags must be passed as objects, never bare strings).
- Read `references/slack-integration.md` before any Slack read or write — it holds the Desktop Commander requirements and the read.py/post.py commands.
- Read `references/pending-drafts-schema.md` before writing any pending-drafts.json entry — it holds the shared-file design rule and the entry schema.
- Read `references/hub-registry.md` when selecting tags (hub link check) or running step-01 Step 1c. It holds the hub registry, the tag-to-hub match rules, and the hub page sync protocol.

---

## BLOG VOICE & FORMAT

Read `identity/VOICE.md` for full voice configuration. For blog posts specifically:

- **Length:** 300-700 words. Short. 2-4 minute read.
- **Structure (citation-friendly, approved 2026-10-21):** Open with a one-sentence bottom line (the governing claim) → body under 2-4 H2 subheadings (Story/Observation → Insight) → close with a brief "What to do" takeaway (the Challenge). When the post cites a stat, study, or firm, include at least one outbound link to the primary source.
- **Tone:** Personal, reflective, direct. First person. David is writing to peers, not students.
- **Style:** Conversational. No jargon unless it earns its place. Parenthetical asides are natural. Exclamation marks when energized.
- **Not a summary:** The source URL is a spark, not the article to rewrite. David's reaction, angle, or insight is the post — not a recap of what he read.
- **No em-dashes.** Use commas, periods, or parentheses instead.

---

## DEDUPLICATION

Before drafting, check:
1. `reference/blog-ideas.md` — Published section
2. Ghost published posts — call `mcp__ghost-blog__get_posts` and scan titles
3. `pending-drafts.json` (shared file — see `references/pending-drafts-schema.md`) — normalized URL and, for digests, title match

If the source URL or its core topic already has a published post, skip it and notify: "Skipped [URL] — topic already covered in '[existing post title]'."

---

## HUB PAGES

The blog has undated hub pages that collect clusters of dated posts around a theme. `references/hub-registry.md` is the source of truth: it maps tag combinations (from the locked tag list) to hubs and drives both directions of linking. Drafted posts link out to their hub (checked at GATE 2), and hub pages pick up newly published posts (step-01 Step 1c, which runs with the daily resync). Adding a new hub is a registry entry plus a David-approved Ghost page, never a workflow edit. Hub updates only ever touch `published`/`scheduled` posts, never drafts.

---

## GATES — OVERVIEW

This workflow enforces two deterministic gates, both in `steps/step-01-discover.md`:

1. **GATE 1 — Source Integrity (HARD)** — runs immediately after the Slack channel pull, before any drafting begins. Confirms the read actually succeeded against the right channel with real data.
2. **GATE 2 — Content Schema Validation (HARD)** — runs after drafting, before the Ghost API create-post call. Confirms the drafted post satisfies the digest/post-arc schema, voice rules, and tag-list membership described above.

See step-01-discover.md for full pass/fail criteria, logging format, and escalation instructions for each.

---

## STATE CHECK — Run Before Any Execution

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `content-discovery`; agent: Harper.

## EXECUTION

| # | File | Executed by | Produces |
|---|------|-------------|----------|
| 1 | `steps/step-01-discover.md` (includes GATE 1 and GATE 2) | spawned subagent (Harper) | Ghost draft posts + Slack notifications |
| 2 | `steps/step-02-git-finalize.md` | spawned subagent (Rigby, git via `skills/git/SKILL.md`) | Committed discovery state |
| 3 | `steps/step-03-adversarial-verify.md` | spawned subagent (Harper) spawning **Ralph** | `adversarial-verification` guardrail result + verdict |

1. Read and follow `steps/step-01-discover.md` (includes GATE 1 and GATE 2).
2. After completion, run `steps/step-02-git-finalize.md` to commit all changes.
3. Then run `steps/step-03-adversarial-verify.md`, which spawns **Ralph** with `workflows/content-discovery-verification/workflow.md` (the draft-claims-vs-Slack/digest-source lens). Ralph re-derives every draft and skip claim from the recorded source and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/content-discovery/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate.
<!-- personal:end -->

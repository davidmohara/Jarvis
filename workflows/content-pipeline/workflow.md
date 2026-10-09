---
name: content-pipeline
description: "Active end-to-end content pipeline (discover, approve, publish), used daily by automated systems. The content-discovery and content-approval workflows also run on their own schedules as focused sub-flows."
agent: harper
model: sonnet
---

<!-- personal:start -->
# Content Pipeline Workflow

**Status:** Active — used daily by automated systems (David, 2026-10-09). Previously marked retired 2026-09-02 in favor of content-discovery/content-approval; that marking was wrong: automation still runs this pipeline daily.

## This workflow has been split

This file used to describe "two independent scheduled agents running on different cadences"
(daily discovery, hourly/multi-daily approval) inside a single workflow.md, with no
deterministic gates anywhere. David had Rigby split it into two separate, gated workflow
directories because the two halves run on genuinely different triggers/cadences and enforce
different checks:

- **`workflows/content-discovery/workflow.md`** — the daily-6am half. Carries forward this
  file's CHANNEL, DIGEST FORMAT, SLACK INTEGRATION, GHOST BLOG CONVENTIONS, BLOG VOICE & FORMAT,
  and DEDUPLICATION sections, plus the full logic of the old `steps/step-01-discover.md` (now
  `content-discovery/steps/step-01-discover.md`). Adds two new deterministic gates: **GATE 1 —
  Source Integrity** (validates the Slack pull before drafting) and **GATE 2 — Content Schema
  Validation** (validates the drafted post against the digest/post-arc schema, voice rules, and
  tag list before Ghost creation).
- **`workflows/content-approval/workflow.md`** — the multi-daily approval half. Carries forward
  the full logic of the old `steps/step-02-approve.md` and `steps/step-03-git-finalize.md` (now
  `content-approval/steps/step-01-approve.md` and `content-approval/steps/step-02-git-finalize.md`).
  Adds three new deterministic gates: **GATE 3 — Approval Decision** (approve / reject / request
  revisions), **GATE 4 — Publishing Pre-flight** (tags, image, lexical, slug checks before
  publish), and **GATE 5 — Delivery Verification** (confirms the post is actually live, not just
  that the API call didn't error).

**The shared state file `pending-drafts.json` now lives at
`workflows/content-approval/pending-drafts.json`** — both new workflows read/write it there. The
copy in this directory (below) is stale as of the split; do not write to it going forward.

**If you were routed here:** stop, and instead read and follow
`workflows/content-discovery/workflow.md` (for drafting new content) or
`workflows/content-approval/workflow.md` (for approval/publish) via Harper, depending on which
half of the pipeline you need.

**Supporting files left in this directory** (`state.yaml`, the stale `pending-drafts.json`,
`step-02-status.log`, `ghost_update_v2.py`, `steps/*.md`, `verify/*.py`) are dead weight now
that their logic and current data live in the two new directories. They were intentionally left
in place rather than deleted — see the Rigby build report for this split — pending confirmation
that the new workflows are working correctly in production. Delete them once that's confirmed.

---

## (Historical, for reference only — superseded content below)

**Goal:** Turn URLs dropped in #content Slack into published blog posts on driventodevelop.com — with zero manual drafting. Harper monitors the channel, drafts in David's voice, submits to Ghost with correct image and tags, and publishes when David approves via Slack reply.

**Agent:** Harper — Storyteller, Communication & Thought Leadership

**Architecture:** Two independent scheduled agents running on different cadences.

---

## OVERVIEW

### Agent 1: content-discovery (runs daily at 6am)
Scans #content for new URLs → fetches content → drafts post → submits to Ghost as draft → notifies David in Slack with review instructions.

### Agent 2: content-approval (runs hourly)
Scans #content for approval replies → publishes approved Ghost drafts → handles rejections and regeneration requests.

---

## CHANNEL

| Channel | ID | Purpose |
|---------|-----|---------|
| #content | C0B160MA3EK | Drop URLs here. Replies here to approve/reject drafts. |

> **Note:** If the channel ID is wrong, David must correct it manually in this file. The channel ID for #content is C0B160MA3EK.

---

## DIGEST FORMAT

The Watchtower workflow (and David directly) posts structured content digests to #content. These are the primary input for the digest drafting path.

### What a digest looks like

```
# Post Title

## Hook
2-4 sentences — the opening move

## Story Angle
David's personal vantage point, first-person

## Core Insight
The distilled truth

## Challenge / CTA
The closing ask/challenge

## Sources
- Source name — URL
- Source name — URL
```

Section header variations are valid: `## Challenge / CTA` and `## Challenge/CTA` are both acceptable. Other section names may vary slightly — match by keyword (see detection rule below).

### Detection rule

A message (bot or user) is a **digest** if it contains BOTH:
- `# ` (an H1 header — the post title)
- At least one `## ` (an H2 section header)

### Section mapping

| Digest section | Post arc role |
|---------------|--------------|
| `## Hook` | Post hook (opening) |
| `## Story Angle` / `## Story` | Body — David's personal angle |
| `## Core Insight` / `## Insight` | Insight — the distilled truth |
| `## Challenge / CTA` / `## Challenge/CTA` / `## Challenge` | Closing challenge/CTA |
| `## Sources` | Reference context only — not cited in the post body |

Match sections by keyword presence in the header, not exact string match. "Hook" matches `## Hook`. "Story" or "Angle" matches `## Story Angle`. "Insight" matches `## Core Insight`. "Challenge" or "CTA" matches any challenge/CTA variant.

### Missing sections

If a digest is missing any of the four post-arc sections (Hook, Story, Insight, Challenge), Harper fills them using `identity/CONTENT-VOICE.md`. Sources are always optional.

### Bot message skip rule (updated)

Previously: skip all bot messages. **Updated rule:** Skip bot messages UNLESS they contain `# ` AND `## ` (digest signal). Bot messages with the digest signal are processed on the DIGEST PATH, not skipped.

---

## SLACK INTEGRATION

> **CRITICAL — Desktop Commander MUST be loaded before any Slack operations:**
> - **ALWAYS load Desktop Commander tools at the start of any step that reads/writes Slack.** Use ToolSearch: `"select:mcp__Desktop_Commander__start_process,mcp__Desktop_Commander__read_file,mcp__Desktop_Commander__write_file"` (See err-20260715T182916-FSMOJK for why this matters.)
> - **In a Cowork session:** the sandboxed `mcp__workspace__bash` tool does NOT have general outbound network access (small allowlist only) and WILL fail read.py/post.py with a tunnel/connection error. Do not use it for this step. Use `mcp__Desktop_Commander__start_process` instead — it executes on the actual Mac and has full network access.
> - **In native Jarvis (Claude Code) runtime:** `mcp__Desktop_Commander__start_process` is the only authorized path regardless — this was already the rule, restated here for emphasis.
> - If read.py/post.py fails with a network/connection error, do NOT conclude "no network access" and abort. First confirm which execution tool was used. If it was the Cowork sandbox bash tool, retry the identical command via `mcp__Desktop_Commander__start_process` before reporting any failure. (See err-20260715T134905-DAGK1T.)

**Reading:** Use `systems/slack-bot/read.py` via Desktop Commander (mcp__Desktop_Commander__start_process)

```bash
# Read #content for URLs dropped in last 24 hours
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C0B160MA3EK 24

# Read replies on a specific draft thread
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" thread C0B160MA3EK 1234567890.123456
```

Both commands return JSON: `{"ok": true, "messages": [...]}` or `{"ok": true, "replies": [...]}`.
Each message object includes: `ts`, `user`, `text`, `thread_ts` (if part of a thread).

**Writing/Notifying:** Use `master-slack` skill — `systems/slack-bot/post.py` via Desktop Commander

```bash
# Post to #content
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "<message>"

# Reply in a thread (pass thread_ts as 3rd arg)
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "<message>" 1234567890.123456
```

No Slack MCP connector is used. Both read and write go through the bot token in config/.env via these two scripts.

---

## GHOST BLOG CONVENTIONS

These are locked. Do not deviate.

### Author
- Always: David O'Hara — ID `68a3465b9e3561027e745c51`

### Images
- **Source:** Unsplash. Search for a thematic image matching the post's core concept.
- **URL format:** `https://images.unsplash.com/photo-{id}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={ixid}&ixlib=rb-4.1.0&q=80&w=2000`
- **feature_image:** Unsplash URL at w=2000
- **twitter_image:** Same URL as feature_image
- **og_image:** Leave null (Ghost generates automatically)
- **How to set:** Use `mcp__ghost-blog__upload_image_from_url` to upload the Unsplash image to Ghost's CDN first, then use the returned Ghost URL for both feature_image and twitter_image. If the upload fails, use the Unsplash URL directly — Ghost accepts external URLs for feature_image.
- **Finding Unsplash images:** `mcp__workspace__web_fetch` has a provenance restriction and cannot directly fetch `unsplash.com/s/photos/...` search pages. Use WebSearch first to find a photo URL, then web_fetch the specific photo page to extract the image ID. See step-01-discover.md for the full protocol.
- **Filename convention:** Use slug of post title (e.g., `skin-in-the-game-cost-of-free`)

### Tags — LOCKED LIST (no new tags ever)
Select 1-3 that best match the post content. IDs are required for the Ghost API.

> **Ghost API format — CRITICAL:** Tags must be passed as objects, not bare strings.
> ✅ `[{"id": "637ea17e92f3300211b1b23a"}]` — links existing tag
> ❌ `["637ea17e92f3300211b1b23a"]` — creates a new tag named after the ID string

| Tag Name | ID | Slug |
|----------|-----|------|
| quotes | 637ea17e92f3300211b1b232 | quotes |
| leadership | 637ea17e92f3300211b1b233 | leadership |
| thoughts | 637ea17e92f3300211b1b234 | thoughts |
| purpose | 637ea17e92f3300211b1b235 | purpose |
| life | 637ea17e92f3300211b1b236 | life |
| speaking | 637ea17e92f3300211b1b237 | speaking |
| culture | 637ea17e92f3300211b1b238 | culture |
| improving | 637ea17e92f3300211b1b239 | improving |
| business | 637ea17e92f3300211b1b23a | business |
| family | 637ea17e92f3300211b1b23b | family |
| excel | 637ea17e92f3300211b1b23c | excel |
| scrum | 637ea17e92f3300211b1b23d | scrum |
| agile | 637ea17e92f3300211b1b23e | agile |
| life-hack | 637ea17e92f3300211b1b23f | life-hack |
| apps | 637ea17e92f3300211b1b240 | apps-tag |
| startup | 637ea17e92f3300211b1b241 | startup |
| rant | 637ea17e92f3300211b1b242 | rant |
| math | 637ea17e92f3300211b1b245 | math |
| trust | 637ea17e92f3300211b1b246 | trust |
| systems thinking | 637ea17e92f3300211b1b247 | systems-thinking |
| conscious capitalism | 637ea17e92f3300211b1b248 | conscious-capitalism |
| sleep | 637ea17e92f3300211b1b249 | sleep |
| mental health | 637ea17e92f3300211b1b24a | mental-health |
| reading | 63c81c6d24f5700210f5ff40 | reading |
| productivity | 63e690387be05d0210064e74 | productivity |
| home projects | 63ebffad2b325802108f5dc5 | home-projects |
| growth | 6400ce1602619502100d3829 | growth |
| fun | 64134647b7e99a0210e5ef27 | fun |
| drone | 64134647b7e99a0210e5ef28 | drone |
| money | 641347f9b7e99a0210e5ef3c | money |
| health | 6414657b52d80f02106903de | health |
| wellness | 6414657b52d80f02106903df | wellness |
| functional medicine | 649470141bafd60209f035d9 | functional-medicine |
| thinking | 64c16e007b788102090a5064 | thinking |
| communication | 64c16e007b788102090a5065 | communication |
| Writing | 66354da2f8a84d01391b72e9 | writing |
| AI | 68fbc4d89e3561027e745c91 | ai |
| technology | 68fbc4d89e3561027e745c92 | technology |

### Post Status Flow
1. Agent 1 creates post with `status: draft` — never published on creation
2. Agent 2 updates to `status: published` only after David's explicit approval in Slack

---

## BLOG VOICE & FORMAT

Read `identity/VOICE.md` for full voice configuration. For blog posts specifically:

- **Length:** 300-500 words. Short. 1-3 minute read.
- **Structure:** Hook → Story/Observation → Insight → Challenge or takeaway
- **Tone:** Personal, reflective, direct. First person. David is writing to peers, not students.
- **Style:** Conversational. No jargon unless it earns its place. Parenthetical asides are natural. Exclamation marks when energized.
- **Not a summary:** The source URL is a spark, not the article to rewrite. David's reaction, angle, or insight is the post — not a recap of what he read.
- **No em-dashes.** Use commas, periods, or parentheses instead.

---

## DEDUPLICATION

Before drafting, check:
1. `reference/blog-ideas.md` — Published section
2. Ghost published posts — call `mcp__ghost-blog__get_posts` and scan titles

If the source URL or its core topic already has a published post, skip it and notify: "Skipped [URL] — topic already covered in '[existing post title]'."

---

## STATE TRACKING

Pending drafts are tracked in `workflows/content-pipeline/pending-drafts.json`. This is the source of truth for Agent 2.

Format:
```json
[
  {
    "ghost_post_id": "abc123",
    "slack_thread_ts": "1234567890.123456",
    "slack_channel": "C08UZMA7EGV",
    "title": "Post title",
    "source_url": "https://...",
    "created_at": "2026-05-04T06:00:00Z",
    "status": "pending",
    "source_type": "url"
  }
]
```

**`source_type` field:** String. Values: `"url"` (standard URL path) or `"digest"` (drafted from a Slack digest message). Optional for backward compatibility — existing entries without this field are treated as `"url"`.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run, initialize state.yaml.
4. If `status: aborted`: surface to controller and wait.

## EXECUTION

> **ACTIVE WORKFLOW, in daily automated use.** The focused sub-flows
> `workflows/content-discovery/` and `workflows/content-approval/` also run on their own
> schedules. Each step carries its own deterministic verifier, and the pipeline carries a terminal
> Ralph adversarial verification step (step-04) with the end-to-end accounting lens.
> `steps/step-03-git-finalize.md` is a filled-in execution record, not a step definition, and is
> intentionally left in place.

| # | File | Executed by | Produces |
|---|------|-------------|----------|
| 1 | `steps/step-01-discover.md` | spawned subagent (Harper) | Ghost draft posts + Slack notifications |
| 2 | `steps/step-02-approve.md` | spawned subagent (Harper) | Published/rejected/edited Ghost posts |
| 3 | `steps/step-03-git-finalize.md` (execution record) | spawned subagent (Rigby, git via `skills/git/SKILL.md`) | Committed pipeline state |
| 4 | `steps/step-04-adversarial-verify.md` | spawned subagent (Harper) spawning **Ralph** | `adversarial-verification` guardrail result + verdict |

For Agent 1 (discovery):
1. Read and follow `steps/step-01-discover.md`
2. After completion, run `steps/step-03-git-finalize.md` to commit all changes

For Agent 2 (approval):
1. Read and follow `steps/step-02-approve.md`
2. After completion, run `steps/step-03-git-finalize.md` to commit all changes

3. Then run `steps/step-04-adversarial-verify.md`, which spawns **Ralph** with `workflows/content-pipeline-verification/workflow.md` (the end-to-end accounting lens). Ralph accounts for every item from discovered through approved to published and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint.

**Deterministic step guardrails:** The verifiers in `workflows/content-pipeline/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record.
<!-- personal:end -->

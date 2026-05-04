---
name: content-pipeline
description: Automated content generation pipeline — reads URLs from #content Slack channel, drafts posts in David's voice, submits to Ghost as drafts for review, publishes on approval
agent: harper
model: sonnet
---

<!-- personal:start -->
# Content Pipeline Workflow

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
| #content | C08UZMA7EGV | Drop URLs here. Replies here to approve/reject drafts. |

> **Note:** If the channel ID above is wrong or the channel doesn't exist yet, the agent should search for it:
> Use `slack_search_channels` with query "content" to find the correct ID. Update this file with the correct ID once confirmed.

---

## SLACK INTEGRATION

**Reading:** Use `systems/slack-bot/read.py` via Desktop Commander (mcp__Desktop_Commander__start_process)

```bash
# Read #content for URLs dropped in last 24 hours
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C08UZMA7EGV 24

# Read replies on a specific draft thread
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" thread C08UZMA7EGV 1234567890.123456
```

Both commands return JSON: `{"ok": true, "messages": [...]}` or `{"ok": true, "replies": [...]}`.
Each message object includes: `ts`, `user`, `text`, `thread_ts` (if part of a thread).

**Writing/Notifying:** Use `master-slack` skill — `systems/slack-bot/post.py` via Desktop Commander

```bash
# Post to #content
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C08UZMA7EGV "<message>"

# Reply in a thread (pass thread_ts as 3rd arg)
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C08UZMA7EGV "<message>" 1234567890.123456
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
- **How to set:** Use `mcp__ghost-blog__upload_image_from_url` to upload the Unsplash image to Ghost's CDN first, then use the returned Ghost URL for both feature_image and twitter_image
- **Filename convention:** Use slug of post title (e.g., `skin-in-the-game-cost-of-free`)

### Tags — LOCKED LIST (no new tags ever)
Select 1-3 that best match the post content. IDs are required for the Ghost API.

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
    "status": "pending"
  }
]
```

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run, initialize state.yaml.
4. If `status: aborted`: surface to controller and wait.

## EXECUTION

For Agent 1 (discovery): Read and follow `steps/step-01-discover.md`
For Agent 2 (approval): Read and follow `steps/step-02-approve.md`
<!-- personal:end -->

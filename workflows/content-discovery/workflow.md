---
name: content-discovery
description: Scans #content Slack channel for new URLs and digests, drafts blog posts in David's voice, submits them to Ghost as drafts, and notifies David in Slack for review. Runs daily at 6am. First half of the split content-pipeline (successor to workflows/content-pipeline).
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

**Lineage:** This workflow is half of the former `workflows/content-pipeline/workflow.md`, which described "two independent scheduled agents running on different cadences" inside a single workflow.md with no deterministic gates. It has been split into this workflow (discovery) and `workflows/content-approval/workflow.md` (approval + publish), each with its own gates, because the two run on different triggers/cadences and enforce different checks. `workflows/content-pipeline/workflow.md` is now RETIRED — see that file for the full redirect note.

**Companion workflow:** `workflows/content-approval/workflow.md` scans for approval replies and publishes. It runs independently on its own cadence. Both workflows read and write the same shared `pending-drafts.json` — see STATE TRACKING below for its location and the reasoning for keeping it shared.
<!-- personal:end -->

---

<!-- personal:start -->
## CHANNEL

| Channel | ID | Purpose |
|---------|-----|---------|
| #content | C0B160MA3EK | Drop URLs here. David replies here to approve/reject drafts (handled by content-approval). |

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

Watchtower bot messages sometimes use `*Bold*` section headers instead of `## ` markdown — those are ALSO digests and must never be skipped as noise (see step-01's MESSAGE ROUTER and err-20260727T201106-MOE539).

### Section mapping

| Digest section | Post arc role |
|---------------|--------------|
| `## Hook` | Post hook (opening) |
| `## Story Angle` / `## Story` | Body — David's personal angle |
| `## Core Insight` / `## Insight` | Insight — the distilled truth |
| `## Challenge / CTA` / `## Challenge/CTA` / `## Challenge` | Closing challenge/CTA |
| `## Sources` | Reference context only — not cited in the post body |

Match sections by keyword presence in the header, not exact string match.

### Missing sections

If a digest is missing any of the four post-arc sections (Hook, Story, Insight, Challenge), Harper fills them using `identity/CONTENT-VOICE.md`. Sources are always optional.

**This "four post-arc elements must all appear" rule is formalized as QUALITY GATE 2 (Content Schema Validation) in step-01-discover.md** — it is no longer just inline prose, it is a checked gate before Ghost draft creation.

### Bot message skip rule

Skip bot messages UNLESS they contain `# ` AND `## ` (digest signal) OR the Watchtower bold-header digest signal. Bot messages with either digest signal are processed on the DIGEST PATH, not skipped.

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
```

Returns JSON: `{"ok": true, "messages": [...]}`. Each message object includes: `ts`, `user`, `text`, `thread_ts` (if part of a thread).

**GATE 1 (Source Integrity) validates this response before anything else happens — see step-01-discover.md.**

**Writing/Notifying:** Use `master-slack` skill — `systems/slack-bot/post.py` via Desktop Commander

```bash
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "<message>"
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
- **Finding Unsplash images:** `mcp__workspace__web_fetch` has a provenance restriction and cannot directly fetch `unsplash.com/s/photos/...` search pages. Use WebSearch first to find a photo URL, then web_fetch the specific photo page to extract the image ID. Full protocol in step-01-discover.md Step 6.

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

**GATE 2 (Content Schema Validation) checks the drafted post against tag-list membership, word count, voice rules, and the four-arc-element requirement above before any Ghost API call.**

### Post Status Flow
1. This workflow (content-discovery) creates the post with `status: draft` — never published on creation.
2. `workflows/content-approval/workflow.md` updates it to `status: published` only after David's explicit approval in Slack.

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
3. `pending-drafts.json` (shared file — see STATE TRACKING) — normalized URL and, for digests, title match

If the source URL or its core topic already has a published post, skip it and notify: "Skipped [URL] — topic already covered in '[existing post title]'."

---

## STATE TRACKING

**Pending drafts are tracked in a single shared file: `workflows/content-approval/pending-drafts.json`.**

**Decision:** `pending-drafts.json` stays a single shared file rather than being split or copied per workflow, and it lives under `content-approval/` (not `content-discovery/`), because:
- Discovery appends new entries; approval owns the entry's full lifecycle after that (status transitions, cleanup, editorial edits, deletion). The heavier read/write logic — the 30-day cleanup rules, the "published"/"scheduled" pruning, the Ghost-status resync — all belongs to approval, so the file lives where most of its mutation logic runs.
- A single file avoids needing sync logic between two copies, which would risk exactly the kind of drift and stale-data bugs step-02 (approval)'s "Ghost Status Verification" section already exists to guard against.
- Both workflows already ran against the exact same file under the old single-workflow.md design (on different cadences: daily vs. 4x/day) with no observed race — the split does not change the concurrency profile, it only changes which directory holds the file.

Discovery (this workflow) reads and appends to `workflows/content-approval/pending-drafts.json` directly — do not create a local copy in this directory.

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
    "source_type": "url",
    "content_type": "post"
  }
]
```

**`source_type` field:** String. Values: `"url"` (standard URL path), `"digest"` (drafted from a Slack digest message), or `"manual"` (legacy entries). Optional for backward compatibility — existing entries without this field are treated as `"url"`.

**`content_type` field:** String, `"post"` or `"article"`. Mandatory on every new entry this workflow writes (MANDATORY EXECUTION RULE 8 in step-01-discover.md).

---

## GATES — OVERVIEW

This workflow enforces two deterministic gates, both in `steps/step-01-discover.md`:

1. **GATE 1 — Source Integrity (HARD)** — runs immediately after the Slack channel pull, before any drafting begins. Confirms the read actually succeeded against the right channel with real data.
2. **GATE 2 — Content Schema Validation (HARD)** — runs after drafting, before the Ghost API create-post call. Confirms the drafted post satisfies the digest/post-arc schema, voice rules, and tag-list membership described above.

See step-01-discover.md for full pass/fail criteria, logging format, and escalation instructions for each.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered. Do not re-pull it.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it; if
     `status: not-started`, begin it fresh.
   - Notify the controller: "[Harper]: Resuming content-discovery from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Harper]: content-discovery was previously aborted at
     [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

1. Read and follow `steps/step-01-discover.md` (includes GATE 1 and GATE 2).
2. After completion, run `steps/step-02-git-finalize.md` to commit all changes.
<!-- personal:end -->

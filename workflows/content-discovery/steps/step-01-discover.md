---
status: complete
started-at: "2026-10-17T19:00:00Z"
completed-at: "2026-10-17T19:05:00Z"
outputs:
  messages_scanned: 8
  new_urls: 0
  new_digests: 0
  posts_drafted: 0
  improving_blog_drafts: 0
  pending_threads_checked: 2
  editorial_feedback_found: 0
  editorial_edits_applied: 0
  gate_1_result: "PASS — ok: true, 8 bot messages (48h retry) from C0B160MA3EK. All without digest signal — SKIP."
  gate_2_result: "n/a — no new drafts"
  outcome: "No new content. 2 pending threads checked (Your Business Has a Dashboard, Love With Your Presence). Both threads fully actioned in prior run — latest replies at ts 1792149571 and 1792149573 (~30h ago) outside 24h window and already confirmed handled in editorial_edits. Clean exit."
model: sonnet
---

<!-- personal:start -->
# Step 01: Content Discovery & Draft

## MANDATORY EXECUTION RULES

0. You MUST use `mcp__Desktop_Commander__start_process` for read.py/post.py, never a sandboxed bash/shell tool. See `workflows/content-discovery/references/slack-integration.md` for the full initialization and retry protocol.
1. You MUST read the full workflow.md before executing — it contains voice rules and channel IDs, and it points to `references/ghost-conventions.md` (Ghost conventions, tag IDs), which you MUST also read before any Ghost API call.
2. You MUST check pending-drafts.json (at `workflows/content-approval/pending-drafts.json` — see `workflows/content-discovery/references/pending-drafts-schema.md`) and dedup against existing posts before drafting anything.
3. You MUST NOT create new Ghost tags. Only use tags from the locked list in workflow.md.
4. You MUST set status: draft on Ghost — never published.
5. You MUST upload the image to Ghost CDN before setting it on the post.
6. You MUST write the pending draft entry to pending-drafts.json after successful Ghost creation.
7. You MUST notify David via post.py (Jarvis bot) — not the Slack MCP connector.
8. You MUST set content_type on every pending-drafts.json entry — "post" or "article". Never omit it.
9. You MUST run the tracker resync and cleanup (Step 1a) and scan pending draft threads for editorial feedback (Step 1b) before processing new content. Discovery is the custodian of the shared tracker — publishing is external (David publishes directly in Ghost), so Step 1a's resync is the only thing keeping pending-drafts.json in sync with reality.
10. You MUST NOT proceed past GATE 1 or GATE 2 below if either fails its HARD criteria.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline
**Trigger:** Runs daily at 6am via scheduled task
**Input:** #content Slack channel (last 24 hours)
**Output:** Ghost draft post + Slack notification with review instructions

---

## YOUR TASK

### 1. Read the channel

Use read.py via Desktop Commander to pull #content messages from the last 24 hours:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C0B160MA3EK 24 2>&1
Timeout: 15000
```

> **48H RETRY RULE (err-20260908T223218-VPU9BH):** If the 24h call returns `ok: true` with 0 messages AND the response includes the warning string `"Zero messages returned for 24h window and 48h retry"`, immediately retry with a 48h window:
> ```
> python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C0B160MA3EK 48 2>&1
> ```
> Only accept a 0-message result as a clean no-op when the warning is absent, OR when the 48h retry also returns 0 messages. Never close the run on the 24h zero alone when the warning is present.

---

## QUALITY GATE 1 — Source Integrity (HARD, BLOCKING)

Run immediately after the read.py call above, before parsing or routing any message.

Run the Gate 1 source-integrity checklist in `references/gates.md` (read it now, before parsing or routing any message). An empty `messages` array is a legitimate PASS — no new content, not a failure.

Parse the JSON response — `{"ok": true, "messages": [...]}`. Each message has `ts`, `user`, `text`, `thread_ts`, and optionally `bot_id`.

Skip messages where `thread_ts != ts` — those are thread replies. Editorial feedback on pending drafts is handled at Step 1b; approve/reject replies need no action (publishing is external — David publishes directly in Ghost, and Step 1a's resync picks the new state up).

For all remaining messages, apply the router below to each one before doing anything else.

---

### 1a. Resync and clean pending-drafts.json (tracker custodianship)

Run this on every execution, before scanning threads. This is the step that keeps the shared tracker honest — David publishes, schedules, and deletes drafts directly in Ghost, so the tracker only learns about it here.

**Resync against live Ghost state.** Read `workflows/content-approval/pending-drafts.json`. For each entry with `status: "pending"`, call `mcp__ghost-blog__get_post(id="{ghost_post_id}")`:

- `post.status == "published"`: published externally. Update the entry: set `status: "published"`, add `published_at: {post.published_at}`. It will be removed by the cleanup pass below.
- `post.status == "scheduled"`: update the entry: set `status: "scheduled"`, add `scheduled_at: {post.published_at}` (Ghost stores the scheduled time in `published_at` for scheduled posts).
- `post.status == "draft"`: still a draft (expected). Leave as `status: "pending"`.
- Not found (404): deleted externally. Update the entry: set `status: "deleted_externally"`.

**Cleanup.** After resync, remove from the array:

- All entries with `status: "published"` — they are done.
- All entries with `status: "scheduled"` AND `scheduled_at` in the past (before current UTC time) — Ghost has already published them.
- All entries with `status: "rejected"` AND `created_at` older than 30 days.
- All entries with `status: "deleted_externally"` AND `created_at` older than 30 days.

If any entries changed or were removed, write the updated array back to `workflows/content-approval/pending-drafts.json` immediately. An empty array `[]` is a valid and healthy state.

Record `tracker_resynced` (count of status changes) and `tracker_entries_removed` (count removed) in this step's frontmatter outputs and in `state.yaml` `accumulated-context`.

### 1b. Scan pending draft threads for editorial feedback

After reading the channel, read `workflows/content-approval/pending-drafts.json`. For every entry with `status: pending` and a non-null `slack_thread_ts`, fetch the thread replies:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" thread C0B160MA3EK {slack_thread_ts} 2>&1
Timeout: 15000
```

For each thread, examine the replies from human users (skip bot messages). Apply this router to each human reply:

**APPROVE/REJECT → skip** (keywords: "approve", "approved", "reject", "rejected", "looks good", "publish"). No action needed — David publishes and deletes drafts directly in Ghost, and Step 1a's resync picks the new state up from Ghost on the next run. Do not process here.

**EDITORIAL FEEDBACK → execute the DRAFT EDIT PATH** (any reply that describes a change to make: "change X", "update X", "rewrite X", "fix X", "make it X", "add X", "remove X", "too long", "too short", "wrong tone", etc.)

Only process replies that arrived in the last 24 hours (compare reply `ts` to now). Skip older replies — they were either already handled or are stale.

If a reply has already been acted on, skip it. Track handled replies by adding an `editorial_edits` array to the pending-drafts.json entry (see DRAFT EDIT PATH below).

---

### DRAFT EDIT PATH

Follow `references/draft-edit-path.md` (read it when 1b surfaces editorial feedback on a pending draft thread): the full draft-edit and re-review protocol.

### MESSAGE ROUTER — apply in priority order

Apply the router in `references/message-router.md` (read it before classifying any message) to each remaining message, in its priority order.

### DIGEST PATH

Execute this section for any message (bot or user) that matched the digest signal.

**A. Parse the digest**

Extract the H1 line as the post title. Then extract content under each `##` section. Match sections by keyword — do not require exact header text:

| Keyword match | Maps to |
|--------------|---------|
| "hook" in header | Hook |
| "story" or "angle" in header | Story/Observation |
| "insight" in header | Insight |
| "challenge" or "cta" in header | Challenge/CTA |
| "source" in header | Sources (reference only) |

Strip leading/trailing whitespace from each section's content.

**B. Strip em-dashes**

Before drafting, replace all em-dashes (`—`, Unicode U+2014) in the extracted content with commas or periods, whichever reads more naturally in context. This is mandatory — Watchtower posts contain em-dashes and David's blog voice prohibits them.

**C. Handle Sources (if present)**

If a `## Sources` section exists, extract the URLs listed there. Fetch each URL with `mcp__workspace__web_fetch` for context only. Do not cite these sources in the post body. The source is a spark for context, not content to reference.

**D. Draft the post**

Before writing a single word: read `identity/CONTENT-VOICE.md` in full.

Map the parsed digest sections to the post arc:
- Hook section → post opening hook
- Story/Angle section → body (David's personal angle and observation)
- Insight section → insight paragraph
- Challenge/CTA section → closing challenge

For any section that is missing from the digest, Harper writes it from scratch using CONTENT-VOICE.md as the voice guide. The four post-arc elements (Hook, Story, Insight, Challenge) must all appear in the final post — no exceptions. **GATE 2 below checks this before Ghost creation.**

Apply all standard drafting rules from the URL PATH section:
- 300-500 words. No headers. No bullet points in body. Prose only.
- No em-dashes. Use commas, periods, or parentheses.
- The post must be David's voice and reaction — not a restatement of the digest content.
- End with a direct challenge or question to the reader.

Also draft at this stage: `meta_title`, `meta_description`, `twitter_title`, `twitter_description` (same rules as URL PATH).

**E. Continue with steps 5 onward (tag selection, image, GATE 2, Ghost creation, notify)**

After drafting from a digest, continue at **Step 5 (Select tags)** below. The digest path merges with the URL path at that point and follows the identical process through GATE 2, Ghost creation, pending-drafts.json write, and Slack notification.

In the pending-drafts.json entry, set:
```json
"source_type": "digest"
```

In the Slack notification teaser (Step 9), append `_(drafted from digest)_` on a new line after the teaser sentences.

---

### IMPROVING BLOG PATH

Follow `references/improving-blog-path.md` (read it when the router sends a message down this path): the full Improving-blog drafting protocol.

### 2. Fetch and research each URL

For each new URL:

1. **Fetch the article:** `mcp__workspace__web_fetch(url="{url}")`
2. **If fetch fails or returns minimal content:** Run a web search for the article title or topic to gather context. The model should self-recover — proceed with search-gathered context.
3. **Extract:** Core argument, key insight, memorable quote or stat, the "so what" for David's audience.

### 3. Check deduplication

- Read `reference/blog-ideas.md` — Published section
- Call `mcp__ghost-blog__get_posts(limit=50)` and scan titles/slugs
- **Normalize URLs before dedup:** Strip tracking parameters before comparing. Spotify URLs include `?si=…` tokens; WSJ/NYT/others append `?mod=`, `?ref=`, `?campaign=`, etc. Compare base URLs only (scheme + host + path). Example: `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV?si=xLu7qQ7g…` → `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV`.
- Check `workflows/content-approval/pending-drafts.json` — if the normalized URL is already present in the `source_url` field (any status), skip it with note: "Skipped {url} — already in pipeline (status: {status})."
- **Digest title dedup:** For digest messages, also check `pending-drafts.json` by title. Extract the H1 from the digest and compare (case-insensitive) against all existing `title` fields. If a match exists (any status), skip with note: "Skipped digest '{title}' — already in pipeline (status: {status})." This prevents the 48h fallback from re-processing Watchtower digests that were already drafted in a prior run.
- If the source URL topic is already covered: skip with a note, don't draft.

### 4. Draft the post

**Before writing a single word: read `identity/CONTENT-VOICE.md` in full.** This is the blog-specific voice guide built from David's actual published posts. It is the source of truth for public content. Do not use `identity/VOICE.md` — that file governs Jarvis's internal communication style and is not appropriate for blog writing. Do not rely on memory or a summary of the rules. Read the file. This is mandatory on every run.

After reading CONTENT-VOICE.md, write a blog post in David's voice following the arc defined there:

- **Hook:** 1-2 sentences. A scene, a question, a contradiction. Something that earns the next sentence. Not "I read an article today." Not a rhetorical question that telegraphs the answer.
- **Story/Observation:** David's personal angle. What did this surface for him? A pattern from his consulting work, a real situation he has been in, something it confirmed or challenged. Be specific — real details, real friction.
- **Insight:** The distilled truth. One clean line of reasoning that arrives somewhere. Not a list of takeaways.
- **Challenge/Takeaway:** A direct question or provocation in the final paragraph. This is non-negotiable. It must appear in every post. It asks something of the reader.

**Length:** 300-500 words. No headers in posts under 500 words. Prose only. No bullet points in the body.

> ❌ **NO EM-DASHES. EVER.** Not `—`, not `–`, not `--`. Use commas, periods, or parentheses. No exceptions.

**Do not:** Summarize the article. Do not write "According to [source]..." David's reaction and angle is the post — the source is the spark, not the content.

Also draft at this stage:
- **meta_title:** Post title (same as title, or slight SEO variation — max 70 chars)
- **meta_description:** 1-2 sentence summary of the post's core insight — max 155 chars
- **twitter_title:** Same as meta_title
- **twitter_description:** Same as meta_description

### 5. Select tags

Choose 1-3 tags from the locked list in workflow.md. Match to the post's core themes. No new tags.

> **CRITICAL — Ghost API tag format:** Tags MUST be passed as an array of objects with an explicit `id` key. Passing bare ID strings causes Ghost to create new tags instead of linking existing ones.
>
> ✅ Correct: `tags=[{"id": "637ea17e92f3300211b1b23a"}, {"id": "68fbc4d89e3561027e745c91"}]`
> ❌ Wrong: `tags=["637ea17e92f3300211b1b23a", "68fbc4d89e3561027e745c91"]`
>
> **If the Ghost MCP rejects tag objects (returns an error about tag format):** Omit `tags` from the `create_post` call entirely. Apply tags via the Ghost Admin API PUT in Step 7b instead — the Admin API handles the object format correctly. Do NOT fall back to bare strings — that creates junk tags in the database.

### 6. Source the feature image

Follow `references/image-sourcing.md` (read it in this step): the two-step Unsplash search/fetch protocol, the image selection rules (landscape, thematic, geography-matching), the mandatory pixel-level orientation check, and the Ghost CDN upload call.

## QUALITY GATE 2 — Content Schema Validation (HARD, BLOCKING)

Run after Step 6 (image sourced) and before Step 7 (Ghost draft creation). Run the Gate 2 checklist in `references/gates.md` (read it at this point): it formalizes the digest-format and voice rules into an explicit pass/fail checklist. Applies to both the URL PATH and the DIGEST PATH (per DIGEST PATH Step E, the digest path merges in here).

### 6b. Record the run's draft-quality manifest (Gate 2 evidence)

Gate 2's voice/image/link checks are only as trustworthy as the evidence they leave behind. After Gate 2 passes for every draft (and before this step closes), write the run's draft-quality manifest to:

```
memory/working/content-discovery-drafts-{YYYY-MM-DD}.json
```

Write the manifest using the schema in `references/draft-quality-manifest.md` (read it before writing) — one JSON object, one `posts` entry per drafted post, written even when zero posts were drafted.

### 7. Create Ghost draft

Follow `references/ghost-draft-creation.md` (read it in this step): the confirmed Ghost MCP limitations, the Admin API key read, JWT generation, Lexical JSON construction, and the single POST that creates the draft.

### 8. Write to pending-drafts.json

Read the current `workflows/content-approval/pending-drafts.json`, append the new entry, write it back:

```json
{
  "ghost_post_id": "{id from Ghost response}",
  "slack_thread_ts": null,
  "slack_channel": "C0B160MA3EK",
  "title": "{Post Title}",
  "source_url": "{original url or null for digest}",
  "created_at": "{ISO timestamp}",
  "status": "pending",
  "source_type": "url",
  "content_type": "post"
}
```

> Set `content_type` to `"article"` if the message contained the `article` keyword (detected in the router above). Otherwise use `"post"`. For digest entries, apply the same logic based on the digest message text or title.

Set `source_type` to `"url"` for the standard URL path, or `"digest"` for the digest path. For digest entries, `source_url` may be null or set to the first source URL from the digest's `## Sources` section if one exists.

`slack_thread_ts` starts as null — it gets filled in step 9 after posting.

### 9. Notify David in Slack

Use `master-slack` skill (post.py via Desktop Commander) to post to #content (C0B160MA3EK):

```
*New draft ready for review* ✍️

*"{Post Title}"*
_Source: {source_url}_

{First 2-3 sentences of the draft as a teaser}

*Review draft:* https://driventodevelop.com/ghost/#/editor/post/{ghost_post_id}/

*To review:* Reply to this thread with:
• `approve` — publishes to driventodevelop.com
• `reject` — discards the draft
• Anything else — I'll treat it as feedback and regenerate
```

**Capture the message timestamp:** Run post.py via Desktop Commander. Parse the stdout JSON response.
- If `ok` is true, extract the `ts` field and set `slack_thread_ts` in the pending draft entry.
- If `ok` is false or `ts` is missing, set `slack_thread_ts` to the current Unix timestamp as a fallback (close enough for content-approval to find replies).

Update `workflows/content-approval/pending-drafts.json` — set `slack_thread_ts` to this value for the entry you just created.

### 10. Update reference/blog-ideas.md

Add the new post to the Candidates table in `reference/blog-ideas.md`:

```
| "{Post Title}" | Content pipeline ({date}) | {tags} | Ghost draft — pending approval |
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| GATE 1 fails (read.py fails, script not found, token error, wrong-channel response) | Report failure via post.py to #jarvis: "Content discovery paused — read.py error: {error}". Exit. |
| URL fetch fails + web search returns nothing | Skip URL. Log: "Could not retrieve content for {url} — skipping." |
| GATE 2 fails and cannot be remediated after one retry | Notify David in #content: "Draft for '{title}' failed content schema validation ({failed check}) after one remediation attempt — needs manual review." Do not create the Ghost post. |
| Ghost API fails on post creation | Log error. Notify David in #content: "Draft creation failed for {url} — will retry tomorrow." |
| Image upload fails | Use a fallback Unsplash URL directly (without uploading) — Ghost accepts external URLs for feature_image. Note in Slack message: "(image not uploaded to CDN — using external URL)" |
| pending-drafts.json is malformed | Reset to `[]` and log the error. Do not halt. |

---

## YOUR TASK — Closing (state bookkeeping)

After Step 10 completes (or after an early clean exit with no new content):

1. Write `status: complete`, `completed-at`, and populated `outputs` (at minimum: `messages_scanned`, `new_urls`, `new_digests`, `posts_drafted`, `gate_1_result`, `gate_2_result`) to this file's own frontmatter.
2. Write those same output keys into `state.yaml`'s `accumulated-context`.
3. Set `state.yaml`'s `current-step: step-02`.

## NEXT STEP

After discovery completes:
1. Draft notification is posted to #content
2. Run `steps/step-02-git-finalize.md` to commit pending-drafts.json and state.yaml

`workflows/content-approval/steps/step-01-approve.md` (the same resync + cleanup, plus on-demand editorial edits) can also be run on demand, followed by its own git-finalize step. Discovery's Step 1a is the primary, scheduled custodian of the shared tracker.
<!-- personal:end -->

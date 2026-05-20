---
status: not-started
model: sonnet
---

<!-- personal:start -->
# Step 01: Content Discovery & Draft

## MANDATORY EXECUTION RULES

1. You MUST read the full workflow.md before executing — it contains Ghost conventions, tag IDs, voice rules, and channel IDs.
2. You MUST check pending-drafts.json and dedup against existing posts before drafting anything.
3. You MUST NOT create new Ghost tags. Only use tags from the locked list in workflow.md.
4. You MUST set status: draft on Ghost — never published.
5. You MUST upload the image to Ghost CDN before setting it on the post.
6. You MUST write the pending draft entry to pending-drafts.json after successful Ghost creation.
7. You MUST notify David via post.py (Jarvis bot) — not the Slack MCP connector.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Trigger:** Runs daily at 6am via scheduled task
**Input:** #content Slack channel (last 24 hours)
**Output:** Ghost draft post + Slack notification with review instructions

---

## YOUR TASK

### 1. Read the channel

Use read.py via Desktop Commander to pull #content messages from the last 24 hours:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/systems/slack-bot/read.py" channel C0B160MA3EK 24 2>&1
Timeout: 15000
```

Parse the JSON response — `{"ok": true, "messages": [...]}`. Each message has `ts`, `user`, `text`, `thread_ts`.

Extract all URLs from message text. Skip:
- Messages where `bot_id` is set (bot messages — including Jarvis's own notifications)
- Messages where thread_ts != ts (those are thread replies — approval responses, Agent 2 handles them)
- URLs already in pending-drafts.json (source_url field)
- URLs whose topics already have published Ghost posts

If no new URLs found: post to #content via post.py:
```
"_Content pipeline: no new URLs in the last 24 hours._"
```
Then exit cleanly.

### 2. Fetch and research each URL

For each new URL:

1. **Fetch the article:** `mcp__workspace__web_fetch(url="{url}")`
2. **If fetch fails or returns minimal content:** Run a web search for the article title or topic to gather context. The model should self-recover — don't halt on a blocked URL.
3. **Extract:** Core argument, key insight, memorable quote or stat, the "so what" for David's audience.

### 3. Check deduplication

- Read `reference/blog-ideas.md` — Published section
- Call `mcp__ghost-blog__get_posts(limit=50)` and scan titles/slugs
- Check `pending-drafts.json` — if the URL is already present in the `source_url` field (any status), skip it with note: "Skipped {url} — already in pipeline (status: {status})."
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

### 6. Source the feature image

Identify the single most important high-level keyword from the post (e.g., "leadership", "resilience", "cost", "writing" — conceptual, not literal). Search Unsplash:

> **IMPORTANT:** `mcp__workspace__web_fetch` has a provenance restriction — it only fetches URLs that appeared in a prior user message or web_fetch result. Direct fetches to `unsplash.com/s/photos/...` will fail. Always use the two-step process below.

1. **Run a WebSearch** for: `unsplash {keyword} landscape photo site:unsplash.com/photos`
2. From the search results, pick a free (non-Unsplash+) photo URL — look for results where the title says "Free ... Image on Unsplash". Avoid results that mention "Unsplash+" or "premium".
3. **Fetch the photo page** with `mcp__workspace__web_fetch` using the exact URL returned by the search — this unlocks it for the provenance check.
4. From the fetched page, extract the photo ID from the `og:image` or `twitter:image` meta tag. The ID appears as `photo-{PHOTO_ID}` in the URL.
5. Construct the Unsplash CDN URL:
```
https://images.unsplash.com/photo-{PHOTO_ID}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={IXID}&ixlib=rb-4.1.0&q=80&w=2000
```
Use the ixid from the meta tag URL if available; omit the ixid parameter if not — it's optional.

**Image selection rules:**
- Must be landscape-oriented (wider than tall)
- Avoid portraits of people as the primary subject
- Must be free (no Unsplash+ license required)

Upload to Ghost CDN:
```
mcp__ghost-blog__upload_image_from_url(
  url="{unsplash_url}",
  filename="{post-slug}",
  purpose="image"
)
```

Use the returned Ghost CDN URL for both `feature_image` and `twitter_image`.

### 7. Create Ghost draft

> **CONFIRMED MCP LIMITATIONS (verified 2026-05-19):** The Ghost MCP silently drops `html`, `feature_image`, and `twitter_image` on both `create_post` and `update_post`. Tags passed as bare ID strings create junk tags. **Do not rely on the MCP for content or metadata.** Use a two-step approach: create the shell via MCP, then populate everything via the Ghost Admin API directly.

**Step 7a — Create shell via MCP:**
```
mcp__ghost-blog__create_post(
  title="{Post Title}",
  status="draft",
  authors=["68a3465b9e3561027e745c51"]
)
```
Capture the returned `id`.

**Step 7b — Populate content, image, and tags via Ghost Admin API:**

Use `mcp__Control_your_Mac__osascript` to run a Python script that:
1. Generates a Ghost JWT from the Admin API key (found in `~/Library/Application Support/Claude/claude_desktop_config.json`, server `ghost-blog`, env `GHOST_ADMIN_API_KEY` — format `{key_id}:{hex_secret}`)
2. GETs the post to retrieve `updated_at` (required for optimistic locking)
3. PUTs the full update with `lexical` (build as Lexical JSON — array of paragraph nodes), `feature_image`, `twitter_image`, and `tags` as `[{"id": "{tag_id}"}]` objects

**Step 7c — Verify via `mcp__ghost-blog__get_post`:**
- `lexical` has correct paragraph count (non-empty)
- `feature_image` is set
- `tags` show real names (trust, leadership, etc.) not ID strings
- `excerpt` is populated (Ghost auto-generates from content)

**Do not send the Slack notification until all three checks pass.** If any check fails, report the specific failure accurately — do not claim partial success.

Capture the returned `id` — this is the Ghost post ID needed for approval.

### 8. Write to pending-drafts.json

Read the current `workflows/content-pipeline/pending-drafts.json`, append the new entry, write it back:

```json
{
  "ghost_post_id": "{id from Ghost response}",
  "slack_thread_ts": null,
  "slack_channel": "C0B160MA3EK",
  "title": "{Post Title}",
  "source_url": "{original url}",
  "created_at": "{ISO timestamp}",
  "status": "pending"
}
```

`slack_thread_ts` starts as null — it gets filled in step 9 after posting.

### 9. Notify David in Slack

Use `master-slack` skill (post.py via Desktop Commander) to post to #content (C0B160MA3EK):

```
*New draft ready for review* ✍️

*"{Post Title}"*
_Source: {source_url}_

{First 2-3 sentences of the draft as a teaser}

*To review:* Reply to this thread with:
• `approve` — publishes to driventodevelop.com
• `reject` — discards the draft
• Anything else — I'll treat it as feedback and regenerate
```

**Capture the message timestamp:** Run post.py via Desktop Commander. Parse the stdout JSON response.
- If `ok` is true, extract the `ts` field and set `slack_thread_ts` in the pending draft entry.
- If `ok` is false or `ts` is missing, set `slack_thread_ts` to the current Unix timestamp as a fallback (close enough for step-02 to find replies).

Update `pending-drafts.json` — set `slack_thread_ts` to this value for the entry you just created.

### 10. Update reference/blog-ideas.md

Add the new post to the Candidates table in `reference/blog-ideas.md`:

```
| "{Post Title}" | Content pipeline ({date}) | {tags} | Ghost draft — pending approval |
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content discovery halted — read.py error: {error}". Exit. |
| URL fetch fails + web search returns nothing | Skip URL. Log: "Could not retrieve content for {url} — skipping." |
| Ghost API fails on post creation | Log error. Notify David in #content: "Draft creation failed for {url} — will retry tomorrow." |
| Image upload fails | Use a fallback Unsplash URL directly (without uploading) — Ghost accepts external URLs for feature_image. Note in Slack message: "(image not uploaded to CDN — using external URL)" |
| pending-drafts.json is malformed | Reset to `[]` and log the error. Do not halt. |

---

## NEXT STEP

This step is self-contained. Agent 2 (step-02-approve.md) runs independently on its own schedule.
<!-- personal:end -->

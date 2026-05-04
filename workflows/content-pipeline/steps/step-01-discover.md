---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

Use Slack MCP to read #content channel (ID: C08UZMA7EGV) for messages in the last 24 hours:

```
slack_read_channel(channel_id="C08UZMA7EGV", hours_ago=24)
```

Extract all URLs from messages. Skip:
- Messages that are replies (thread_ts != ts — those are approval responses, Agent 2 handles them)
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
- If the source URL topic is already covered: skip with a note, don't draft.

### 4. Draft the post

Write a blog post in David's voice using the structure and rules from workflow.md:

- **Hook:** 1-2 sentences. Something that makes the reader stop. Not "I read an article today."
- **Story/Observation:** David's personal angle on what he read. What did it surface for him? A memory, a pattern he's seen, something it confirmed or challenged.
- **Insight:** The distilled truth. What's the one thing the reader should carry away?
- **Challenge/Takeaway:** A direct ask or provocation. What should the reader do, think, or notice?

**Length:** 300-500 words. No headers. Prose only. No bullet points in the post body.

**Voice reminders from identity/VOICE.md:**
- No em-dashes
- Parenthetical asides are natural: "(and I've seen this kill teams)"
- Write like a human exec, not a system
- First person throughout
- Exclamation marks when energized — but earned, not reflexive

**Do not:** Summarize the article. Do not write "According to [source]..." David's reaction and insight is the post.

### 5. Select tags

Choose 1-3 tags from the locked list in workflow.md. Match to the post's core themes. No new tags.

Return the tag IDs (not names) — the Ghost API requires IDs.

### 6. Source the feature image

Search Unsplash for a thematic image matching the post's core concept (not the source article's topic literally — the *feeling* or *theme* of David's post).

Construct the Unsplash URL:
```
https://images.unsplash.com/photo-{PHOTO_ID}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={IXID}&ixlib=rb-4.1.0&q=80&w=2000
```

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

```
mcp__ghost-blog__create_post(
  title="{Post Title}",
  html="{post body as HTML — wrap paragraphs in <p> tags}",
  status="draft",
  authors=["68a3465b9e3561027e745c51"],
  tags=["{tag_id_1}", "{tag_id_2}"],
  feature_image="{ghost_cdn_url}",
  twitter_image="{ghost_cdn_url}"
)
```

Capture the returned `id` — this is the Ghost post ID needed for approval.

### 8. Write to pending-drafts.json

Read the current `workflows/content-pipeline/pending-drafts.json`, append the new entry, write it back:

```json
{
  "ghost_post_id": "{id from Ghost response}",
  "slack_thread_ts": null,
  "slack_channel": "C08UZMA7EGV",
  "title": "{Post Title}",
  "source_url": "{original url}",
  "created_at": "{ISO timestamp}",
  "status": "pending"
}
```

`slack_thread_ts` starts as null — it gets filled in step 9 after posting.

### 9. Notify David in Slack

Use `master-slack` skill (post.py via Desktop Commander) to post to #content (C08UZMA7EGV):

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

Capture the `ts` (timestamp) of this Slack message. Update `pending-drafts.json` — set `slack_thread_ts` to this value for the entry you just created.

### 10. Update reference/blog-ideas.md

Add the new post to the Candidates table in `reference/blog-ideas.md`:

```
| "{Post Title}" | Content pipeline ({date}) | {tags} | Ghost draft — pending approval |
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Slack MCP unavailable | Report "Slack MCP not connected — content-discovery halted" via post.py to #jarvis. Exit. |
| URL fetch fails + web search returns nothing | Skip URL. Log: "Could not retrieve content for {url} — skipping." |
| Ghost API fails on post creation | Log error. Notify David in #content: "Draft creation failed for {url} — will retry tomorrow." |
| Image upload fails | Use a fallback Unsplash URL directly (without uploading) — Ghost accepts external URLs for feature_image. Note in Slack message: "(image not uploaded to CDN — using external URL)" |
| pending-drafts.json is malformed | Reset to `[]` and log the error. Do not halt. |

---

## NEXT STEP

This step is self-contained. Agent 2 (step-02-approve.md) runs independently on its own schedule.
<!-- personal:end -->

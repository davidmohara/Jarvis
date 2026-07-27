---
status: not-started
model: sonnet
---

<!-- personal:start -->
# Step 01: Content Discovery & Draft

## MANDATORY EXECUTION RULES

0. You MUST use `mcp__Desktop_Commander__start_process` for read.py/post.py, never a sandboxed bash/shell tool (e.g. Cowork's `mcp__workspace__bash`). The sandbox has no general outbound network access and will fail Slack calls with a connection/tunnel error. If that happens, do not conclude Slack or the network is down, retry via Desktop Commander first. See err-20260715T134905-DAGK1T.
1. You MUST read the full workflow.md before executing — it contains Ghost conventions, tag IDs, voice rules, and channel IDs.
2. You MUST check pending-drafts.json and dedup against existing posts before drafting anything.
3. You MUST NOT create new Ghost tags. Only use tags from the locked list in workflow.md.
4. You MUST set status: draft on Ghost — never published.
5. You MUST upload the image to Ghost CDN before setting it on the post.
6. You MUST write the pending draft entry to pending-drafts.json after successful Ghost creation.
7. You MUST notify David via post.py (Jarvis bot) — not the Slack MCP connector.
8. You MUST set content_type on every pending-drafts.json entry — "post" or "article". Never omit it.

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

Parse the JSON response — `{"ok": true, "messages": [...]}`. Each message has `ts`, `user`, `text`, `thread_ts`, and optionally `bot_id`.

Skip messages where `thread_ts != ts` — those are thread replies handled by Agent 2.

For all remaining messages, apply the router below to each one before doing anything else.

---

### MESSAGE ROUTER — apply in priority order

Evaluate each message against the following rules in sequence. Stop at the first match.

```
1. Bot message WITHOUT digest signal AND WITHOUT Watchtower section keywords  →  SKIP (operational noise)
2. Bot message WITH digest signal (# + ##) OR Watchtower section keywords (*Hook*, *Story Angle*/*Core Insight*, *Challenge*/*CTA*)  →  DIGEST PATH
   NOTE: Watchtower drafts ALWAYS route to DIGEST PATH. They use *bold* headers, not ## markdown. Never skip them. (err-20260727T201106-MOE539)
3. User message WITH routing keywords    →  OBSIDIAN ROUTE
   (keywords: "save to obsidian", "save as a note", "for a talk", "reference",
    "do not draft a post", "don't draft a post")
4. User message WITH (# + ##) headers   →  DIGEST PATH
4.5. User message WITH "article" keyword (case-insensitive) AND URL  →  URL PATH (content_type: "article")
5. User message WITH URL, no routing keywords  →  URL PATH
6. User message with deck/slides/presentation/PowerPoint  →  MANUAL FLAG
7. User message referencing an existing post with editorial instructions (no URL, no digest signal)  →  EDITORIAL EDIT PATH
   (keywords: "change the image", "update the image", "add the link", "add a link", "change image",
    "swap image", "replace image", "fix the image", "update the post", "edit the post")
```

**Detection rule for digest signal:** A message matches ANY of these patterns:
- Has `# ` AND `## ` — an H1 title line and at least one H2 section header (standard markdown digest)
- Is a bot message containing all four Watchtower section keywords in bold: `*Hook*` (or `*Hook*\n`), `*Story Angle*` or `*Core Insight*`, and `*Challenge*` or `*CTA*` — these are Watchtower drafts and are ALWAYS processed, never skipped

> **CRITICAL — err-20260727T201106-MOE539:** Watchtower bot messages use `*Bold*` section headers, not `## ` markdown. The old detection rule missed them entirely and skipped them as "operational noise." This is wrong. Watchtower drafts are NEVER noise. If a bot message contains Hook + Story/Insight + Challenge in any header format, it is a digest and must be drafted.

**For SKIP:** Do nothing. Move to next message.

**For OBSIDIAN ROUTE:** Execute `skills/obsidian-source-note/SKILL.md` inline. Read the full skill before acting. Use Spotify extraction (Step 3d in podcast-transcript-extract) for Spotify URLs. After saving the note, notify David in #content:
```
"_Saved to Obsidian: [{Note Title}] — {vault_path}_"
```

**For MANUAL FLAG:** Post to #content:
```
"_@david — [{source title}] needs manual handling: {brief reason}. I can't process this automatically._"
```

**Prior-post linking (DIGEST PATH and URL PATH):** After drafting, scan the post body for references to prior posts, recurring themes, or named figures/numbers that appeared in a recent post. Check `pending-drafts.json` titles and Ghost published post slugs for thematic matches. If a clear callback exists, insert an inline hyperlink on the most natural anchor text before submitting to Ghost. Do not wait for David to ask. This is mandatory when the digest itself signals a "step two" or "prior week" relationship. (err-20260727T201700-2H2GW4)

**For EDITORIAL EDIT PATH:** Execute the edit inline. Do not defer to Jarvis Master. Do not flag to #content. Handle it directly:

1. **Identify the target post.** Match the post name from the message to a Ghost draft or published post. Use `mcp__ghost-blog__get_posts` or search by slug if needed.
2. **Image swap:** If the instruction is to change the image, find a new Unsplash image following the Step 6 protocol (WebSearch → fetch photo page → extract ID → construct CDN URL). Upload via `mcp__ghost-blog__upload_image_from_url` if available; fall back to direct Unsplash URL if upload fails. Update the post via Ghost Admin API (same JWT pattern as Step 7) — PATCH to `/ghost/api/admin/posts/{id}/` with `{"posts": [{"feature_image": "{new_url}", "twitter_image": "{new_url}", "updated_at": "{current_updated_at}"}]}`.
3. **Link insertion:** If the instruction is to add a hyperlink to specific text, fetch the current post's `lexical` from Ghost, locate the target text node, wrap it in a link node, and PATCH the updated lexical back via Ghost Admin API.
4. **Confirm silently** by verifying the post via `mcp__ghost-blog__get_post` after the update. No Slack notification needed unless the edit fails.
5. **If the edit also includes a workflow update instruction** ("encode this in the workflow", "update the workflow"): apply the change to this file (step-01-discover.md) or workflow.md as appropriate, then confirm with a brief #content reply: `"_Workflow updated: {what changed}._"`

**For URL PATH and DIGEST PATH:** Continue to the relevant section below.

Do NOT treat non-blog messages as failed pipeline items. Route them correctly or flag them.

If no messages route to URL PATH or DIGEST PATH after evaluating all messages: post to #content via post.py:
```
"_Content pipeline: no new URLs or digests in the last 24 hours._"
```
Then exit cleanly.

---

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

For any section that is missing from the digest, Harper writes it from scratch using CONTENT-VOICE.md as the voice guide. The four post-arc elements (Hook, Story, Insight, Challenge) must all appear in the final post — no exceptions.

Apply all standard drafting rules from the URL PATH section:
- 300-500 words. No headers. No bullet points in body. Prose only.
- No em-dashes. Use commas, periods, or parentheses.
- The post must be David's voice and reaction — not a restatement of the digest content.
- End with a direct challenge or question to the reader.

Also draft at this stage: `meta_title`, `meta_description`, `twitter_title`, `twitter_description` (same rules as URL PATH).

**E. Continue with steps 5 onward (tag selection, image, Ghost creation, notify)**

After drafting from a digest, continue at **Step 5 (Select tags)** below. The digest path merges with the URL path at that point and follows the identical process through Ghost creation, pending-drafts.json write, and Slack notification.

In the pending-drafts.json entry, set:
```json
"source_type": "digest"
```

In the Slack notification teaser (Step 9), append `_(drafted from digest)_` on a new line after the teaser sentences.

---

### 2. Fetch and research each URL

For each new URL:

1. **Fetch the article:** `mcp__workspace__web_fetch(url="{url}")`
2. **If fetch fails or returns minimal content:** Run a web search for the article title or topic to gather context. The model should self-recover — proceed with search-gathered context.
3. **Extract:** Core argument, key insight, memorable quote or stat, the "so what" for David's audience.

### 3. Check deduplication

- Read `reference/blog-ideas.md` — Published section
- Call `mcp__ghost-blog__get_posts(limit=50)` and scan titles/slugs
- **Normalize URLs before dedup:** Strip tracking parameters before comparing. Spotify URLs include `?si=…` tokens; WSJ/NYT/others append `?mod=`, `?ref=`, `?campaign=`, etc. Compare base URLs only (scheme + host + path). Example: `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV?si=xLu7qQ7g…` → `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV`.
- Check `pending-drafts.json` — if the normalized URL is already present in the `source_url` field (any status), skip it with note: "Skipped {url} — already in pipeline (status: {status})."
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
- Must be landscape-oriented (wider than tall). No portrait-oriented images. Ever.
- Must be thematically aligned with the post's core concept — not just generically "professional." A post about auditing should show paperwork, spreadsheets, or financial review. A post about purpose/fulfillment should show open space, horizon, or journey imagery. A post about AI governance should show systems/infrastructure. Match the metaphor, not just the industry.
- Avoid portraits of people as the primary subject
- Must be free (no Unsplash+ license required)
- If the first candidate is premium (Unsplash+) or portrait, discard it and try the next search result — do not settle

> **MANDATORY — verify orientation from the actual pixels, never from the title, alt text, or search category.** Unsplash titles like "a long road with a mountain in the background" or category tags do not reliably indicate orientation — the same photo can be a portrait crop. (See err-20260715T195437-E6MUV6: a "long road / mountain" photo was used and turned out to be 2000x3000, portrait, because the title was trusted instead of the image.)
>
> Before accepting any candidate, fetch it and check real width vs. height via Desktop Commander:
> ```python
> import requests
> from io import BytesIO
> from PIL import Image
> r = requests.get(candidate_url, timeout=20)
> w, h = Image.open(BytesIO(r.content)).size
> assert w > h, f"portrait ({w}x{h}) — discard and try next candidate"
> ```
> If `w <= h`, discard the candidate and move to the next search result. Do not construct the final CDN URL or use the image in Ghost until this check passes.

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

> **CONFIRMED MCP LIMITATIONS (verified 2026-05-19):** The Ghost MCP silently drops `feature_image`, `twitter_image`, and `lexical` content on both `create_post` and `update_post`. Tags passed as bare ID strings create junk tags. **Do not use the Ghost MCP for post creation.** Use a single Admin API POST instead.

**Step 7 — Create post via Ghost Admin API (single call, replaces the old 7a/7b two-step):**

Use `mcp__Control_your_Mac__osascript` to run a Python script that:

1. **Get Admin API key:** Read `~/Library/Application Support/Claude/claude_desktop_config.json`. Find the server named `ghost-blog`. Read `GHOST_ADMIN_API_KEY` from its env block. The format is `{key_id}:{hex_secret}`.

2. **Generate JWT:**
   - Header: `{"alg": "HS256", "kid": "{key_id}", "typ": "JWT"}`
   - Payload: `{"exp": now + 300, "iat": now, "aud": "/admin/"}`
   - Sign using `hex_secret` decoded from hex to bytes (not base64)
   - Use PyJWT: `jwt.encode(payload, bytes.fromhex(hex_secret), algorithm="HS256", headers={"kid": key_id})`

3. **Build Lexical JSON** from the drafted post body. Structure: `{"root": {"children": [{paragraph nodes}], "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1}}`. Each paragraph: `{"children": [{"detail": 0, "format": 0, "mode": "normal", "style": "", "text": "{paragraph text}", "type": "text", "version": 1}], "direction": "ltr", "format": "", "indent": 0, "type": "paragraph", "version": 1}`.

4. **POST to Ghost Admin API:**
   ```
   POST https://driventodevelop.com/ghost/api/admin/posts/
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {
     "posts": [{
       "title": "{Post Title}",
       "status": "draft",
       "authors": [{"id": "68a3465b9e3561027e745c51"}],
       "feature_image": "{ghost_cdn_url}",
       "twitter_image": "{ghost_cdn_url}",
       "tags": [{"id": "{tag_id}"}, ...],
       "lexical": "{lexical_json_string}",
       "meta_title": "{meta_title}",
       "meta_description": "{meta_description}",
       "twitter_title": "{twitter_title}",
       "twitter_description": "{twitter_description}"
     }]
   }
   ```

5. **Capture returned post ID** from the response (`posts[0].id`).

**Step 7 verify — `mcp__ghost-blog__get_post`:**
- `lexical` is non-empty (has paragraph nodes)
- `feature_image` is set
- `tags` show real tag names (e.g., "leadership", "trust") not bare ID strings
- `excerpt` is populated (Ghost auto-generates from content)

**Do not send the Slack notification until ALL verification checks pass.** Report specific failures accurately — do not claim partial success:
- `lexical` empty or null: the POST failed to write content. Check the API response for errors and retry.
- Tags show ID strings: tag format was wrong. Retry with correct `{"id": "..."}` object format.
- `feature_image` null: the image upload failed. Retry Step 6 before proceeding.

Only a clean `get_post` response with content, image, and real tag names unlocks the Slack notification in Step 9.

Capture the returned `id` — this is the Ghost post ID needed for approval.

### 8. Write to pending-drafts.json

Read the current `workflows/content-pipeline/pending-drafts.json`, append the new entry, write it back:

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
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content discovery paused — read.py error: {error}". Exit. |
| URL fetch fails + web search returns nothing | Skip URL. Log: "Could not retrieve content for {url} — skipping." |
| Ghost API fails on post creation | Log error. Notify David in #content: "Draft creation failed for {url} — will retry tomorrow." |
| Image upload fails | Use a fallback Unsplash URL directly (without uploading) — Ghost accepts external URLs for feature_image. Note in Slack message: "(image not uploaded to CDN — using external URL)" |
| pending-drafts.json is malformed | Reset to `[]` and log the error. Do not halt. |

---

## NEXT STEP

After discovery completes:
1. Draft notification is posted to #content
2. Run `steps/step-03-git-finalize.md` to commit pending-drafts.json and state.yaml

Agent 2 (step-02-approve.md) runs independently on its own schedule, also followed by step-03.
<!-- personal:end -->

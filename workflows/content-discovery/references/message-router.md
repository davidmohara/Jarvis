<!-- system:start -->
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
4.6. User message WITH Improving blog keywords AND URL  →  IMPROVING BLOG PATH
   (keywords: "improving thoughts", "improving blog", "improving's blog", "improving thought leadership",
    "not one for my blog", "not my blog")
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

**For IMPROVING BLOG PATH:** Draft an Improving thought-leadership post from the URL and save it locally. Do NOT post to Ghost. Do NOT add to pending-drafts.json. Execute the IMPROVING BLOG PATH section below.

**Prior-post linking (DIGEST PATH and URL PATH):** After drafting, scan the post body for references to prior posts, recurring themes, or named figures/numbers that appeared in a recent post. Check `pending-drafts.json` titles and Ghost published post slugs for thematic matches. If a clear callback exists, insert an inline hyperlink on the most natural anchor text before submitting to Ghost. Do not wait for David to ask. This is mandatory when the digest itself signals a "step two" or "prior week" relationship. (err-20260727T201700-2H2GW4)

> **CRITICAL — err-20260820T191921-BLD5R9:** Never strip or drop links. If a referenced post is published, resolve it to a real URL using the Ghost post list (url field, not tag URLs) and build a proper lexical link node. Only skip linking if the referenced post is still in draft status. Dropping a link and leaving plain text is always wrong. Use the `url` field from `get_posts` results — not the slug — as the canonical URL.

> **CRITICAL — err-20260915T154324-VTPMUJ:** Internal links are a required output, not optional. If the post references or clearly relates to a published post, the link MUST be inserted as a lexical link node — not deferred to a later step. After building the lexical body in Step 7, scan for any named prior posts. For each match, resolve its URL via `mcp__ghost-blog__get_posts` and insert a lexical link node wrapping the anchor text. Use this node structure:
> ```json
> {
>   "type": "link",
>   "url": "{resolved_url}",
>   "rel": null,
>   "target": null,
>   "title": null,
>   "children": [{"detail": 0, "format": 0, "mode": "normal", "style": "", "text": "{anchor text}", "type": "text", "version": 1}],
>   "direction": "ltr",
>   "format": "",
>   "indent": 0,
>   "version": 1
> }
> ```
> The parent paragraph node's `children` array contains this link node in place of the text node that would have held the anchor text. Build this into the lexical before the Step 7 POST call — do not POST first and patch later. Gate 2 checks for this (see `has_internal_link_if_required`). Only omit if the referenced post is still in draft status (not published).

**For EDITORIAL EDIT PATH:** Execute the edit inline. Do not defer to Jarvis Master. Do not flag to #content. Handle it directly:

1. **Identify the target post.** Match the post name from the message to a Ghost draft or published post. Use `mcp__ghost-blog__get_posts` or search by slug if needed.
2. **Image swap:** If the instruction is to change the image, find a new Unsplash image following the Step 6 protocol (WebSearch → fetch photo page → extract ID → construct CDN URL). Upload via `mcp__ghost-blog__upload_image_from_url` if available; fall back to direct Unsplash URL if upload fails. Update the post via Ghost Admin API (same JWT pattern as Step 7) — PATCH to `/ghost/api/admin/posts/{id}/` with `{"posts": [{"feature_image": "{new_url}", "twitter_image": "{new_url}", "updated_at": "{current_updated_at}"}]}`.
3. **Link insertion:** If the instruction is to add a hyperlink to specific text, fetch the current post's `lexical` from Ghost, locate the target text node, wrap it in a link node, and PATCH the updated lexical back via Ghost Admin API.
4. **Confirm silently** by verifying the post via `mcp__ghost-blog__get_post` after the update. No Slack notification needed unless the edit fails.
5. **If the edit also includes a workflow update instruction** ("encode this in the workflow", "update the workflow"): apply the change to this file (step-01-discover.md) or workflow.md as appropriate, then confirm with a brief #content reply: `"_Workflow updated: {what changed}._"`

**For URL PATH and DIGEST PATH:** Continue to the relevant section below.

Do NOT treat non-blog messages as failed pipeline items. Route them correctly or flag them.

If no messages route to URL PATH or DIGEST PATH after evaluating all messages: exit cleanly. Do NOT post anything to #content.

---
<!-- system:end -->

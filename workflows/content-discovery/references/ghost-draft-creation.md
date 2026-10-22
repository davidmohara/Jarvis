<!-- system:start -->
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

3. **Build Lexical JSON** from the drafted post body. Structure: `{"root": {"children": [{nodes}], "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1}}`. Each paragraph: `{"children": [{"detail": 0, "format": 0, "mode": "normal", "style": "", "text": "{paragraph text}", "type": "text", "version": 1}], "direction": "ltr", "format": "", "indent": 0, "type": "paragraph", "version": 1}`. Each H2 subheading: `{"children": [{"detail": 0, "format": 0, "mode": "normal", "style": "", "text": "{subheading text}", "type": "text", "version": 1}], "direction": "ltr", "format": "", "indent": 0, "type": "heading", "tag": "h2", "version": 1}`. The draft's 2-4 H2 subheadings MUST survive into Lexical as `heading` nodes with `tag: "h2"`. Do not flatten them into paragraphs or bold text.

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

   **`updated_at` is not needed on creation.** A POST creates the post; Ghost issues the first `updated_at` itself. The required-`updated_at` rule below applies only to PUTs.

5. **Capture returned post ID** from the response (`posts[0].id`).

**Step 7 verify — `mcp__ghost-blog__get_post`:**
- `lexical` is non-empty (has paragraph nodes, and `heading` nodes with `tag: "h2"` for each subheading)
- `feature_image` is set
- `tags` show real tag names (e.g., "leadership", "trust") not bare ID strings
- `excerpt` is populated (Ghost auto-generates from content)
- `meta_title` is non-empty and ≤ 70 chars
- `meta_description` is non-empty and ≤ 155 chars

**Do not send the Slack notification until ALL verification checks pass.** Report specific failures accurately — do not claim partial success:
- `lexical` empty or null: the POST failed to write content. Check the API response for errors and retry.
- Tags show ID strings: tag format was wrong. Retry with correct `{"id": "..."}` object format.
- `feature_image` null: the image upload failed. Retry Step 6 before proceeding.
- `meta_title` or `meta_description` empty, null, or over the limit: the POST dropped or mangled the metas. Re-apply them via a Ghost Admin API PUT (`update_post` path) and re-verify before proceeding. A missing meta blocks the Slack notification like any other verify failure.

**`updated_at` is REQUIRED on every PUT (verified 2026-10-21).** This Ghost version rejects a PUT to `/ghost/api/admin/posts/{id}` without it (422, `must have required property 'updated_at'`), and it rejects a client-generated timestamp too (optimistic lock: "Someone else is editing this post"). The value must be the post's **current server-issued `updated_at`**. So: GET the post immediately before the PUT, read `updated_at` from that response, and send that exact string in the PUT body. Do not cache it from an earlier read and do not construct it client-side. The same rule applies to the `update_post` MCP path and to the image-only PATCH in draft-edit-path.md.

Only a clean `get_post` response with content, image, real tag names, and both meta fields populated unlocks the Slack notification in Step 9.

Capture the returned `id` — this is the Ghost post ID needed for approval.
<!-- system:end -->

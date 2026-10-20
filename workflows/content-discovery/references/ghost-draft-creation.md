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
<!-- system:end -->

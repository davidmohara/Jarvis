<!-- system:start -->
# Editorial Edit Protocols (content-approval step-01, Editorial Edit Path)

Used when a thread reply is classified as a surgical editorial edit. Execute directly.

#### Link Insertion

1. Fetch the Ghost Admin API key from `~/Library/Application Support/Claude/claude_desktop_config.json` → server `ghost-blog` → `GHOST_ADMIN_API_KEY` (`{key_id}:{hex_secret}`).

2. Generate JWT (same as content-discovery's Step 7):
   - Header: `{"alg": "HS256", "kid": "{key_id}", "typ": "JWT"}`
   - Payload: `{"exp": now + 300, "iat": now, "aud": "/admin/"}`
   - Sign with `bytes.fromhex(hex_secret)` via PyJWT.

3. Fetch the current post lexical via Ghost Admin API:
   ```
   GET https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}/?formats=lexical
   Authorization: Ghost {jwt}
   ```
   Capture `posts[0].lexical` (JSON string) and `posts[0].updated_at`.

4. Parse the lexical JSON. Locate the target text node (the word/phrase David identified). Wrap it in a link node:
   ```json
   {
     "type": "link",
     "url": "{target_url}",
     "children": [{"type": "text", "text": "{link text}", "format": 0, ...}]
   }
   ```
   If David said to search for the link (e.g., "find a link for 'agentic arbitrage'"), run a WebSearch first. If no authoritative source is found, skip the link and note that in the Slack reply.

5. PATCH the updated lexical back:
   ```
   PATCH https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}/
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {"posts": [{"lexical": "{updated_lexical_string}", "updated_at": "{updated_at}"}]}
   ```

6. Verify with `mcp__ghost-blog__get_post` — confirm the link appears in the content.

#### Image Swap

1. Find a new Unsplash image following content-discovery's step-01 Step 6 protocol (WebSearch → fetch photo page → verify landscape orientation via PIL → upload to Ghost CDN).

2. PATCH the post:
   ```
   PATCH https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}/
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {"posts": [{"feature_image": "{new_ghost_cdn_url}", "twitter_image": "{new_ghost_cdn_url}", "updated_at": "{updated_at}"}]}
   ```

#### After any editorial edit

Update pending-drafts.json — append to the entry's `editorial_edits` array with `reply_ts`, `instruction`, `applied_at`, and `summary`. Leave `status` as `"pending"` (publishing is external — David publishes directly in Ghost when he is ready).

Reply in the Slack thread via post.py:
```
[UPDATED] "{Post Title}" — {brief description of what changed}.
```

---
<!-- system:end -->

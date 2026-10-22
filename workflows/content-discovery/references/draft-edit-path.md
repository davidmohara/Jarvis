<!-- system:start -->
### DRAFT EDIT PATH

Execute this section when a pending draft thread contains editorial feedback.

**A. Fetch the current post from Ghost and verify draft status**

Use `mcp__ghost-blog__get_post(post_id="{ghost_post_id}")` to retrieve the post. Extract the `status`, `lexical` content, and `updated_at` timestamp.

If `status` is not `"draft"` (i.e., the post is published or scheduled), do NOT apply any edits. Reply in the thread:

```
"_Skipped — '{Post Title}' is already published. Edit it directly in Ghost._"
```

Then move on to the next pending draft. Only proceed with the edit if `status == "draft"`.

**B. Read the editorial instruction**

Parse what the reply is asking for. Categories:

| Instruction type | Action |
|-----------------|--------|
| Rewrite a specific section | Rewrite that section in David's voice (CONTENT-VOICE.md) |
| Change tone, length, or focus | Apply the change across the affected paragraphs |
| Add or remove specific content | Insert or delete the relevant text |
| Image swap | Follow the Step 6 image protocol, then update `feature_image` and `twitter_image` |
| Other structural change | Apply using best judgment; note what changed in the thread reply |

**C. Apply the edit**

Before writing: read `identity/CONTENT-VOICE.md` if the edit touches post body content.

Rebuild the affected lexical nodes. For full rewrites, rebuild the entire lexical body. For targeted edits, locate and replace only the affected paragraph nodes.

Use the Ghost Admin API PUT (same JWT pattern as Step 7) to update the post. Use PUT with no trailing slash — PATCH returns 404:

`updated_at` is **required** on every PUT and must be the post's current **server-issued** value, taken verbatim from the `get_post` response in section A. It is not a client timestamp: generating one fails the optimistic lock ("Someone else is editing this post"), and omitting it fails with 422 `must have required property 'updated_at'`. If any meaningful time has passed since section A (image work, a slow rebuild), re-run `get_post` immediately before the PUT and use the fresh `updated_at` from that response.

```
PUT https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}
Authorization: Ghost {jwt}
Content-Type: application/json

{
  "posts": [{
    "lexical": "{updated_lexical_json_string}",
    "updated_at": "{current_updated_at}"
  }]
}
```

In that body, `current_updated_at` means the exact string returned as `updated_at` by the section A `get_post` call (re-fetched immediately before the PUT if stale). It is never a timestamp you generated.

For image-only updates, PATCH `feature_image` and `twitter_image` (and `updated_at`) without touching `lexical`. The same server-issued `updated_at` rule applies.

**D. Verify**

Call `mcp__ghost-blog__get_post` to confirm the edit landed. Check that `lexical` reflects the change and `updated_at` advanced.

**E. Reply in the thread**

Post a confirmation reply to the same Slack thread via post.py:

```
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "_Done — {brief description of what changed}. Draft updated._" {slack_thread_ts} 2>&1
```

**F. Update pending-drafts.json**

Add or append to the `editorial_edits` array on the entry:

```json
"editorial_edits": [
  {
    "reply_ts": "{ts of the feedback reply}",
    "instruction": "{brief summary of what was requested}",
    "applied_at": "{ISO timestamp}",
    "summary": "{brief description of what changed}"
  }
]
```

This prevents the same reply from being re-processed on the next run.

---
<!-- system:end -->

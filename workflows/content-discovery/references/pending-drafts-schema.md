<!-- personal:start -->
# STATE TRACKING

**Pending drafts are tracked in a single shared file: `workflows/content-approval/pending-drafts.json`.**

**Design rule:** `pending-drafts.json` is a single shared file, owned by `content-approval/` because most of its mutation logic (status transitions, 30-day cleanup, Ghost-status resync) runs there. Discovery (content-discovery) reads and appends to `workflows/content-approval/pending-drafts.json` directly — do not create a local copy in the content-discovery directory.

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

**`content_type` field:** String, `"post"` or `"article"`. Mandatory on every new entry content-discovery writes (MANDATORY EXECUTION RULE 8 in step-01-discover.md).
<!-- personal:end -->

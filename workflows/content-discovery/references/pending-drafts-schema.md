<!-- personal:start -->
# STATE TRACKING

**Pending drafts are tracked in a single shared file: `workflows/content-approval/pending-drafts.json`.**

**Design rule:** `pending-drafts.json` is a single shared file, kept at `workflows/content-approval/pending-drafts.json` (its historical home — do not move it; verify scripts and pipeline steps reference this path). Custodianship sits with `content-discovery`: its step-01 runs the Ghost-status resync and cleanup (Step 1a) on every scheduled daily run, which is what keeps the tracker in sync with Ghost now that publishing is external (David publishes, schedules, and deletes drafts directly in Ghost). `content-approval` runs the same resync and cleanup when invoked on demand. Discovery reads and appends to the file directly — do not create a local copy in either workflow directory.

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

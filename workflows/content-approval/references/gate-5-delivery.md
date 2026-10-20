<!-- system:start -->
## QUALITY GATE 5 — Delivery Verification (HARD, BLOCKING, now folded into Step 3 above)

This gate's checks are performed by `delivery-router`'s `ghost` backend as part of the Step 3
call above, not as a separate manual re-fetch — kept here as documentation of exactly what
"verified" means for this workflow, since that's still worth stating explicitly even though
the mechanics moved into the skill:

| Check | Expected | On failure |
|-------|----------|------------|
| Re-fetch via `mcp__ghost-blog__get_post(post_id="{ghost_post_id}")` | Call succeeds | **STOP.** If the re-fetch itself fails, treat as unverified — do not tell David it published. Notify with "publish call succeeded but verification fetch failed — check manually." |
| `post.status == "published"` | Confirmed on the re-fetched object, not assumed from the update_post response | **STOP.** If still `"draft"` or `"scheduled"`, the publish did not actually take. Do not send the `[PUBLISHED]` Slack notification. Retry per the concurrent-edit protocol above, or escalate. |
| `post.url` is present and resolves to `driventodevelop.com` | Non-null, correct host | **STOP.** A missing or wrong-host URL means something is off in the Ghost response — do not report a URL you haven't confirmed. |
| `post.published_at` is set | Non-null timestamp | **STOP.** Missing timestamp is a signal the publish is incomplete — do not treat this as done. |

Log the result:
```
[Gate 5] Re-fetch: succeeded
[Gate 5] post.status: published (confirmed)
[Gate 5] post.url: {url}
[Gate 5] PASS — publication verified. Proceeding to notify David.
```

**Only after `delivery_status[0].success == true`** does the `[PUBLISHED]` Slack notification (Step 4 below) get sent. If it's `false`, do not claim success anywhere — follow FAILURE MODES instead.

---

**Step 4: Update pending-drafts.json**

Set `status: "published"` if GATE 5 confirmed the publish, or `status: "approved_pending_publish"` if retries are exhausted or GATE 5 failed.

---

**Step 5: Notify David via Slack**

Post to #content (reply in the same thread as the original draft notification):
```
[PUBLISHED]

"{Post Title}" is live on driventodevelop.com
{post url — from the GATE 5 re-fetch, not the raw update_post response}

Obsidian vault updated: {vault_folder}/{slug}.md — renamed, status set to "Posted"
```

If Obsidian update had warnings, include them in the notification.

---

**Step 6: Update reference docs**

Update `reference/blog-ideas.md` — move the entry from Candidates to Published section.
<!-- system:end -->

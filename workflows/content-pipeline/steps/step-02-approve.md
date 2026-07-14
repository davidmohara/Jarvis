---
status: complete
started-at: 2026-07-13T15:03:00Z
completed-at: 2026-07-13T15:04:00Z
outputs:
  drafts_checked: 2
  actions_taken: 0
  published: 0
  rejected: 0
  regenerated: 0
  outcome: "SUCCESS: All 2 pending drafts checked. Draft 1 (Fulfillment) has no thread activity. Draft 2 (Urgency Trap) shows David requested full post view, bot posted complete draft. No approval/rejection signal yet. All remain pending."
  pending_drafts: 2
model: haiku
---

<!-- personal:start -->
# Step 02: Content Approval & Publish

## MANDATORY EXECUTION RULES

1. You MUST read pending-drafts.json first — only process posts that are tracked there.
2. You MUST read the reply content carefully before acting — do not publish on ambiguous signals.
3. You MUST only publish posts with `status: pending` — never re-process already published or rejected entries.
4. You MUST update pending-drafts.json after every action (publish, reject, regenerate, or cleanup).
5. You MUST NOT create new Ghost tags during regeneration.
6. Approval signal is ONLY valid from David's Slack user ID (U0ANHV5UXEW). Ignore replies from others.
7. You MUST remove `status: "published"` entries from pending-drafts.json on every run — they are done and take up space.
8. You MUST remove `status: "scheduled"` entries from pending-drafts.json once their `scheduled_at` date has passed.
9. **NO EMOJI in Slack messages.** Use text labels like `[PUBLISHED]`, `[REJECTED]`, `[REGENERATED]`, `[ERROR]` instead. Emoji corrupt in shell-to-Slack transmission and render as garbage characters.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Trigger:** Runs hourly via scheduled task
**Input:** pending-drafts.json + Slack thread replies on draft notifications
**Output:** Published Ghost posts, updated pending-drafts.json, Slack confirmations

---

## YOUR TASK

### 0. Fast-exit gate (runs before anything else)

Read `workflows/content-pipeline/pending-drafts.json`.

- If the array is **empty** (`[]`): exit immediately. Do not read Slack, do not call Ghost, do not run cleanup. Nothing to process.
- If all entries have `slack_thread_ts == null`: exit immediately. There are no threads to check for approval replies. Do not call Slack.

Only proceed to Step 1 if there is at least one entry with a non-null `slack_thread_ts`.

---

### 1. Load and clean pending-drafts.json

Read `workflows/content-pipeline/pending-drafts.json`.

**Before anything else, run cleanup:**

- Remove all entries where `status: "published"` — they are done.
- Remove all entries where `status: "scheduled"` AND `scheduled_at` is in the past (before current UTC time) — Ghost has already published them.
- Remove all entries where `status: "rejected"` AND `created_at` is older than 30 days.

If any entries were removed, write the updated array back to pending-drafts.json immediately.

Now filter the remaining entries for `status: "pending"`.

If none: exit cleanly — nothing to process.

### 2. Check each pending draft for a reply

For each pending draft:
- If `slack_thread_ts` is null, skip that draft entry — do not attempt thread reads.
- If `slack_thread_ts` is set, read the thread via read.py:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" thread {slack_channel} {slack_thread_ts}
Timeout: 15000
```

Parse the JSON response — `{"ok": true, "replies": [...]}`. Each reply has `ts`, `user`, `text`.

Look for replies from David (user ID: U0ANHV5UXEW) that arrived after the original bot message.

Ignore: bot replies, replies from other users, reactions (emoji only — those are not approval signals).

If no reply from David: leave as pending, move to next draft.

### 3. Classify the reply

| Signal | Classification | Action |
|--------|---------------|--------|
| `approve`, `approved`, `yes`, `publish`, `go`, `ship it`, `looks good`, `post it` | **Approved** | Publish to Ghost |
| `reject`, `rejected`, `no`, `delete`, `discard`, `trash`, `kill it`, `nope` | **Rejected** | Delete Ghost draft |
| Anything else (feedback, edits, notes, questions) | **Feedback** | Regenerate draft |

### 4a. If Approved — Publish

```
mcp__ghost-blog__update_post(
  post_id="{ghost_post_id}",
  status="published"
)
```

**Retry on concurrent edit error:**

If Ghost returns "Someone else is editing this post" (concurrent edit):
1. Wait 2 seconds
2. Retry the update_post call once
3. If still fails: wait 5 seconds, attempt a third time
4. If all three attempts fail: notify David with the error and keep status as "approved" (not "pending" — approval was confirmed, awaiting Ghost to clear the concurrent edit)

Retry aggressively on concurrent edits — this is a known Ghost behavior when multiple sessions access the post.

Update pending-drafts.json — set `status: "published"` if successful, or `status: "approved_pending_publish"` if retries are needed.

**Obsidian Note Update (runs before Slack notification):**

> **Note for step-01 (content-discovery):** When Agent 1 creates a pending-drafts.json entry, it should set a `content_type` field on that entry — either `"post"` or `"article"`. Harper uses this field here to route to the correct vault folder. If `content_type` is absent, Harper defaults to `"post"`.

1. **Determine the vault folder** from the `content_type` field on the pending-drafts.json entry:
   - If `content_type == "article"`: vault folder is `Mind/Articles/`
   - If `content_type == "post"`, is absent, or is null: vault folder is `Mind/Posts/`

2. **Determine the filename** using the following priority:
   - If the pending-drafts.json entry has an `obsidian_slug` field that is non-null and non-empty: use it exactly as the filename. Example: `obsidian_slug: "_dallas-just-topped-dc.md"` → filename is `_dallas-just-topped-dc.md`.
   - If `obsidian_slug` is absent or null: derive the filename from the `title` field — lowercase, hyphens for spaces, strip punctuation, prepend `_`, append `.md`. Example: title "Why Governance Doesn't Scale" → `_why-governance-doesnt-scale.md`.

   Note: `obsidian_slug` should be set by Agent 1 when the draft note is created. If absent, slug is derived from title.

3. **Find the note** using `mcp__obsidian-local__get_vault_file` with the path `{vault_folder}/{filename}` (e.g., `Mind/Posts/_dallas-just-topped-dc.md`). This is the ONLY location — do not try any other paths. If the file is not found at the expected path, this is a hard failure — surface it to David immediately.

4. **If the note is NOT found:** This is a hard failure — do NOT skip silently. Prepend the following warning to the Slack notification (not as a postscript):
   ```
   ⚠️ *Obsidian note not found* — expected `{vault_folder}/_{title}.md`. Post is live but vault is out of sync. Update manually.
   ```
   Then send the Slack notification with this warning prepended, and continue.

5. **If found:** proceed with the following:

   a. **Rename the file** — strip the leading `_` from the filename, keeping it in the same vault folder.
      Example (post): `Mind/Posts/_AI and the Future of Work.md` → `Mind/Posts/AI and the Future of Work.md`
      Example (article): `Mind/Articles/_AI and the Future of Work.md` → `Mind/Articles/AI and the Future of Work.md`

      Preferred: use `mcp__obsidian-local__patch_vault_file` to rename if the tool supports it.
      Fallback: use `mcp__Desktop_Commander__move_file` with the full vault path to rename the file.

   b. **Update frontmatter** — add or update these two fields in the note's YAML frontmatter:
      - `status: Published`
      - `published_url: {url from Ghost response}`

      Use `mcp__obsidian-local__patch_vault_file` to write the frontmatter changes to the renamed file.

6. **If the rename or frontmatter update fails:** This is a hard failure — do NOT skip silently. Prepend the following warning to the Slack notification (not as a postscript):
   ```
   ⚠️ *Obsidian update failed* — {specific error}. Post is live but vault is out of sync. Update manually.
   ```
   Then send the Slack notification with this warning prepended, and continue.

Notify David via post.py to #content:
```
[PUBLISHED] *Published!*

*"{Post Title}"* is live on driventodevelop.com
{post url from Ghost response}
```

Update `reference/blog-ideas.md` — move the entry from Candidates to Published section.

### 4b. If Rejected — Delete

```
mcp__ghost-blog__delete_post(post_id="{ghost_post_id}")
```

Update pending-drafts.json — set `status: "rejected"`.

Notify via post.py to #content (reply in same thread):
```
[REJECTED] Draft discarded — "{Post Title}"
```

### 4c. If Feedback — Regenerate

Read David's reply as editorial direction. Common patterns:
- "Make it shorter" → cut to 250-300 words
- "Lead with the personal story" → restructure opening
- "Too abstract" → add a concrete example or anecdote
- "Wrong angle — focus on X" → rewrite from that angle

Re-draft the post applying the feedback. Keep the same tags and image unless the feedback implies a different topic.

Delete the old Ghost draft:
```
mcp__ghost-blog__delete_post(post_id="{ghost_post_id}")
```

Create a new Ghost draft with the revised content (same process as step-01, steps 7-9).

Update pending-drafts.json — replace the old entry with the new one (new ghost_post_id, new slack_thread_ts, status: "pending").

Post the new draft notification to #content as a reply in the original thread:
```
[REGENERATED] Draft revised

*"{Post Title}"* (revised)

{2-3 sentence teaser of new version}

Same commands: reply `approve` to publish, `reject` to discard, or give more feedback.
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content approval paused — read.py error: {error}". Exit. |
| Ghost publish fails with "Someone else is editing this post" | This is a known concurrent edit behavior in Ghost. Retry 3 times with 2s and 5s delays between attempts. If all fail: set status to "approved_pending_publish", notify David with instructions to check Ghost dashboard, and prepare for retry on next run. |
| Ghost update/delete fails (other errors) | Retry once. If still fails, notify David in #content: "Failed to {publish/delete} '{title}' — Ghost API error: {error}. Please check manually at driventodevelop.com/ghost." |
| pending-drafts.json malformed | Reset to `[]`, log error, notify #jarvis: "pending-drafts.json was corrupted and reset. Active drafts in Ghost may need manual review." |
| Reply is ambiguous and doesn't fit any category | Treat as feedback. Reply in thread: "Got your reply — treating it as feedback. Here's what I'll change: [interpretation]. Reply `approve` to publish the revision or give me more direction." |
| Post already published (status mismatch) | Log and skip. Do not attempt to republish. |

---

## CLEANUP

Cleanup now runs at the top of every execution (Step 1), not periodically. Rules:
- `status: "published"` — remove immediately on any run.
- `status: "scheduled"` with `scheduled_at` in the past — remove immediately (Ghost has published it).
- `status: "rejected"` older than 30 days — remove.

Keep the file lean. An empty array `[]` is a valid and healthy state.

---

## NOTE ON SLACK INTEGRATION

`systems/slack-bot/read.py` handles all READ operations (channel history, thread replies) via the Slack Web API using the bot token.
`systems/slack-bot/post.py` handles all WRITE operations (posting messages, thread replies) via the same bot token.
Both scripts are invoked via Desktop Commander (mcp__Desktop_Commander__start_process). No Slack MCP connector is used.

**IMPORTANT: Bash quoting for newlines**
When posting messages via post.py from bash/Desktop Commander, use `$'...'` syntax to enable escape sequence interpretation:
- ✅ `python3 post.py C0B160MA3EK $'Line 1\nLine 2\nLine 3'` — produces actual newlines
- ❌ `python3 post.py C0B160MA3EK "Line 1\nLine 2"` — produces literal backslash-n characters

post.py will also process `\n` strings and convert them to newlines, but the shell quoting is the primary mechanism.

---

## NOTE ON EVAL RECORDS

**Harper does NOT write eval records.** The eval harness is owned by Rigby. Harper's job is to execute the content pipeline correctly and report outcomes. Rigby observes those outcomes and writes eval records.

If this workflow run is being executed as part of an observed/instrumented session (i.e., a Rigby eval run is active), Harper surfaces the following outcome data for Rigby to record:
- Run timestamp (started/completed)
- Number of drafts checked
- Number of actions taken (published/rejected/regenerated)
- Any tool failures encountered
- Ghost post IDs of published posts

Harper does NOT write to `systems/eval-harness/runs/` or `systems/eval-harness/skill-runs/`. Any eval record write from Harper is a routing error — log it as such.
<!-- personal:end -->
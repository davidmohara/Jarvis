---
status: complete
started-at: 2026-07-24T16:00:00Z
completed-at: 2026-07-24T16:02:30Z
outputs:
  threads_checked: 8
  new_approvals: 0
  new_rejections: 0
  new_slack_messages: 0
  actions_taken: 0
  published: 0
  pending_approvals: 6
  regenerating_stalled: 2
  outcome: "BLOCKAGE PERSISTS: No new Slack messages in past hour. All 8 threads unchanged. 6 posts pending approval (4 W29, 1 Corrections, 1 Safe Bet). 2 posts stalled (Governance, SaaS Stack). No new commands from David. System awaiting override or Harper regeneration fix."
model: haiku
---

<!-- personal:start -->
# Step 02: Content Approval & Publish

## MANDATORY EXECUTION RULES

1. You MUST read pending-drafts.json first — only process posts that are tracked there.
2. You MUST read the reply content carefully before acting — do not publish on ambiguous signals.
3. You MUST only publish posts with `status: pending` — never re-process already published or rejected entries.
4. You MUST update pending-drafts.json after every action (publish, reject, regenerate, or editorial edit).
5. You MUST NOT create new Ghost tags during regeneration.
6. Approval signal is ONLY valid from David's Slack user ID (U0ANHV5UXEW). Ignore replies from others.
7. You MUST remove `status: "published"` entries from pending-drafts.json on every run — they are done and take up space.
8. You MUST remove `status: "scheduled"` entries from pending-drafts.json once their `scheduled_at` date has passed.
9. **NO EMOJI in Slack messages.** Use text labels like `[PUBLISHED]`, `[REJECTED]`, `[REGENERATED]`, `[UPDATED]`, `[ERROR]` instead. Emoji corrupt in shell-to-Slack transmission and render as garbage characters.
10. **NEVER route editorial instructions to regeneration.** Link insertions, image swaps, and other surgical edits must be executed directly via Ghost Admin API. Regeneration is for substantive content rewrites only. (See err-20260726T164307-HSUVNE.)

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Trigger:** Runs hourly via scheduled task
**Input:** pending-drafts.json + Slack thread replies on draft notifications
**Output:** Published Ghost posts, updated pending-drafts.json, Slack confirmations

---

## CRITICAL: DESKTOP COMMANDER INITIALIZATION

**BEFORE running any step, load Desktop Commander tools via ToolSearch.** This is required for all Slack read/write operations in Cowork mode.

```
ToolSearch("select:mcp__Desktop_Commander__start_process,mcp__Desktop_Commander__read_file,mcp__Desktop_Commander__write_file")
```

**RETRY PROTOCOL:** If ToolSearch returns "No matching deferred tools found":
1. Wait 2 seconds
2. Retry ToolSearch once more
3. If still unavailable: log error (err-YYYYMMDDTHHMMSS-XXXXXX) and abort with status message to #jarvis: "Content approval halted — Desktop Commander unavailable. Check tool initialization."

**DO NOT use bash for Slack operations.** The sandbox lacks network access and macOS tools. Only Desktop Commander has full host network access. See err-20260715T200539-J9SK5Z for previous initialization failure.

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

Apply these checks **in order**. Stop at the first match.

**3a. Approval signals** — publish immediately:

| Signal | Examples |
|--------|---------|
| Approve | `approve`, `approved`, `yes`, `publish`, `go`, `ship it`, `looks good`, `post it` |
| → Action | **Publish** (Step 4a) |

**3b. Rejection signals** — delete immediately:

| Signal | Examples |
|--------|---------|
| Reject | `reject`, `rejected`, `no`, `delete`, `discard`, `trash`, `kill it`, `nope` |
| → Action | **Delete** (Step 4b) |

**3c. Editorial edit signals** — execute directly, do NOT regenerate:

Detect by keyword presence (case-insensitive) in David's reply text:

| Keywords | Edit type |
|----------|----------|
| `put the link`, `add the link`, `add a link`, `insert the link`, `include the link`, `link to`, `inline link`, `hyperlink` | Link insertion |
| `change the image`, `update the image`, `swap image`, `replace image`, `fix the image`, `new image`, `different image` | Image swap |
| `update the post`, `edit the post`, `fix the post`, `change the title`, `update the title` | General post edit |

If ANY of these keywords appear in the reply → **Editorial Edit Path** (Step 4d). Never send these to regeneration.

**3d. Feedback / content rewrite** — everything else:

If none of 3a/3b/3c matched → **Regenerate** (Step 4c). This is for substantive content changes: tone, angle, structure, length, missing context.

---

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

Update pending-drafts.json — set `status: "published"` if successful, or `status: "approved_pending_publish"` if retries are needed.

**Obsidian Note Update (runs before Slack notification):**

> **Note for step-01 (content-discovery):** When Agent 1 creates a pending-drafts.json entry, it should set a `content_type` field on that entry — either `"post"` or `"article"`. Harper uses this field here to route to the correct vault folder. If `content_type` is absent, Harper defaults to `"post"`.

1. **Determine the vault folder** from the `content_type` field on the pending-drafts.json entry:
   - If `content_type == "article"`: vault folder is `Mind/Articles/`
   - If `content_type == "post"`, is absent, or is null: vault folder is `Mind/Posts/`

2. **Determine the filename** using the following priority:
   - If the pending-drafts.json entry has an `obsidian_slug` field that is non-null and non-empty: use it exactly as the filename.
   - If `obsidian_slug` is absent or null: derive the filename from the `title` field — lowercase, hyphens for spaces, strip punctuation, prepend `_`, append `.md`.

3. **Find the note** using `mcp__obsidian-local__get_vault_file` with the path `{vault_folder}/{filename}`. If not found, surface a hard failure to David.

4. **If the note is NOT found:** Do NOT skip silently. Prepend this warning to the Slack notification:
   ```
   [WARNING] Obsidian note not found — expected {vault_folder}/_{title}.md. Post is live but vault is out of sync. Update manually.
   ```

5. **If found:**
   a. Rename the file — strip the leading `_` from the filename, keeping it in the same vault folder.
   b. Update frontmatter — add `status: Published` and `published_url: {url from Ghost response}`.

6. **If rename or frontmatter update fails:** Prepend the warning to the Slack notification and continue.

Notify David via post.py to #content:
```
[PUBLISHED]

"{Post Title}" is live on driventodevelop.com
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

**Only use this path for substantive content rewrites** — tone, angle, structure, length, missing context. If the reply contains any editorial keywords from Step 3c, go to Step 4d instead.

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

"{Post Title}" (revised)

{2-3 sentence teaser of new version}

Same commands: reply `approve` to publish, `reject` to discard, or give more feedback.
```

### 4d. Editorial Edit Path — Execute Directly

**Use this path when Step 3c matched.** Execute the edit directly against Ghost Admin API. Do NOT delete the draft. Do NOT regenerate.

**Read `identity/CONTENT-VOICE.md` before writing any new text.** If the edit requires writing prose (e.g., adding context around a link), it must match David's voice.

#### Link Insertion

1. Fetch the Ghost Admin API key from `~/Library/Application Support/Claude/claude_desktop_config.json` → server `ghost-blog` → `GHOST_ADMIN_API_KEY` (`{key_id}:{hex_secret}`).

2. Generate JWT (same as step-01 Step 7):
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

1. Find a new Unsplash image following step-01 Step 6 protocol (WebSearch → fetch photo page → verify landscape orientation via PIL → upload to Ghost CDN).

2. PATCH the post:
   ```
   PATCH https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}/
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {"posts": [{"feature_image": "{new_ghost_cdn_url}", "twitter_image": "{new_ghost_cdn_url}", "updated_at": "{updated_at}"}]}
   ```

#### After any editorial edit

Update pending-drafts.json — add a `notes` field summarizing the change and timestamp. Leave `status` as `"pending"` (the draft still needs approval).

Reply in the Slack thread via post.py:
```
[UPDATED] "{Post Title}" — {brief description of what changed}.

Reply `approve` to publish, `reject` to discard, or give more feedback.
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content approval paused — read.py error: {error}". Exit. |
| Ghost publish fails with "Someone else is editing this post" | Retry 3 times with 2s and 5s delays. If all fail: set status to "approved_pending_publish", notify David, prepare for retry on next run. |
| Ghost update/delete fails (other errors) | Retry once. If still fails, notify David in #content: "Failed to {action} '{title}' — Ghost API error: {error}. Please check manually at driventodevelop.com/ghost." |
| Link search returns no authoritative source | Skip the link. Reply in thread: "[UPDATED] Searched for a link to '{phrase}' — no authoritative source found. Skipped. Reply `approve` to publish as-is or give a specific URL to use." |
| Editorial edit PATCH fails | Log error. Notify in thread: "[ERROR] Could not apply edit to '{title}' — {error}. Please make the change manually in Ghost." |
| pending-drafts.json malformed | Reset to `[]`, log error, notify #jarvis: "pending-drafts.json was corrupted and reset. Active drafts in Ghost may need manual review." |
| Reply is ambiguous and doesn't fit any category | Treat as feedback (4c). Reply in thread: "Got your reply — treating it as feedback. Here's what I'll change: [interpretation]. Reply `approve` to publish the revision or give me more direction." |
| Post already published (status mismatch) | Log and skip. Do not attempt to republish. |

---

## CLEANUP

Cleanup runs at the top of every execution (Step 1). Rules:
- `status: "published"` — remove immediately on any run.
- `status: "scheduled"` with `scheduled_at` in the past — remove immediately (Ghost has published it).
- `status: "rejected"` older than 30 days — remove.

Keep the file lean. An empty array `[]` is a valid and healthy state.

---

## NOTE ON SLACK INTEGRATION

`systems/slack-bot/read.py` handles all READ operations via the Slack Web API using the bot token.
`systems/slack-bot/post.py` handles all WRITE operations via the same bot token.
Both scripts are invoked via Desktop Commander (mcp__Desktop_Commander__start_process). No Slack MCP connector is used.

**IMPORTANT: Bash quoting for newlines**
When posting messages via post.py from bash/Desktop Commander, use `$'...'` syntax to enable escape sequence interpretation:
- `python3 post.py C0B160MA3EK $'Line 1\nLine 2\nLine 3'` — produces actual newlines
- `python3 post.py C0B160MA3EK "Line 1\nLine 2"` — produces literal backslash-n characters

---

## NOTE ON EVAL RECORDS

Harper does NOT write eval records. The eval harness is owned by Rigby. Harper surfaces outcome data for Rigby to observe; it does not write to `systems/eval-harness/runs/` or `systems/eval-harness/skill-runs/`. Any such write from Harper is a routing error — log it.

---

## NEXT STEP

After approval completes:
1. All Slack notifications and Ghost updates are complete.
2. Run `steps/step-03-git-finalize.md` to commit pending-drafts.json and state.yaml.
<!-- personal:end -->

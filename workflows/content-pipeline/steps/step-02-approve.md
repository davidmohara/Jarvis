---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 02: Content Approval & Publish

## MANDATORY EXECUTION RULES

1. You MUST read pending-drafts.json first — only process posts that are tracked there.
2. You MUST read the reply content carefully before acting — do not publish on ambiguous signals.
3. You MUST only publish posts with `status: pending` — never re-process already published or rejected entries.
4. You MUST update pending-drafts.json after every action (publish, reject, regenerate).
5. You MUST NOT create new Ghost tags during regeneration.
6. Approval signal is ONLY valid from David's Slack user ID (U0ANHV5UXEW). Ignore replies from others.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Trigger:** Runs hourly via scheduled task
**Input:** pending-drafts.json + Slack thread replies on draft notifications
**Output:** Published Ghost posts, updated pending-drafts.json, Slack confirmations

---

## YOUR TASK

### 1. Load pending drafts

Read `workflows/content-pipeline/pending-drafts.json`. Filter for entries where `status: "pending"`.

If none: exit cleanly — nothing to process.

### 2. Check each pending draft for a reply

For each pending draft with a `slack_thread_ts`, read the thread via read.py:

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

Update pending-drafts.json — set `status: "published"`.

Notify David via post.py to #content:
```
✅ *Published!*

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
🗑️ Draft discarded — "{Post Title}"
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
*Regenerated draft* ♻️

*"{Post Title}"* (revised)

{2-3 sentence teaser of new version}

Same commands: reply `approve` to publish, `reject` to discard, or give more feedback.
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content approval halted — read.py error: {error}". Exit. |
| Ghost update/delete fails | Retry once. If still fails, notify David in #content: "Failed to {publish/delete} '{title}' — Ghost API error. Please check manually at driventodevelop.com/ghost." |
| pending-drafts.json malformed | Reset to `[]`, log error, notify #jarvis: "pending-drafts.json was corrupted and reset. Active drafts in Ghost may need manual review." |
| Reply is ambiguous and doesn't fit any category | Treat as feedback. Reply in thread: "Got your reply — treating it as feedback. Here's what I'll change: [interpretation]. Reply `approve` to publish the revision or give me more direction." |
| Post already published (status mismatch) | Log and skip. Do not attempt to republish. |

---

## CLEANUP

Periodically (when running): remove entries from pending-drafts.json that are older than 30 days with status "rejected" or "published". Keep the file lean.

---

## NOTE ON SLACK INTEGRATION

`systems/slack-bot/read.py` handles all READ operations (channel history, thread replies) via the Slack Web API using the bot token.
`systems/slack-bot/post.py` handles all WRITE operations (posting messages, thread replies) via the same bot token.
Both scripts are invoked via Desktop Commander (mcp__Desktop_Commander__start_process). No Slack MCP connector is used.
<!-- personal:end -->

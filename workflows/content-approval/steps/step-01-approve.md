---
status: not-started
started-at: ~
completed-at: ~
model: haiku
---

<!-- personal:start -->
# Step 01: Content Approval & Publish

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
11. You MUST NOT proceed past GATE 3, GATE 4, or GATE 5 below if any fails its HARD criteria.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline
**Trigger:** Runs multiple times daily via scheduled task
**Input:** pending-drafts.json (`workflows/content-approval/pending-drafts.json`) + Slack thread replies on draft notifications
**Output:** Published Ghost posts, updated pending-drafts.json, Slack confirmations

---

## CRITICAL: DESKTOP COMMANDER INITIALIZATION

Desktop Commander MUST be loaded before any Slack read or write. See `workflows/content-discovery/references/slack-integration.md` for the full initialization and retry protocol; it applies identically here.

---

## YOUR TASK

### 0. Fast-exit gate (runs before anything else)

Read `workflows/content-approval/pending-drafts.json`.

- If the array is **empty** (`[]`): exit immediately. Do not read Slack, do not call Ghost, do not run cleanup. Nothing to process.
- If all entries have `slack_thread_ts == null`: exit immediately. There are no threads to check for approval replies. Do not call Slack.

Only proceed to Step 1 if there is at least one entry with a non-null `slack_thread_ts`.

---

### 1. Ghost Status Verification (Sync pending-drafts.json with live Ghost state)

**Critical:** Before processing any drafts, verify the actual status of all pending posts in Ghost. This prevents working off stale data.

For each entry in pending-drafts.json with `status: "pending"`:

1. Call `mcp__ghost-blog__get_post(post_id="{ghost_post_id}", formats="lexical")`

2. Inspect the returned post object:
   - If `post.status == "published"`: The draft was published externally. Update pending-drafts.json entry: set `status: "published"`, add `published_at: {post.published_at}`. This entry will be cleaned up in Step 2.
   - If `post.status == "scheduled"`: The draft is scheduled. Update pending-drafts.json entry: set `status: "scheduled"`, add `scheduled_at: {post.scheduled_at}`. This entry will be cleaned up in Step 2 if past the scheduled date.
   - If `post.status == "draft"`: The draft is still in draft state (expected). Leave as `status: "pending"`. Continue processing.
   - If post not found (404): The post was deleted externally. Update pending-drafts.json entry: set `status: "deleted_externally"`. This entry will be cleaned up in Step 2.

3. If any entry's status changed during this verification, write the updated pending-drafts.json immediately before proceeding.

**Why this matters:** Stale data can lead to attempting to re-publish already-published posts, re-deleting already-deleted posts, or losing sync with Ghost's source of truth. Always verify first.

---

### 2. Load and clean pending-drafts.json

Read `workflows/content-approval/pending-drafts.json`.

**Before anything else, run cleanup:**

- Remove all entries where `status: "published"` — they are done.
- Remove all entries where `status: "scheduled"` AND `scheduled_at` is in the past (before current UTC time) — Ghost has already published them.
- Remove all entries where `status: "rejected"` AND `created_at` is older than 30 days.
- Remove all entries where `status: "deleted_externally"` AND `created_at` is older than 30 days.

If any entries were removed, write the updated array back to pending-drafts.json immediately.

Now filter the remaining entries for `status: "pending"`.

If none: exit cleanly — nothing to process.

### 3. Exit early if no pending drafts remain

After cleanup, if the remaining pending-drafts.json array contains **zero** entries with `status: "pending"`:
- Exit cleanly
- Do not read Slack
- No Slack notifications needed
- No further processing

Only proceed to Step 4 if there is at least one entry with `status: "pending"`.

### 4. Check each pending draft for a reply

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

---

## QUALITY GATE 3 — Approval Decision (HARD, BLOCKING)

Run this gate for every draft that has a reply from David (Step 4). This formalizes and replaces the old ad hoc "classify the reply" prose into an explicit three-outcome decision gate.

**Outcomes — exactly one must be selected, checked in this order, stop at first match:**

| Outcome | Signal | Examples | Action |
|---------|--------|----------|--------|
| **Approve** | Approval keywords | `approve`, `approved`, `yes`, `publish`, `go`, `ship it`, `looks good`, `post it` | → GATE 4 then Step 6a (Publish) |
| **Reject** | Rejection keywords | `reject`, `rejected`, `no`, `delete`, `discard`, `trash`, `kill it`, `nope` | → Step 6b (Delete) |
| **Request Revisions** | Everything else that isn't ambiguous noise | Two existing sub-paths, both pre-dating this gate: (a) **surgical edit** — keyword match on `put/add/insert/include the link`, `change/update/swap/replace/fix the image`, `update/edit/fix the post`, `change the title` → Step 6d (Editorial Edit Path, execute directly, do not regenerate); (b) **substantive rewrite** — everything else (tone, angle, structure, length, missing context) → Step 6c (Regenerate) | → GATE 4 applies only if the revision path re-publishes; regeneration produces a new pending draft, not an immediate publish |

**On "Request Revisions":** the label groups the two pre-existing sub-paths (editorial edit vs. regenerate). It does not authorize a new fourth behavior.

**Ambiguous replies:** If a reply doesn't clearly match Approve or Reject and contains no revision-instruction content that a human would recognize as a change request, treat it as Request Revisions → Regenerate path, and say so explicitly in the Slack reply (see FAILURE MODES, "Reply is ambiguous").

Log the result:
```
[Gate 3] Draft: "{title}" ({ghost_post_id})
[Gate 3] Reply: "{reply text, truncated to 80 chars}"
[Gate 3] Outcome: approve | reject | request-revisions (edit | regenerate)
[Gate 3] PASS — routing to {action}.
```

Write `gate_3_outcome` for this draft into `state.yaml` `accumulated-context` at completion.

---

### 6a-6d. Execute the routed action

Continue to the outcome-specific section below based on GATE 3's result:
- Approve → **Obsidian Note Update Protocol** then **Section 6a**
- Reject → **Section 6b**
- Request Revisions (surgical edit) → **Section 6d**
- Request Revisions (substantive rewrite) → **Section 6c**

---

## Obsidian Note Update Protocol (for all publish operations)

Follow `references/obsidian-note-update.md` (read it when publishing) for the Obsidian source-note update steps.

### 6a. If Approved — Publish

**Execution order:**
1. Update Obsidian file (if it exists)
2. GATE 4 — Publishing pre-flight
3. Publish to Ghost (mark as live)
4. GATE 5 — Delivery verification
5. Update pending-drafts.json
6. Notify David via Slack
7. Update reference docs

---

**Step 1: Update Obsidian file** — See detailed instructions above in "Obsidian Note Update" section (Steps 1-7).

---

## QUALITY GATE 4 — Publishing Pre-flight (HARD, BLOCKING)

Run the Gate 4 pre-flight checklist in `references/gate-4-preflight.md` (read it before any publish call).

## QUALITY GATE 5 — Delivery Verification (HARD, BLOCKING)

Run the Gate 5 delivery-verification protocol in `references/gate-5-delivery.md` (read it after publishing).

### 6b. If Rejected — Delete

```
mcp__ghost-blog__delete_post(post_id="{ghost_post_id}")
```

Update pending-drafts.json — set `status: "rejected"`.

Notify via post.py to #content (reply in same thread):
```
[REJECTED] Draft discarded — "{Post Title}"
```

### 6c. If Feedback — Regenerate

**Only use this path for substantive content rewrites** — tone, angle, structure, length, missing context. If the reply contains any editorial keywords from GATE 3's "Request Revisions" table, go to Section 6d instead.

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

Create a new Ghost draft with the revised content (same process as content-discovery's step-01, Steps 7-9, including GATE 2 there before creation).

Update pending-drafts.json — replace the old entry with the new one (new ghost_post_id, new slack_thread_ts, status: "pending").

Post the new draft notification to #content as a reply in the original thread:
```
[REGENERATED] Draft revised

"{Post Title}" (revised)

{2-3 sentence teaser of new version}

Same commands: reply `approve` to publish, `reject` to discard, or give more feedback.
```

### 6d. Editorial Edit Path — Execute Directly

**Use this path when GATE 3 routed to "Request Revisions (surgical edit)".** Execute the edit directly against Ghost Admin API. Do NOT delete the draft. Do NOT regenerate.

**Read `identity/CONTENT-VOICE.md` before writing any new text.** If the edit requires writing prose (e.g., adding context around a link), it must match David's voice.

Execute the link-insertion, image-swap, and post-edit protocols in `references/editorial-edits.md` (read it when performing an editorial edit).

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content approval paused — read.py error: {error}". Exit. |
| GATE 4 fails on any check | Do not publish. Notify David in #content: "[ERROR] '{title}' failed publishing pre-flight ({failed check}) — needs manual review before it can go live." Leave status as "pending". |
| Ghost publish fails with "Someone else is editing this post" | Retry 3 times with 2s and 5s delays. If all fail: set status to "approved_pending_publish", notify David, prepare for retry on next run. |
| GATE 5 fails (publish call succeeded but verification shows status/url/timestamp not confirmed) | Do NOT send [PUBLISHED]. Set status to "approved_pending_publish". Notify David: "[ERROR] Publish call for '{title}' returned success but could not be verified live — check driventodevelop.com/ghost manually." |
| Ghost update/delete fails (other errors) | Retry once. If still fails, notify David in #content: "Failed to {action} '{title}' — Ghost API error: {error}. Please check manually at driventodevelop.com/ghost." |
| Link search returns no authoritative source | Skip the link. Reply in thread: "[UPDATED] Searched for a link to '{phrase}' — no authoritative source found. Skipped. Reply `approve` to publish as-is or give a specific URL to use." |
| Editorial edit PATCH fails | Log error. Notify in thread: "[ERROR] Could not apply edit to '{title}' — {error}. Please make the change manually in Ghost." |
| pending-drafts.json malformed | Reset to `[]`, log error, notify #jarvis: "pending-drafts.json was corrupted and reset. Active drafts in Ghost may need manual review." |
| Reply is ambiguous and doesn't fit any category | Treat as Request Revisions → Regenerate (GATE 3). Reply in thread: "Got your reply — treating it as feedback. Here's what I'll change: [interpretation]. Reply `approve` to publish the revision or give me more direction." |
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

## YOUR TASK — Closing (state bookkeeping)

After the run completes (published, rejected, regenerated, edited, or a clean no-op exit):

1. Write `status: complete` and `completed-at` to this file's frontmatter, and record outputs (at minimum: `threads_checked`, `new_approvals`, `new_rejections`, `new_edits`, `published`, `gate_3_outcomes`, `gate_4_result`, `gate_5_result`) in `state.yaml` `accumulated-context`.
2. Write those same output keys into `state.yaml`'s `accumulated-context`.
3. Set `state.yaml`'s `current-step: step-02`.

## NEXT STEP

After approval completes:
1. All Slack notifications and Ghost updates are complete.
2. Run `steps/step-02-git-finalize.md` to commit pending-drafts.json and state.yaml.
<!-- personal:end -->

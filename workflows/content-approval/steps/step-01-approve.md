---
status: not-started
started-at: ~
completed-at: ~
model: haiku
---

<!-- personal:start -->
# Step 01: Tracker Resync, Cleanup & Editorial Edits

> Filename retained as `step-01-approve.md` for compatibility — verify scripts, guardrails, and `workflows/content-pipeline/steps/step-02-approve.md` reference this path. The approve-keyword publish flow it used to implement is retired (2026-10-20): publishing is external, David publishes directly in Ghost.

## MANDATORY EXECUTION RULES

1. You MUST read pending-drafts.json first — only process posts that are tracked there.
2. You MUST NOT publish, schedule, or delete any Ghost post. Publishing and deletion are external — David does both directly in Ghost. The resync below is how the tracker learns about it.
3. You MUST only run editorial edits against posts with `status: pending` — never touch already published, scheduled, rejected, or externally deleted entries beyond the resync/cleanup transitions below.
4. You MUST update pending-drafts.json after every action (resync status change, cleanup removal, or editorial edit).
5. You MUST NOT create new Ghost tags during an editorial edit.
6. Editorial instructions are ONLY valid from David's Slack user ID (U0ANHV5UXEW). Ignore replies from others.
7. You MUST remove `status: "published"` entries from pending-drafts.json on every run — they are done and take up space.
8. You MUST remove `status: "scheduled"` entries from pending-drafts.json once their `scheduled_at` date has passed.
9. **NO EMOJI in Slack messages.** Use text labels like `[UPDATED]`, `[ERROR]` instead. Emoji corrupt in shell-to-Slack transmission and render as garbage characters.
10. Editorial edits execute directly via Ghost Admin API (see `references/editorial-edits.md`). This workflow has no regeneration path — substantive rewrite requests are deferred to content-discovery's DRAFT EDIT PATH, which runs on its daily schedule. (See err-20260726T164307-HSUVNE.)

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline
**Trigger:** On demand (the former 4x-daily scheduled sweep is retired; content-discovery's daily 6 AM run carries the scheduled resync + cleanup via its step-01 Step 1a)
**Input:** pending-drafts.json (`workflows/content-approval/pending-drafts.json`) + Slack thread replies on draft notifications
**Output:** Resynced/cleaned pending-drafts.json, edited Ghost drafts, Slack confirmations

---

## CRITICAL: DESKTOP COMMANDER INITIALIZATION

Desktop Commander MUST be loaded before any Slack read or write. See `workflows/content-discovery/references/slack-integration.md` for the full initialization and retry protocol; it applies identically here.

---

## YOUR TASK

### 0. Fast-exit gate (runs before anything else)

Read `workflows/content-approval/pending-drafts.json`.

- If the array is **empty** (`[]`): exit immediately. Do not read Slack, do not call Ghost, do not run cleanup. Nothing to process.
- If all entries have `slack_thread_ts == null`: skip the thread scan (Step 4) but still run the resync and cleanup (Steps 1-2) — external publishes must be reflected even when there are no threads to read.

---

### 1. Ghost Status Verification (Sync pending-drafts.json with live Ghost state)

**Critical:** Before anything else, verify the actual status of all pending posts in Ghost. Publishing is external, so this resync is the only way the tracker learns that a draft went live.

For each entry in pending-drafts.json with `status: "pending"`:

1. Call `mcp__ghost-blog__get_post(id="{ghost_post_id}")`

2. Inspect the returned post object:
   - If `post.status == "published"`: The draft was published externally. Update pending-drafts.json entry: set `status: "published"`, add `published_at: {post.published_at}`. This entry will be cleaned up in Step 2.
   - If `post.status == "scheduled"`: The draft is scheduled. Update pending-drafts.json entry: set `status: "scheduled"`, add `scheduled_at: {post.published_at}` (Ghost stores the scheduled time in `published_at` for scheduled posts). This entry will be cleaned up in Step 2 once the scheduled time has passed.
   - If `post.status == "draft"`: The draft is still in draft state (expected). Leave as `status: "pending"`. Continue processing.
   - If post not found (404): The post was deleted externally. Update pending-drafts.json entry: set `status: "deleted_externally"`. This entry will be cleaned up in Step 2.

3. If any entry's status changed during this verification, write the updated pending-drafts.json immediately before proceeding.

**Why this matters:** Stale data leads to editing posts that are already live or gone, and to a tracker that claims drafts are pending when they published weeks ago. Always verify first.

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

### 4. Check each pending draft for editorial feedback

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

Ignore: bot replies, replies from other users, reactions (emoji only — those are not instructions).

Classify each reply from David:

| Reply class | Signal | Action |
|-------------|--------|--------|
| **Approve / reject** | `approve`, `approved`, `yes`, `publish`, `go`, `ship it`, `looks good`, `post it`, `reject`, `no`, `delete`, `discard`, `kill it` | **No action.** Publishing and deletion are external — David acts in Ghost directly and Step 1's resync picks it up. Do not reply in the thread. |
| **Editorial edit (surgical)** | keyword match on `put/add/insert/include the link`, `change/update/swap/replace/fix the image`, `update/edit/fix the post`, `change the title` | Execute the edit directly — see the Editorial Edit Path below. |
| **Substantive rewrite** | tone, angle, structure, length, missing context | **Defer to content-discovery.** Its step-01 DRAFT EDIT PATH handles rewrites on the daily run. Record the reply in `rewrites_deferred` and move on. Do not attempt the rewrite here. |
| **Ambiguous** | none of the above | If a human would read it as a change request, treat it as an editorial edit if surgical, otherwise defer to discovery. If it is pure noise, skip it. |

Skip replies already acted on — a reply whose `reply_ts` already appears in the entry's `editorial_edits` array was handled (by this workflow or by discovery's Step 1b, which uses the same tracking).

---

## Editorial Edit Path — Execute Directly

**Read `identity/CONTENT-VOICE.md` before writing any new text.** If the edit requires writing prose (e.g., adding context around a link), it must match David's voice.

Execute the link-insertion, image-swap, and post-edit protocols in `references/editorial-edits.md` (read it when performing an editorial edit).

After each applied edit, update the pending-drafts.json entry: append to its `editorial_edits` array with `reply_ts`, `instruction`, `applied_at`, `summary`. Leave `status` as `"pending"`.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| read.py fails (script not found or token error) | Report failure via post.py to #jarvis: "Content approval paused — read.py error: {error}". Exit. |
| Ghost resync call fails for a post (non-404 error) | Skip that entry, leave its status unchanged, note it in `accumulated-context`. Do not abort the run — resync the rest. |
| Ghost edit fails | Retry once. If still fails, notify David in #content: "Failed to edit '{title}' — Ghost API error: {error}. Please make the change manually at driventodevelop.com/ghost." |
| Link search returns no authoritative source | Skip the link. Reply in thread: "[UPDATED] Searched for a link to '{phrase}' — no authoritative source found. Skipped." |
| Editorial edit PATCH fails | Log error. Notify in thread: "[ERROR] Could not apply edit to '{title}' — {error}. Please make the change manually in Ghost." |
| pending-drafts.json malformed | Reset to `[]`, log error, notify #jarvis: "pending-drafts.json was corrupted and reset. Active drafts in Ghost may need manual review." |

---

## CLEANUP

Cleanup runs at the top of every execution (Steps 1-2). Rules:
- `status: "published"` — remove immediately on any run.
- `status: "scheduled"` with `scheduled_at` in the past — remove immediately (Ghost has published it).
- `status: "rejected"` older than 30 days — remove.
- `status: "deleted_externally"` older than 30 days — remove.

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

After the run completes (edits applied, or a clean no-op exit):

1. Write `status: complete` and `completed-at` to this file's frontmatter, and record outputs (at minimum: `threads_checked`, `tracker_resynced`, `tracker_entries_removed`, `new_edits`, `rewrites_deferred`, `outcome`) in `state.yaml` `accumulated-context`.
2. Write those same output keys into `state.yaml`'s `accumulated-context`.
3. Set `state.yaml`'s `current-step: step-02`.

## NEXT STEP

After the resync/edit pass completes:
1. All Slack notifications and Ghost edits are complete.
2. Run `steps/step-02-git-finalize.md` to commit pending-drafts.json and state.yaml.
<!-- personal:end -->

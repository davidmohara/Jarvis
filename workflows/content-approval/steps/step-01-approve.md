---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

**Agent:** Harper
**Trigger:** Runs multiple times daily via scheduled task
**Input:** pending-drafts.json (`workflows/content-approval/pending-drafts.json`) + Slack thread replies on draft notifications
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

**On "Request Revisions":** this label is new as of this gate — see workflow.md's GATES OVERVIEW flag. The two sub-paths it groups (editorial edit vs. regenerate) are unchanged, pre-existing behavior from the retired step-02-approve.md. Do not treat "request revisions" as authorizing a new fourth behavior; it is a naming/grouping change over the existing two.

**Ambiguous replies:** If a reply doesn't clearly match Approve or Reject and contains no revision-instruction content that a human would recognize as a change request, treat it as Request Revisions → Regenerate path, and say so explicitly in the Slack reply (see FAILURE MODES, "Reply is ambiguous").

Log the result:
```
[Gate 3] Draft: "{title}" ({ghost_post_id})
[Gate 3] Reply: "{reply text, truncated to 80 chars}"
[Gate 3] Outcome: approve | reject | request-revisions (edit | regenerate)
[Gate 3] PASS — routing to {action}.
```

Write `gate_3_outcome` for this draft into this step's `outputs` at completion.

---

### 6a-6d. Execute the routed action

Continue to the outcome-specific section below based on GATE 3's result:
- Approve → **Obsidian Note Update Protocol** then **Section 6a**
- Reject → **Section 6b**
- Request Revisions (surgical edit) → **Section 6d**
- Request Revisions (substantive rewrite) → **Section 6c**

---

## Obsidian Note Update Protocol (for all publish operations)

**This protocol applies when publishing a post (Step 6a) or when manually updating a published post. Run this BEFORE Ghost publish to ensure vault sync on success.**

> **Note for content-discovery:** When discovery creates a pending-drafts.json entry, it sets a `content_type` field on that entry — either `"post"` or `"article"`. Harper uses this field here to route to the correct vault folder. If `content_type` is absent, Harper defaults to `"post"`.

### Obsidian Update Steps:

1. **Determine the vault folder** from the `content_type` field on the pending-drafts.json entry:
   - If `content_type == "article"`: vault folder is `Mind/Articles/`
   - If `content_type == "post"`, is absent, or is null: vault folder is `Mind/Posts/`

2. **Build the filename and find the note:**
   - If the pending-drafts.json entry has an `obsidian_slug` field that is non-null and non-empty: use it as the filename slug.
   - If `obsidian_slug` is absent or null: derive from the `title` field — lowercase, hyphens for spaces, strip punctuation.
   - **Expected filename pattern:** `_{slug}.md` (with leading underscore, indicating draft status)
   - Example: title "The Corrections Are the Leak" → expected filename `_the-corrections-are-the-leak.md`

3. **Find the note** using `mcp__obsidian-mcp-tools__get_vault_file` with the path `{vault_folder}/_{slug}.md`. If not found, surface a hard failure to David.

4. **If the note is NOT found:** Do NOT skip silently. Stop all processing immediately:
   - Log the missing file
   - Prepend this warning to any Slack notification:
   ```
   [WARNING] Obsidian note not found — expected {vault_folder}/_{slug}.md. Cannot proceed with publication.
   ```
   - Do NOT proceed to Ghost publish if the note is missing. This prevents publishing without vault sync.

5. **If found, update the note in this exact order:**

   **Step 5a: Update frontmatter fields:**
   - Set `status: "Posted"` (changed from "Draft" or similar)
   - Set `published_url: "{url from Ghost response}"` (add the live URL)
   - Set `published_date: "{ISO 8601 timestamp from Ghost response}"` (when published)

   **Step 5b: Update tags in frontmatter:**
   - Add tag: `status: Posted` (indicates publication status)
   - Remove tag: `status: Draft` (if present, old draft tag)
   - Keep all other tags unchanged

   **Step 5c: Rename the file:**
   - Strip the leading `_` from the filename
   - New filename pattern: `{slug}.md` (no leading underscore)
   - Example: `_the-corrections-are-the-leak.md` → `the-corrections-are-the-leak.md`
   - Use `mcp__obsidian-mcp-tools__rename_vault_file` for the rename

6. **If any step in 5a/5b/5c fails:**
   - Log the failure with specific error details
   - Prepend a warning to the Slack notification: `[WARNING] Could not update Obsidian vault — {specific error}. Post is live but vault is out of sync. Update manually.`
   - Continue to Ghost publish — the post must still be published even if vault sync fails
   - But note that the vault is now out of sync and will need manual correction

7. **Verify the update succeeded:**
   - Re-fetch the file from Obsidian to confirm all changes: frontmatter updated, filename renamed, tags changed
   - If verification fails, note it but continue — the important part (vault update) was attempted

---

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

Run immediately before the Ghost publish call. This formalizes the checks discovery's GATE 2 already ran at draft-creation time — re-run here because time has passed since drafting and an editorial edit (Section 6d) may have touched the post since, so the pre-publish state needs its own independent check rather than trusting the draft-time gate.

Fetch the current post via `mcp__ghost-blog__get_post(post_id="{ghost_post_id}", formats="lexical")`, then call `skills/schema-validator/SKILL.md`:

```yaml
data:
  status: "{post.status}"
  lexical_non_empty: <bool>          # your own check: does lexical have paragraph nodes
  feature_image: "{post.feature_image}"
  tags: {post.tags}                  # real tag objects as returned, not bare strings
  slug: "{post.slug}"
  obsidian_note_found: <bool>        # from the vault-sync protocol above
schema_spec:
  required_fields:
    - "feature_image"
    - "slug"
  custom_checks:
    - { field: "status", rule: "must_equal", value: "draft" }
    - { field: "lexical_non_empty", rule: "must_be_true" }
    - { field: "obsidian_note_found", rule: "must_be_true" }
  tags: { field: "tags", allowed_list: [<locked-list tag ids from workflows/content-discovery/workflow.md>], format: "object_with_id" }
```

| Check | Expected | On failure |
|-------|----------|------------|
| `post.status == "draft"` | Confirmed still a draft, not already published/scheduled (re-confirms Step 1's Ghost Status Verification, since time has passed) | **STOP.** If status changed since Step 1, do not publish — re-run Step 1 sync and re-classify. |
| `lexical` is non-empty | Has paragraph nodes | **STOP.** Do not publish a post with empty body content. Notify David and do not proceed. |
| `feature_image` is set | Non-null, non-empty URL | **STOP.** Do not publish without a feature image. If an editorial edit removed it, re-run the Step 6 image protocol from content-discovery's step-01. |
| `tags` show real tag names (not bare ID strings) and every tag is on the locked list | Cross-check against `workflows/content-discovery/workflow.md`'s LOCKED LIST table | **STOP.** If tags are malformed or off-list, fix via Ghost Admin API PUT before publishing. Never publish with a junk tag. |
| `slug` is present and non-empty | Ghost auto-generates on creation; confirm it wasn't cleared by a prior edit | **STOP.** If missing, this indicates a corrupted post — notify David rather than guessing a slug. |
| Obsidian note found (from the protocol above) or its failure was surfaced per Step 4 of that protocol | No silent skip | **STOP** if the note is missing and the warning wasn't prepended — do not publish without vault sync being at least attempted and reported. |

Log the result (reading `errors` back from the skill's response for anything that failed):
```
[Gate 4] Post: "{title}" ({ghost_post_id})
[Gate 4] Status: draft (confirmed) | lexical: non-empty | feature_image: set | tags: {names} (locked-list confirmed) | slug: {slug}
[Gate 4] PASS — proceeding to publish.
```

If `schema-validator` returns `valid: false` (or the direct status check above fails), log
`[Gate 4] FAIL — <errors list>` and remediate (or halt and notify David per FAILURE MODES)
before calling the publish endpoint.

---

**Step 3: Publish to Ghost, then verify — via `skills/delivery-router/SKILL.md`**

Gate 5 (delivery verification) and the publish call itself are now one skill call, because
"call the API" and "confirm it actually took" are exactly what `delivery-router`'s `ghost`
backend already does as a single unit (call `update_post`, then re-fetch and check the result
— see that skill's Process section) — keeping them as two separate manual steps here would
just be re-implementing what the skill already owns.

```yaml
content: "{ghost_post_id}"          # ghost backend keys off config.post_id; content is informational here
destinations:
  - backend: "ghost"
    required: true
    config:
      post_id: "{ghost_post_id}"
      target_status: "published"
      expected_host: "driventodevelop.com"
```

The skill's `ghost` backend handles the concurrent-edit wait/retry protocol internally (2s
retry, then 5s retry, matching what this step used to do manually) before falling through to
its general 3-attempt budget. Read `delivery_status[0]` for the outcome:

- `success: true` → `.id` is `post.url` from the verified re-fetch. This **is** Gate 5 passing
  — proceed straight to notifying David (Step 5 below). Do not re-run a separate verification
  fetch; the skill already did it and only reports `success: true` if the re-fetch confirmed
  `status == target_status`, `url` resolves to `expected_host`, and `published_at` is set.
- `success: false` → treat as both the publish failing and Gate 5 failing (the skill does not
  distinguish "the call failed" from "the call succeeded but didn't verify" in its retry
  loop — by the time it reports failure, every attempt including verification has been
  exhausted). Read `.error` for what to tell David. Keep `pending-drafts.json` status as
  "approved" (not "pending") per the concurrent-edit handling this replaces, and follow
  FAILURE MODES below.

---

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

1. Write `status: complete`, `completed-at`, and populated `outputs` (at minimum: `threads_checked`, `new_approvals`, `new_rejections`, `new_edits`, `published`, `gate_3_outcomes`, `gate_4_result`, `gate_5_result`) to this file's own frontmatter.
2. Write those same output keys into `state.yaml`'s `accumulated-context`.
3. Set `state.yaml`'s `current-step: step-02`.

## NEXT STEP

After approval completes:
1. All Slack notifications and Ghost updates are complete.
2. Run `steps/step-02-git-finalize.md` to commit pending-drafts.json and state.yaml.
<!-- personal:end -->

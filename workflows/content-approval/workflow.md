---
name: content-approval
description: Scans #content Slack thread replies for approve/reject/revision signals on pending Ghost drafts, publishes on approval, deletes on rejection, executes editorial edits and regenerations, and syncs Obsidian. Runs on-demand / multiple times daily. Second half of the split content-pipeline (successor to workflows/content-pipeline).
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "personal content publishing workflow — no decisions about individuals' access to opportunity or resources"
---

<!-- personal:start -->
# Content Approval Workflow

**Goal:** Watch #content thread replies on pending Ghost drafts and turn David's decision (approve / reject / request revisions) into the right action: publish to driventodevelop.com, delete the draft, or execute an editorial edit or regeneration, with Obsidian and reference docs kept in sync.

**Agent:** Harper — Storyteller, Communication & Thought Leadership

**Trigger:** Scheduled multiple times daily (`config/scheduled-tasks.json`, task id `content-approval`, currently 9 AM / 11 AM / 1 PM / 3 PM).

**Lineage:** This workflow is half of the former `workflows/content-pipeline/workflow.md`, split out because approval/publish runs on a different cadence and enforces different checks than discovery. See `workflows/content-discovery/workflow.md` for the discovery half and `workflows/content-pipeline/workflow.md` for the RETIRED original with a full redirect note.

**Companion workflow:** `workflows/content-discovery/workflow.md` drafts new posts and appends to the same shared `pending-drafts.json` this workflow owns (see STATE TRACKING below).
<!-- personal:end -->

---

<!-- personal:start -->
## CHANNEL

| Channel | ID | Purpose |
|---------|-----|---------|
| #content | C0B160MA3EK | David replies here to approve/reject drafts or give feedback. |

---

## SLACK INTEGRATION

> **CRITICAL — Desktop Commander MUST be loaded before any Slack operations.** See `workflows/content-discovery/workflow.md`'s SLACK INTEGRATION section for the full initialization/retry protocol — it applies identically here.

**Reading:** `systems/slack-bot/read.py` via Desktop Commander. **Writing:** `systems/slack-bot/post.py` via Desktop Commander (the `master-slack` skill). No Slack MCP connector is used.

---

## GHOST BLOG CONVENTIONS RELEVANT TO PUBLISHING

Full tag list and image conventions are documented in `workflows/content-discovery/workflow.md` (this workflow does not re-select tags or images on publish — it only validates what discovery already set, per GATE 4 below, unless an editorial edit or regeneration requires re-sourcing one).

### Author
- Always: David O'Hara — ID `68a3465b9e3561027e745c51`

### Post Status Flow
1. `workflows/content-discovery/workflow.md` creates the post with `status: draft`.
2. This workflow updates it to `status: published` only after David's explicit approval in Slack, gated by GATE 3 (approval decision), GATE 4 (publishing pre-flight), and GATE 5 (delivery verification) below.

### Ghost Admin API access

Get Admin API key: read `~/Library/Application Support/Claude/claude_desktop_config.json`, find server `ghost-blog`, read `GHOST_ADMIN_API_KEY` (`{key_id}:{hex_secret}`). Generate JWT: header `{"alg": "HS256", "kid": "{key_id}", "typ": "JWT"}`, payload `{"exp": now+300, "iat": now, "aud": "/admin/"}`, signed with `bytes.fromhex(hex_secret)` via PyJWT. Full detail and worked examples are in `steps/step-01-approve.md`.

`ghost_update_v2.py` in this directory is a reference script showing the JWT-generation and PUT-update pattern against a real post (kept for pattern reference — it has a hardcoded post_id and body from a one-off manual fix and is not meant to be re-run as-is).

---

## STATE TRACKING

**`pending-drafts.json` lives in this directory: `workflows/content-approval/pending-drafts.json`.** It is the single shared file both `content-discovery` and this workflow read and write — see `workflows/content-discovery/workflow.md`'s STATE TRACKING section for the full reasoning on why it is shared rather than split, and why it lives here rather than in content-discovery.

This workflow owns the file's lifecycle: cleanup of stale `published`/`scheduled`/`rejected`/`deleted_externally` entries, Ghost-status resync, and all status transitions after David's decision.

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

---

## GATES — OVERVIEW

This workflow enforces three deterministic gates, all in `steps/step-01-approve.md`:

3. **GATE 3 — Approval Decision (HARD)** — classifies David's Slack reply into exactly one of three outcomes: **approve**, **reject**, or **request revisions**. "Request revisions" is a formalization that groups the pre-existing "editorial edit" (surgical, keyword-detected) and "regenerate" (substantive rewrite) sub-paths under one decision label — both already existed in the retired step-02-approve.md; this gate does not add new capability, it names and gates the existing split explicitly. **Flag for human confirmation: whether "request revisions" as a single named outcome (vs. keeping editorial-edit and regenerate as two separately-gated outcomes) is the right formalization** — see the build report.
4. **GATE 4 — Publishing Pre-flight (HARD)** — before calling Ghost's publish endpoint, re-verifies tags (locked list, object format), feature_image presence, non-empty lexical, and slug — the same checks discovery's GATE 2 ran at draft time, re-checked here because time may have passed and editorial edits may have touched the post since.
5. **GATE 5 — Delivery Verification (HARD)** — after the publish call returns success, confirms via `mcp__ghost-blog__get_post` that `status == "published"` and a real, resolvable post URL is present — not just that the API call didn't error.

See step-01-approve.md for full pass/fail criteria, logging format, and escalation instructions for each.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered. Do not re-pull it.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it; if
     `status: not-started`, begin it fresh.
   - Notify the controller: "[Harper]: Resuming content-approval from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Harper]: content-approval was previously aborted at
     [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

1. Read and follow `steps/step-01-approve.md` (includes GATE 3, GATE 4, GATE 5).
2. After completion, run `steps/step-02-git-finalize.md` to commit all changes.
<!-- personal:end -->

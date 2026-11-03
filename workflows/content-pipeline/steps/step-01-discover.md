---
status: complete
started-at: "2026-11-02T22:10:00Z"
completed-at: "2026-11-03T04:25:00Z"
outputs:
  messages_scanned: 6
  new_urls: 0
  new_digests: 2
  posts_drafted: 7
  improving_blog_drafts: 0
  pending_threads_checked: 0
  editorial_feedback_found: 0
  editorial_edits_applied: 0
  tracker_resynced: 7
  tracker_entries_removed: 3
  hub_synced: 1
  gate_1_result: "PASS: ok true, 6 messages from C0B160MA3EK over a 24h window"
  gate_2_result: "PASS x4 (word counts 330-528, no em-dashes, 4 H2 each with closing What to do, tags on locked list, metas within limits, images landscape and CDN-uploaded). Checks run by inline script; skills/schema-validator not invoked."
  outcome: "4 Ghost drafts created and verified (2 from David's pasted text, 2 Watchtower digests), 4 Slack notifications plus 1 skip note sent. 3 'Draft:' bot messages first skipped by router, then drafted per David's correction (not noise): vetted, linked, Ghost drafts created, Slack notified. Hub agent-governance-guide broken link fixed and Give Every Agent a Manager linked. SUPERSEDED skip note: (Anxiety Is a Supermarket Aisle, We Keep Looking for One Cause, Would You Write the Same Book in Ten Years). Tracker resynced: 3 published removed, 4 scheduled kept. Flags: Anthropic pricing-pressure claim unverified and dropped; Principled Business linked to principledbusiness.org; hub candidate for David: Give Every Agent a Manager (agent-governance-guide has no post-list section, so no write); agent-governance-guide links a broken URL (your-agents-keys-nobody-changed-the-locks vs your-agents-have-keys-nobody-changed-the-locks)."
model: sonnet
---

<!-- personal:start -->
# Step 01: Discover and Draft (delegates to content-discovery)

## MANDATORY EXECUTION RULES

1. You MUST read and execute `workflows/content-discovery/steps/step-01-discover.md` in full, including GATE 1 (Source Integrity) and GATE 2 (Content Schema Validation). Do not skip, weaken, or defer either gate.
2. You MUST NOT re-implement discovery logic in this step. The gated step file is the single source of truth for drafting, tags, images, Ghost creation, and notification.
3. You MUST write all state to the shared file `workflows/content-approval/pending-drafts.json`. Do not create or write a local pending-drafts file in this directory.
4. You MUST record this run's outputs in this file's frontmatter after execution (see YOUR TASK).

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline.
**Mode:** Delegation to the gated sub-workflow step.
**Input:** #content Slack channel (last 24 hours), shared pending-drafts.json.
**Output:** Ghost draft posts + Slack review notifications; outputs recorded in this file's frontmatter.

---

## CONTEXT BOUNDARIES

- The gated step's CONTEXT BOUNDARIES apply in full.
- The Ghost blog conventions, voice rules, digest format, and dedup rules are owned by `workflows/content-discovery/workflow.md` and its `references/` files. Read it before executing; do not rely on memory.

---

## YOUR TASK

### Sequence

1. Write `status: in-progress` and `started-at` to this file's frontmatter.

2. Read `workflows/content-discovery/workflow.md` (conventions), then read and execute `workflows/content-discovery/steps/step-01-discover.md` exactly as written, including GATE 1 and GATE 2.

3. After execution, write `status: complete`, `completed-at`, and `outputs` to this file's frontmatter. Record at minimum:
   ```
   messages_scanned: N
   new_urls: N
   new_digests: N
   posts_drafted: N
   improving_blog_drafts: N
   pending_threads_checked: N
   outcome: "<one-line summary>"
   ```

4. Update `state.yaml`: set `current-step: step-02`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Either gate fails in the delegated step | Follow that gate's failure protocol in the gated step file. Do not proceed to step-02 on a gate failure. |
| Gated step file is missing or unreadable | Abort the run. Notify #jarvis: "content-pipeline step-01 cannot delegate: content-discovery step-01-discover.md unavailable." |

## NEXT STEP

Read fully and follow: `step-02-approve.md`
<!-- personal:end -->

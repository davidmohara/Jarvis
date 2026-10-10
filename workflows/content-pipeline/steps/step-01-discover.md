---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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
- The Ghost blog conventions, voice rules, digest format, and dedup rules are owned by `workflows/content-discovery/workflow.md`. Read it before executing; do not rely on memory.

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

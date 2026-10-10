---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 02: Approval and Publish (delegates to content-approval)

## MANDATORY EXECUTION RULES

1. You MUST read and execute `workflows/content-approval/steps/step-01-approve.md` in full, including GATE 3 (Approval Decision), GATE 4 (Publishing Pre-flight), and GATE 5 (Delivery Verification). Do not skip, weaken, or defer any gate.
2. You MUST NOT re-implement approval logic in this step. The gated step file is the single source of truth for approval classification, publishing, editorial edits, regeneration, and state cleanup.
3. You MUST write all state to the shared file `workflows/content-approval/pending-drafts.json`. Do not create or write a local pending-drafts file in this directory.
4. You MUST record this run's outputs in this file's frontmatter after execution (see YOUR TASK).

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline.
**Mode:** Delegation to the gated sub-workflow step.
**Input:** #content Slack thread replies, shared pending-drafts.json, live Ghost post state.
**Output:** Published/rejected/edited Ghost posts + updated pending-drafts.json; outputs recorded in this file's frontmatter.

---

## CONTEXT BOUNDARIES

- The gated step's CONTEXT BOUNDARIES apply in full.
- Only David's replies (U0ANHV5UXEW) act as approval signals; the gated step enforces this.
- Publishing is irreversible. The gated step's GATE 4 pre-flight checkpoint must pass before any publish call.

---

## YOUR TASK

### Sequence

1. Write `status: in-progress` and `started-at` to this file's frontmatter.

2. Read `workflows/content-approval/workflow.md` (conventions), then read and execute `workflows/content-approval/steps/step-01-approve.md` exactly as written, including GATE 3, GATE 4, and GATE 5.

3. After execution, write `status: complete`, `completed-at`, and `outputs` to this file's frontmatter. Record at minimum:
   ```
   threads_checked: N
   new_approvals: N
   new_rejections: N
   new_edits: N
   actions_taken: N
   published: N
   pending_approvals: N
   outcome: "<one-line summary>"
   ```

4. Update `state.yaml`: set `current-step: step-03`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Any gate fails in the delegated step | Follow that gate's failure protocol in the gated step file. Do not proceed to step-03 on a gate failure unless the gated step's protocol says to. |
| Gated step file is missing or unreadable | Abort the run. Notify #jarvis: "content-pipeline step-02 cannot delegate: content-approval step-01-approve.md unavailable." |

## NEXT STEP

Read fully and follow: `step-03-git-finalize.md`
<!-- personal:end -->

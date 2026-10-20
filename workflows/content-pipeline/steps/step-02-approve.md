---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- personal:start -->
# Step 02: Tracker Resync and Editorial Edits (delegates to content-approval)

> Filename retained as `step-02-approve.md` for compatibility — verify scripts and this workflow's state reference this path. The approve-keyword publish flow it used to delegate is retired (2026-10-20): publishing is external, David publishes directly in Ghost.

## MANDATORY EXECUTION RULES

1. You MUST read and execute `workflows/content-approval/steps/step-01-approve.md` in full: Ghost-status resync, cleanup, and the editorial-edit path. Do not skip or defer the resync or cleanup.
2. You MUST NOT re-implement resync or edit logic in this step. The delegated step file is the single source of truth for resync, cleanup, editorial edits, and rewrite deferral.
3. You MUST NOT publish, schedule, or delete any Ghost post. Publishing and deletion are external — David does both directly in Ghost.
4. You MUST write all state to the shared file `workflows/content-approval/pending-drafts.json`. Do not create or write a local pending-drafts file in this directory.
5. You MUST record this run's outputs in `state.yaml` `accumulated-context` after execution (see YOUR TASK).

---

## EXECUTION PROTOCOL

**Agent:** Harper, spawned by the coordinator, never executed inline.
**Mode:** Delegation to the content-approval step.
**Input:** #content Slack thread replies, shared pending-drafts.json, live Ghost post state.
**Output:** Resynced/cleaned pending-drafts.json + edited Ghost drafts; outputs recorded in `state.yaml` `accumulated-context`.

---

## CONTEXT BOUNDARIES

- The delegated step's CONTEXT BOUNDARIES apply in full.
- Only David's replies (U0ANHV5UXEW) act as editorial instructions; the delegated step enforces this.

---

## YOUR TASK

### Sequence

1. Write `status: in-progress` and `started-at` to this file's frontmatter.

2. Read `workflows/content-approval/workflow.md` (conventions), then read and execute `workflows/content-approval/steps/step-01-approve.md` exactly as written.

3. After execution, write `status: complete` and `completed-at` to this file's frontmatter. Record at minimum these keys in `state.yaml` `accumulated-context`:
   ```
   threads_checked: N
   tracker_resynced: N
   tracker_entries_removed: N
   new_edits: N
   rewrites_deferred: N
   outcome: "<one-line summary>"
   ```

4. Update `state.yaml`: set `current-step: step-03`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Any failure in the delegated step | Follow that step's failure protocol. Do not proceed to step-03 on a failure unless the delegated step's protocol says to. |
| Delegated step file is missing or unreadable | Abort the run. Notify #jarvis: "content-pipeline step-02 cannot delegate: content-approval step-01-approve.md unavailable." |

## NEXT STEP

Read fully and follow: `step-03-git-finalize.md`
<!-- personal:end -->

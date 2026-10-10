---
title: Content workflow family fix (commentary cleanup, decision 2)
agent: master
date: 2026-10-10
session: 2026-10-10 commentary cleanup audit + content-family fix
tags: [content-pipeline, content-discovery, content-approval, cleanup]
duration_minutes: 60
importance: 7
session_id: "2026-10-10-commentary-audit"
agent-source: master
---

David directed a full-system commentary audit (skills, workflows, agents, identity, SYSTEM.md, CLAUDE.md): strictly instructional files only. Seven read-only audit agents reported ~6,600 removable lines; consolidated plan at `specs/commentary-cleanup-plan-2026-10-10.md`. All four plan decisions resolved: frontmatter state purges (to state.yaml/logs), step-file boilerplate centralizes via shared references, canonical owners locked (conventions.md, routing.md, SYSTEM.md, git skill), eval capture moves to hooks.

## What was executed (decision 2: content family)

David confirmed content-pipeline, content-discovery, and content-approval ALL run regularly; the "retired/superseded" story in the repo was wrong and self-contradictory. Fix executed within David's authorization to edit personal blocks in this family:

- `workflows/content-pipeline/workflow.md`: rewritten as live end-to-end orchestrator delegating to the two gated sub-workflows (326 to ~85 lines). Status flip-flop record, split narrative, and 273-line "Historical" duplicate body removed.
- `workflows/content-pipeline/steps/step-01-discover.md` + `step-02-approve.md`: ~1,100 lines of ungated duplicate logic replaced with delegation stubs that execute the gated sub-workflow steps in full (GATE 1-5 always enforced now, where the old copies bypassed all gates).
- `step-03-git-finalize.md`: July 24 run transcript rewritten as a real git-finalize instruction. `step-04`: false RETIRED note removed.
- Verifiers `verify/step-01-discover.py`, `verify/step-02-approve.py` and `content-pipeline-verification/` (workflow.md + step-01-verify.md) repointed from deleted local `pending-drafts.json` to the live shared `workflows/content-approval/pending-drafts.json`.
- Deleted: `workflows/content-pipeline/pending-drafts.json` (stale; all 20 entries verified present in live file), `step-02-status.log`, `ghost_update_v2.py` duplicate.
- False "retired"/lineage claims and build meta-commentary removed from content-discovery, content-approval, their steps, verifier docstrings, and both descriptions in `config/scheduled-tasks.json`.
- All verifiers compile; no stale path references remain; personal block structure preserved throughout.

## Open items surfaced (need David)

1. GATE 3 design question (removed from files, parked here): is "request revisions" the right single outcome, vs. editorial-edit and regenerate as two separately-gated outcomes?
2. `workflows/content-approval/ghost_update_v2.py` is FLAGGED FOR HUMAN REVIEW: redacted-credential reference copy. Keep, or delete entirely since the JWT pattern is documented in step-01-approve.md?
3. Content-family step frontmatter `outputs:` mirrors still serve as content-pipeline-verification's data source; their purge is gated on Phase F4 reader migration.

## Follow-ups

- Nothing committed yet; session-close commit per git skill.
- Remaining plan phases (A, B, D, E, F) await David's go.

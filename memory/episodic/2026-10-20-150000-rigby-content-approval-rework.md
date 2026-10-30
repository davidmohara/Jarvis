---
type: working-archive
task_id: "session"
session_id: "rigby-2026-10-20-150000"
agent-source: rigby
created: 2026-10-20T15:00:00-05:00
expires: 2026-10-22T15:00:00-05:00
status: archived
context: "content-approval rebuilt (external publishing model), tracker custodianship moved to discovery — 2026-10-20"
date: 2026-10-20
source_file: memory/working/2026-10-20-150000-rigby-content-approval-rework.md
tags:
  - rigby
  - omnifocus
  - pipeline
related_people:
salience:
  score: 6
  last-promoted-check: 2026-10-30
  promoted: true
---

**What was requested/produced:** David approved Rigby's redesign of the content pipeline after diagnosing pending-drafts.json rot (cleanup never ran because the 9/11/13/15 content-approval sweep never executed — zero eval records ever, David's real pattern is Slack feedback + direct Ghost publish).

**Changes:**
- Discovery is now pending-drafts.json custodian: new Step 1a (Ghost resync + 4 cleanup rules) runs before the editorial scan in every daily 6 AM run. Schema/ghost-conventions/workflow.md updated.
- Content-approval rebuilt: gates retired (no publish gates remain), on-demand trigger, keeps fast-exit + resync + cleanup + thread scan + editorial-edit path. Step-01 fast-exit no longer skips resync when all thread timestamps null. 4 references/guardrail files deleted; verify script pruned of publish-preflight check.
- Verification + pipeline retargeted to tracker-state-vs-Ghost lens; delivery-router, schema-validator, master-workflow-registry, adversarial-isolation, scheduled-tasks.json (entry marked RETIRED SWEEP 2026-10-20) all updated.
- Impact analysis covered 20+ referencing files before edits; all fence/JSON/parse checks clean.
- Tracker itself reconciled earlier: 48 -> 2 entries (40 live removed, 6 deleted-externally removed, 2 scheduled kept).

**Surfaced / follow-ups:**
- Cowork scheduled task untouched per instruction; if it ever fires it now runs the slim workflow harmlessly.
- step-01-approve.md / step-02-approve.md filename misnomers kept for compatibility (header comments explain).
- reference/blog-ideas.md "Published section move" now has NO owner (was done by retired publish path) — candidate new home: discovery Step 1a.
- Nothing committed; next session commit carries ~30+ changed/deleted files.

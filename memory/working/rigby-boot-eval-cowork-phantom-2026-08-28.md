---
date: 2026-08-28
session: rigby-boot-eval-cowork-phantom
type: work-summary
tags: [rigby, eval-harness, boot, cowork-hook, race-condition, capability-fix, bug-fix]
---

# Rigby — boot eval cowork-path phantom duplicate fix — Session Summary

Round 3 of the same underlying investigation, same real session
(`4378bed7-1972-4c0f-8361-48ef8b8f8d8b`), same day.

- Round 1: `memory/working/rigby-boot-eval-consolidation-2026-08-28.md` — fixed two independent,
  disagreeing `session_id`-inference implementations across the eval hooks (some read
  `memory/sessions/index.json`'s `started` field, one read its `id` field), which had produced
  two unlinked boot records for the same real session.
- Round 2: tracked in `evolutions/.pending-changes.json` as
  `work-20260828-boot-eval-subagent-misattribution` — fixed (a) `eval-agent-start.py` linking
  ANY subagent spawn into whichever single turn-level record happened to be open, with no check
  it was actually a child of that workflow (Knox's sibling fire-and-forget spawns getting merged
  into boot's `subagents[]`), and (b) a lost-completion race where `eval-agent-stop.py` derived
  "the parent" by re-checking which turn record was open at Stop time, and the parent had already
  closed a few seconds before the subagent's own slower SubagentStop hook ran.
- Round 3 (this one): a third, structurally different bug, found by Master in
  `eval-20260828T160656-FE6XZW.json`.

## What was wrong

`FE6XZW` was not a duplicate produced by either of the first two fixes' code paths. It came from
a third, independent eval-record-creation path: `post-tool-use.py`'s `create_eval_record_from_state()`
(the "Cowork path" — fires on any `PostToolUse` write to a workflow's `state.yaml` when
`find_active_eval_record()` can't find/update an active in-progress stub for the session).

That function's only duplicate guard, `find_completed_eval_record()`, checks for an existing
**completed** record for the same workflow + session. It has no check for a **still-open**
turn-level record for that workflow. In this incident:

- `eval-turn-start.py` had already opened `eval-20260828T154249-UQX5N6` for `boot` at
  `15:42:49Z`, correctly, on `UserPromptSubmit`.
- At `16:03:00Z`, a `PostToolUse` write to `workflows/boot/state.yaml` fired.
  `find_active_eval_record()` (no `type` filter, picks the most-recently-started in-progress
  record for the session) picked a newer `type: agent` subagent stub instead of `UQX5N6`.
  `update_eval_record_state_yaml()` correctly declined to overwrite that unrelated stub (existing
  guard from round 1/2 work) and returned `False`.
- That `False` sent execution down the Cowork-path fallback. `find_completed_eval_record()` found
  nothing (UQX5N6 was still in-progress, not completed) and let `create_eval_record_from_state()`
  write a brand-new "completed" `boot` record — `FE6XZW`, `started`/`completed` = 16:03:00Z /
  16:06:56.30Z, `steps: []`, all-null tokens/cost.
- `UQX5N6` itself didn't finalize until `16:07:10.70Z` — 14 seconds *after* `FE6XZW` was written.
  It's a genuine cross-hook race: `PostToolUse` (owns the Cowork fallback) and `Stop`
  (`eval-turn-stop.py`, owns real finalization) are separate async hook processes with no
  ordering guarantee, and the Cowork path's guard only looked at completed records, not
  in-progress ones.

Notably, the existing code already half-suspected this exact case: when `create_eval_record_from_state()`
sees `steps: []` after construction it self-tags the record `phantom-candidate` (alongside
`cowork-hook`) and logs a `[GUARD]` warning — but it still wrote the record instead of skipping
creation outright.

## Root cause, stated plainly

Check-then-act race between two independent hook triggers (`PostToolUse` vs. `Stop`), with a
duplicate guard (`find_completed_eval_record`) scoped too narrowly — it dedupes against
*completed* records only, not against a real turn-level record that is still in-progress and
about to complete on its own via the correct path seconds later.

## Fix

- `systems/eval-harness/hook_utils.py`: added `open_turn_level_record_exists(workflow_name)` —
  the exact in-progress/`monitoring.active` dedup check `eval-turn-start.py` already had
  (`already_open_for_workflow`), now living in one shared place.
- `.claude/hooks/eval-turn-start.py`: `already_open_for_workflow()` is now a thin alias to
  `hook_utils.open_turn_level_record_exists()` — no behavior change, single source of truth.
- `.claude/hooks/post-tool-use.py`: `create_eval_record_from_state()` now has a second guard —
  before writing a Cowork-path record, checks `open_turn_level_record_exists(workflow_name)` and
  backs off (logs `[GUARD]`, returns without writing) if a real turn-level record for this
  workflow is still open. Lets `eval-turn-stop.py` finalize the genuine record instead of racing
  it with a phantom duplicate.

## Disposition of FE6XZW

Genuine duplicate, not a recoverable record (no standalone subagent record exists for this
window with real data to merge in — `UQX5N6` is the complete, correct, already-finalized record
for this exact boot run). Archived to
`systems/eval-harness/runs/_archived/2026-08-28-boot-cowork-phantom/eval-20260828T160656-FE6XZW.json`,
following the same convention as rounds 1 and 2.

## Broader sweep

Scanned every `eval-*.json` under `systems/eval-harness/runs/` with `started` today
(2026-08-28) for `subagents: null` or all-null token/cost fields. Found 10 matches; 9 are
`type: agent` subagent-level records with real, non-null token/cost data (subagents:null is
expected schema for that record type — not a bug) or the one still-`in-progress` record from
this live session. `FE6XZW` was the only record showing the actual bug signature (`type:
workflow`, all-null tokens/cost, self-tagged `phantom-candidate`/`cowork-hook`). No other
workflow was hit by this bug class today — scope is contained to this single incident.

## Tracking

Logged as `work-20260828-boot-eval-cowork-phantom-duplicate` in `evolutions/.pending-changes.json`.

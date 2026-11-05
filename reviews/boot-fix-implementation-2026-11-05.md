# Boot Root-Cause Fixes: Implementation Report

Companion to `reviews/boot-root-cause-2026-11-05.md`. All 10 ranked fixes were approved by David ("make all the fixes right now") and implemented on 2026-11-05. Nothing is committed; all changes are staged-ready in the working tree.

---

## Per-fix status

| # | Fix | Status | Files changed |
|---|-----|--------|---------------|
| 1 | Stale-window guard on the inline attribution path | Implemented | `.claude/hooks/post-tool-use.py` |
| 2 | Restore `started-at` to step-04 + start-of-step stamping in steps 04-08 | Implemented | `workflows/boot/steps/step-04..step-08*.md` |
| 3 | Finders match the `workflow` field (record-step, guardrail-checkpoint, GUARD 2) | Implemented | `systems/eval-harness/record-step.py`, `guardrail-checkpoint.py`, `hook_utils.py` |
| 4 | Error correlation scoped by the error entry's agent | Implemented | `.claude/hooks/post-tool-use.py` |
| 5 | Benign tool failures discriminated from real ones | Implemented | `.claude/hooks/eval-tool-failure.py` |
| 6 | Totals re-aggregated after every parent write (re-attach, backfill, rollup) | Implemented | `.claude/hooks/eval-agent-stop.py` |
| 7 | Step sum-integrity check with partition repair | Implemented | `.claude/hooks/eval-agent-stop.py` |
| 8 | Canonical abort_reason codes | Implemented | `.claude/hooks/eval-turn-stop.py`, `eval-session-end.py`, `tests/test_eval_session_end.py`, `systems/eval-harness/hook_utils.py`, `success-rate.py`, `generate-dashboard.py`, `schema.md` |
| 9 | Cross-session boot record policy (continuation semantics) | Implemented (policy decision below) | `.claude/hooks/eval-turn-start.py` |
| 10 | fetch_plaud.py drops confirmed-404 pending entries; target date processed first | Implemented | `skills/plaud-transcripts/scripts/fetch_plaud.py`, `systems/error-tracking/entries/err-20261104T212704-8DIR4P.json` (fix_status proposed -> applied) |

No fix was blocked. None turned out riskier than the report suggested, though fix 9 required a design ruling (documented below) and carries one named residual.

---

## Design decisions David should know about

### Fix 9: the cross-session policy (the medium-large one)

**Policy: one eval record per logical workflow run, across sessions, via continuation adoption.** IES workflows already have continuation semantics at the workflow layer: state.yaml persists `current-step`, and a session that resumes a dead boot picks up where the old one left off. The eval layer now mirrors that instead of minting a fresh record per session attempt.

Mechanism (all in `eval-turn-start.py`):

- When this hook is about to open a turn-level record for workflow W, it first looks for a **continuable** prior record: same workflow (name or `workflow` field), closed within 24h (`CONTINUATION_WINDOW_HOURS`), closed by a session-lifecycle sweep (`abort_reason` in `SESSION_EXIT_ABORT_REASONS`), not graded, and W's state.yaml still `in-progress` (the run genuinely never finished).
- If found, that record is **reopened and adopted** instead of a new one being opened: `status` back to `in-progress`, `session_id` re-keyed to the new session, `monitoring.active` restored, and a `monitoring.continuations[]` audit entry records the resume (session, time, prior status, prior abort_reason, trigger evidence). The record keeps its original `started`, so the final `duration_seconds` honestly spans the whole logical run including the dead sessions.
- The boot special case also gained a resume branch: a first prompt in a session where boot's state.yaml is still `in-progress` now opens/adopts a record (previously `boot_is_fresh()` returned False for that case and a resumed boot got no turn-level record at all unless the prompt text happened to match a trigger phrase).

Sub-decisions I made (each implemented to the safe side):

1. **A re-run from step-01 in a later session still adopts** the prior mid-run-death record if it is inside the window. Rationale: it is the same boot-day attempt chain; the `continuations` list makes the merge visible; re-executed steps overwrite their prior entries by name. If David wants a top-of-boot re-run to count as a NEW record instead, that is a one-line gate (compare the new run's first step against the prior record's completed steps).
2. **Records with real verdicts are never adopted.** A prior record closed success/failure/partial, or graded (`grading.last_graded` set), is done; the next run gets a fresh record.
3. **Residual gap, flagged honestly:** old-session subagent records keep their old `session_id`. A very late SubagentStop from a dead session resolves its parent by subagents[] membership (still present on the adopted record) or by the orphan re-attach path (session + workflow + window), and the re-attach's session match will no longer hit after re-keying. In practice a dead session's subagents stop before its SessionEnd sweep runs, so this is narrow, but it is the one place the continuation policy can lose a straggler's rollup.

### Fix 5: what counts as benign

Two classes, both evidenced in the window's records: `Read` failures whose text says the file does not exist (the check-then-create probe), and MCP tool failures carrying `NOT_FOUND` (the Outlook fake-folder capability probe). Everything else counts as before. Benign failures are still logged in `tool_failure_log` with a `classification` field and counted in a new `benign_tool_failures` counter, so the audit trail is intact and the finalize rule (`tool_failures > 0 -> partial`) keeps signal without any change to the closers. If David wants a different benign vocabulary (e.g. WebFetch 404s), it is one list in `classify_tool_failure`.

### Fix 8: the code vocabulary

`hook_utils.SESSION_EXIT_ABORT_REASONS = ("session-exit-normal", "session-end-mid-run", "stale-state-open")`, documented in `schema.md`. `session-exit-normal` stays the session-exit sweep's code (it is referenced by CLAUDE.md's exit protocol and existing metrics); the two new codes cover eval-turn-stop's abandoned-record close and stale-evidence close, which previously fell to `unspecified` plus free text. The retired divergent spelling `session-ended` (eval-session-end's inline fallback) now writes the canonical code and remains recognized in historical records by the metric consumers. `success-rate.py` and `generate-dashboard.py` tier all three codes as session-exit class.

### Fix 4: why agent, not session

The error entry's `session` field is an IES label (e.g. `pi-20261104-001`), not a Claude session id, so it cannot be matched against a record's `session_id`. The `agent` field is the causal signal that does match: the error only stamps a record whose workflow family is owned by the error's reporting agent (`workflow_owner_agent`: boot -> master, plaud-ingest -> knox). Entries with no resolvable agent keep the old activity-gated behavior. Known conservative edge: an error reported BY knox ABOUT boot's step-08 will no longer stamp boot's record; the stop-time same-session correlation in eval-agent-stop still catches that class.

---

## Data repairs (fixes 6/7 authorization)

Four records, all 2026-11-04, all repaired in place with an `attribution_integrity` audit block naming `manual-data-repair-2026-11-05 (root-cause fixes 6+7)`:

1. **eval-20261104T211453-019TAZ (boot, the 29.6M record).** Steps 05-08: nulled tokens/cost/duration, relabeled `token_source: stale-window` (their values came from 11-02 started-at stamps sliced over the main transcript; 4 x 1,875,532 = 7.5M phantom tokens). Step-04: filled from its single-step executor (543,220 in / 5,602 out / $0.511, `executed_by_agent_id: a41aec9a162e6511c`, `token_source: subagent-transcript`), started set to the executor's evidenced start 21:27:30Z. Totals re-aggregated: **29,603,073 -> 22,315,836 input tokens** (steps 01-03 inline 1.0M + step-04 excluded via the double-count guard + subagents 21.3M), matching the review's ~22.1M estimate.
2. **eval-20261104T212943-QGM9VB (05-08 briefing subagent).** Its four steps carried the same stale windows sliced over the agent transcript (steps summed 7.13M against a 2.38M run). All four nulled and relabeled `stale-window`; the parent's subagents[] entry keeps the real 2.38M.
3. **eval-20261104T212730-LC6KLO (step-04 executor).** Its own step-04 entry (tokens null, started null) filled with the whole-run attribution, single-step agent rule, labeled `subagent-transcript` with an attribution_note.
4. **eval-20261104T211632-963724 (plaud-ingest, the over-sum).** Steps re-partitioned across its own transcript by started-at order: **step sum 15,939,291 -> 14,839,248, exactly the whole-run total** (the partition invariant). Step-04's overlapping claim no longer double-counts. Status stays `failure` (the err-8DIR4P failure was real).

No other records were touched. Statuses, grades, and controller feedback were not altered anywhere.

---

## Verification performed

- **Existing suites:** all 12 test files in `.claude/hooks/tests/` pass (async-agent recording, attribution heuristics, detect-workflow 32/32, eval-session-end, fully-loaded cost, git gate, ies-git, noop records, secret scanner, skill capture, step token capture, turn-record liveness).
- **Per-fix simulation suite** (40/40 checks, scratchpad, exercising each failure mode):
  - Fix 1: a stale 11-02 started-at against an 11-04 record produces null tokens + `stale-window` + null duration; a fresh window still slices normally (2,000 in over a synthetic transcript); a 23s-early rounding stamp is not flagged (60s tolerance).
  - Fix 3: record-step and guardrail-checkpoint both find a `{name: general-purpose, workflow: plaud-ingest, in-progress}` record; a closed record still never matches; `open_turn_level_record_exists` sees an open agent record and stops seeing it once it is 8h stale.
  - Fix 4: a knox-reported error does not stamp a boot record; a master-reported error does; an agent-less entry keeps the old behavior.
  - Fix 5: both benign classes classified correctly and do not increment `tool_failures`; a real Bash failure still does.
  - Fix 6: aggregate-before/after a late subagent rollup (100 -> 1,000 total).
  - Fix 7: the live repair path re-partitions the reconstructed 963724 over-sum (15,945,291 -> 14,839,248, exact) and stamps the audit trail; an already-consistent record is untouched.
  - Fix 8: success-rate tiers all five codes correctly; both hooks' code lines verified.
  - Fix 9: adoption happy path plus four negative cases (completed workflow, non-session-lifecycle abort, 30h-old closure, graded record) and the first-prompt resume flow end-to-end (prior record adopted, no new record minted).
  - Fix 10: confirmed-gone entry dropped without aborting; transient error keeps the entry without raising; a ready entry is processed and dequeued; main() provably runs the target-date loop before the pending re-check.
- **Harness self-checks:** `workflows/boot/verify/boot-verify.py phase2` passes; `systems/eval-harness/validate-conventions.py` shows no new violations for any edited file (only pre-existing acknowledged size exceptions).
- **The repairs themselves double as fix 6/7 verification** on real records (aggregate_record_totals on 019TAZ; the partition invariant on 963724).

---

## Residual risks

1. **Fix 9 straggler gap** (detailed above): a dead session's very-late subagent stop may miss the re-keyed parent's orphan re-attach (session match). Narrow in practice.
2. **Fix 5 is a policy, not a proof:** a genuine "expected file missing" failure that happens to use a Read probe is now benign-by-classification. The step-output guardrails (state.yaml accumulated-context checks) remain the real detector for that class.
3. **Fix 1 tolerance (60s):** a step legitimately starting more than 60s before its record opens (theoretically possible if a record opens mid-step) would be labeled stale-window. The observed corruption was 2 days; no legitimate case in the window comes within an order of magnitude of 60s.
4. **Fix 3 GUARD 2 agent-branch:** an in-progress agent record for the same workflow now blocks the cowork phantom path for up to `ABANDONED_RECORD_AFTER_HOURS` (6h). A crashed SubagentStop could suppress a legitimate cowork-path record for that window; the turn-start path is unaffected.
5. **Historical records are not rewritten.** Old `partial`/`failure` verdicts caused by the now-fixed mechanisms stand as recorded; only the four authorized 11-04 repairs were made.

## What still needs David's decision

Nothing blocks on David to use any of this. Two optional calls, both one-liners if wanted:

1. **Fix 9 sub-decision:** should a top-of-boot RE-RUN in a later session (state reset, steps 01+ re-executed) count as a continuation of the dead run (current behavior) or as a fresh record? Current behavior optimizes for record-count honesty per boot day; the alternative optimizes for attempt-level attribution.
2. **Fix 5 vocabulary:** the benign classes are Read file-not-found and MCP NOT_FOUND. Add others (e.g. WebFetch 404) or leave as is.

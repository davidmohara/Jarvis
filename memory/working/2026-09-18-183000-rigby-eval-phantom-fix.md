---
type: working
task_id: "session"
session_id: "rigby-2026-09-18-183000"
agent-source: rigby
created: 2026-09-18T18:30:00-05:00
expires: 2026-09-20T18:30:00-05:00
status: active
context: "Rigby capability build: phantom eval-record prevention — 2026-09-18"
---

## What was requested
David: "Make the fix" — prevent phantom eval records after the morning's Tier 3 sweep graded 2 harness artifacts as F. Master diagnosed root cause; Rigby built.

## Root cause (confirmed)
`post-tool-use.py:create_eval_record_from_state` resolved workflow names from a `workflow:` YAML field that boot's state.yaml doesn't have → name "unknown" → both dedupe guards (keyed on name) missed → phantom written on every boot completion. Plus: empty-steps guard tagged-but-wrote, and the orphan sweep ignored cowork-hook stubs (no `monitoring.active`).

## What Rigby changed
- `.claude/hooks/post-tool-use.py`: new `workflow_name_from_path()`/`resolve_workflow_name()` — name derived from `workflows/<name>/state.yaml` path, YAML field now fallback only; records named "unknown" are refused (logged, never written); empty-steps records quarantined to `runs/_phantoms/` with correct names instead of tag-and-write into the main runs dir.
- `.claude/hooks/eval-turn-stop.py`: orphan sweep second pass — cowork-hook in-progress stubs with zero steps/subagents deleted after 2h (delete-don't-archive precedent, err-20260829T161711-3IPMKR).
- Metrics hygiene: `generate-dashboard.py`, `version-trend.py` skip phantom-candidate records; `rigby-eval-grade` SKILL.md excludes phantom-candidate/_phantoms/unknown/zero-activity stubs.
- `assertions/rigby-eval-grade.json`: fixed to match the skill's real deliverable (in-place record updates) — Tier 2 now scores 100% (3/3) vs 72% this morning.
- Tracked as `work-20260918-eval-phantom-guards` in `evolutions/.pending-changes.json`.

## Verification
- py_compile clean; existing suite 26/26 pass.
- Boot replay: GUARD 1 fired on the resolved name "boot", no phantom written, real record 0NC0AY untouched (checksum identical).
- Synthetic no-`workflow:`-field workflow → quarantined with correct name, not "unknown".
- Unresolvable name → refused, logged.
- Orphan sweep: 23h-old stub deleted, 30-min-old stub survived.

## Records deleted (siblings verified first)
PH2FIV (boot phantom), 4A3L9C (dream-cycle), IXSB15 (daily-review), J4EJWW (orphan stub; had finalized success by deletion time).

## Deliberately not done
- Quarantine chosen over hard-skip for empty-steps (preserves the uninstrumented cowork path for diagnosis).
- GUARD 1's session_id scoping NOT widened — daily-review phantom slipped past because close-eval-record.py read a stale session id from the index vs. the hook payload's id. Separate root cause, worth its own entry.
- Master additionally repaired `eval-20260907T080916-ZF09EX.json` (stray `<<<<<<< HEAD` marker from the 09-07 rebase incident) — now valid JSON, close-open-evals runs clean.

Commit: `adc09ccc fix(rigby): stop phantom eval records at creation, sweep, and metrics` (pushed by Master in session wrap).

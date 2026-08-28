---
date: 2026-08-28
session: rigby-boot-eval-consolidation
type: work-summary
tags: [rigby, eval-harness, boot, session-id, hook-bug, capability-fix, bug-fix]
---

# Rigby — boot eval record consolidation + session_id hook fix — Session Summary

## What was done
Today's boot run (session `session-2026-08-28T085856`) produced 7 scattered eval records
instead of one. Consolidated it into a single canonical `eval-20260828T140308-WL89IY`, archived
the 6 redundant/misattributed source records, and fixed the underlying hook bug so this doesn't
recur.

## Root cause (confirmed by reading the hooks, not assuming Master's theory)
Two independent, disagreeing session_id-inference implementations across the eval-harness hooks:

- `hook_utils.infer_session_id()` (used by `eval-turn-start.py`, `eval-turn-stop.py`, and
  `eval-agent-start.py`'s own hand-maintained local copy) read
  `memory/sessions/index.json`'s **`started`** field.
- `post-tool-use.py`'s `get_session_id()` (and `close-eval-record.py`'s
  `current_session_id()`) read the same file's **`id`** field instead.

Both fields exist on recent session records but disagree in format (`2026-08-28T08:58:56...` vs
`session-2026-08-28T085856`). Compounding this, `eval-turn-start.py`'s `UserPromptSubmit` hook
fires before boot's own Session Index step has appended the current session's entry — so at
that exact moment it can read a stale, previously-**unclosed** prior session's record (the Aug 25
17:14:37 session, `closed: null` to this day). That produced:

- `eval-20260828T135817-P00Y9T` — workflow/boot record opened by `eval-turn-start.py`, stamped
  with the stale 3-day-old session_id; its lone `subagents[]` entry was actually Knox's
  plaud-ingest background fork, misattributed as a boot step.
- `eval-20260828T135908-MWOCUW` — the **real** boot-execution subagent (steps 01.2-08, agent_id
  `a1fe36b3241840cf5`, 3,976,036 input / 1,158 output tokens, $1.697209) — orphaned as a
  standalone `type:agent` record because the session_id mismatch meant
  `find_unambiguous_open_turn_record()` never found P00Y9T to link it to.
- `eval-20260828T140308-WL89IY` — a near-empty duplicate workflow/boot record, created by
  `post-tool-use.py`'s `create_eval_record_from_state()` cowork-path fallback when
  `find_active_eval_record()` (using the `id`-format session_id) couldn't find P00Y9T (which had
  the `started`-format session_id) to update instead.
- `eval-20260828T135851-0LKM88`, `eval-20260828T135922-RW2RNP`, `eval-20260828T140547-8SKFKO`,
  `eval-20260828T142027-68E9WF` — all genuinely belong to the separate plaud-ingest /
  plaud-discover-false-positive-fix workflow chain (Knox's background fork from boot step-01 and
  the subsequent Rigby-style dispatch fixing that bug), not to boot's own execution.

Verified via a `claude-code-guide` lookup (not assumed) that Claude Code's hook stdin payload
carries a documented, guaranteed-present, session-stable `session_id` field on every relevant
hook event (UserPromptSubmit, PreToolUse, PostToolUse, SubagentStart, SubagentStop, SessionStart,
SessionEnd, Stop) — `eval-tool-failure.py`'s own prior comment ("this hook doesn't provide it
directly") was simply wrong.

## What changed
- `systems/eval-harness/hook_utils.py`: `infer_session_id()` now takes an optional `payload` and
  prefers the harness-native `session_id` off it directly (no file I/O, no race). Added
  `harness_session_id()` helper. Memory-index fallback (for callers with no payload) now prefers
  `id` over `started`, and the fallback is used only when no payload is available at all.
- `.claude/hooks/eval-turn-start.py`, `.claude/hooks/eval-turn-stop.py`: pass the hook's parsed
  payload into `infer_session_id(payload)`.
- `.claude/hooks/eval-agent-start.py`: deleted the local hand-maintained `infer_session_id()`
  copy; delegates to `hook_utils.infer_session_id(payload)`.
- `.claude/hooks/post-tool-use.py`: `get_session_id()` now prefers the harness-native session_id
  via `hook_utils.infer_session_id(payload)` before falling back to the memory index. Also
  hardened `update_eval_record_state_yaml()`'s overwrite guard to decline touching a
  `type:"agent"` stub too (previously only declined on a disagreeing `type:"workflow"` name) —
  a latent mislabeling risk that gets *more* likely, not less, now that every hook-opened record
  in a session shares one true session_id.
- `.claude/hooks/eval-tool-failure.py`: scopes its "most recent in-progress record" lookup to the
  failing tool call's own session_id (present on the payload) before falling back to the old
  unscoped global scan.
- `systems/eval-harness/schema.md`: documented the harness-native-payload source of truth for
  `session_id` on hook-opened records vs. the memory-index fallback for CLI-invoked ones.

## Consolidation
Canonical record: `systems/eval-harness/runs/eval-20260828T140308-WL89IY.json`.
- status: success. started `13:58:56.392400Z`, completed `14:03:53.139820Z` (MWOCUW's real
  completion — the latest genuine boot-execution timestamp), duration 296.75s.
- `subagents[]`: one entry, the real boot-execution subagent (`a1fe36b3241840cf5`) with its real
  token/cost data.
- `total_tokens_input` 3,976,036 / `total_tokens_output` 1,158 / `total_cost_usd` $1.697209 —
  MWOCUW's real figures, re-derived and cross-checked before archiving anything.
- Guardrail entry (`pre-completion-review`, pass) and the one real tool failure (`Read`, file not
  found) merged in from P00Y9T. `boot-004-guardrail-checkpoint-ran` assertion now correctly
  passes (was failing on WL89IY before the guardrails array existed on it).
- `related_records` field: the real Knox plaud-ingest fork noted by reference (not merged — it's
  a genuinely separate workflow with its own eval trail), plus the 3 other plaud-ingest/
  plaud-discover-fix records noted the same way.

Archived (not deleted, for audit trail) to
`systems/eval-harness/runs/_archived/2026-08-28-boot-consolidation/`:
P00Y9T, 0LKM88, MWOCUW, RW2RNP, 8SKFKO, 68E9WF. All consumers glob `runs/eval-*.json`
non-recursively, so archived files no longer surface in any dashboard/analysis tooling.

**Confirmed untouched:** all Aug 25 and Aug 27 eval records — out of scope for this cleanup,
verified still present in `systems/eval-harness/runs/` after the archive move.

Tracked in `evolutions/.pending-changes.json` as
`work-20260828-boot-eval-session-id-consolidation`.

## Outstanding / not done
- Did not execute a live end-to-end boot run to observe the fix produce exactly one record in
  practice — that will only be visible on tomorrow's boot. Verified by direct smoke-test of
  `hook_utils.infer_session_id()` (with/without a payload) and `py_compile` on every touched file.
- Did not touch the still-open Aug 25 17:14:37 session entry in `memory/sessions/index.json`
  (`closed: null`) that made the stale-session-id race possible in the first place — the
  harness-native session_id fix makes this moot for hook-triggered records regardless, and
  closing that entry is a memory-system housekeeping question, not an eval-harness bug, so left
  alone pending Master's/David's call.
- Did not commit. Per `skills/git/SKILL.md`, all git ops go through that skill; flagging here so
  whoever runs it next includes: the 6 hook/utility files, `systems/eval-harness/schema.md`,
  `evolutions/.pending-changes.json`, the consolidated `WL89IY` record, and the archive move.

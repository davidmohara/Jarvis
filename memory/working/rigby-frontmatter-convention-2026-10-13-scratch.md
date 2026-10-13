# Rigby scratch — step-frontmatter minimal-schema change (2026-10-13)

## DONE
- Swept 291 `workflows/*/steps/*.md` frontmatter to minimal schema (status/started-at/completed-at [+ static keys model/step/name/workflow kept]). Stripped: outputs (291), prior-run-2026-10-09 (7), prior-run-2026-10-08-archived (1), approved-followup-2026-09-15 (1, dream-cycle step-04 — canonical copy lives in dream-cycle state.yaml accumulated-context.step-04-2026-09-15-approved-followup), prior-cycle-approved-followup (1, same).
- Rewrote step-body instructions (YOUR TASK etc.) pointing executors at state.yaml accumulated-context instead of frontmatter outputs; removed obsolete frontmatter-mirror fenced examples (22 files); relabeled bare `outputs:` schema blocks to `# state.yaml -> accumulated-context`.
- Residual sweep: 0 bad references left (watchtower config.yaml `outputs.*` refs intentionally untouched — config schema, not step frontmatter).
- Updated `reference/workflow-conventions.md` (minimal schema; removed traceability sentence).
- Updated `agents/rigby.md` step-file frontmatter template (removed `outputs: {}`).
- Updated `specs/Workflow State Tracking Plan.md` (Change 2 + Section B quote).
- Adapted `.claude/hooks/step-complete.py`: added `load_step_outputs()` reading state.yaml accumulated-context; legacy fallback + generate_retry_instruction now reference state.yaml, not frontmatter. Syntax-checked OK.

## IMPACT FINDINGS
- `assertion_checks.py` `expected_outputs_written`/`outputs_non_empty`: derived from file_exists/file_min_bytes assertions — NOT step frontmatter. No change.
- `.claude/skills/rigby-capability-build/scripts/generate_review.py`: "outputs/" = run workspace dir. Unrelated. No change.
- eval hooks (post-tool-use, eval-agent-start/stop, eval-turn-start): same field names, populated from assertions. No change.
- Guardrail JSONs with check_field rules: 9 files, all in workflows/boot/guardrails/. Field checks now resolve against accumulated-context via step-complete.py change; retry_instruction TEXTS still mention "outputs" — cosmetic update pending.
- 26 verify scripts read step-frontmatter outputs — ADAPTATION IN PROGRESS (see below).

## DONE (continued)
- Created `systems/eval-harness/step_outputs.py` (shared loader: deep-search accumulated-context by expected keys).
- Patched 28 verify scripts (dream-cycle x5, watchtower x14, daily-review x2, golf-booking x3, client-meeting-prep step-01, talking-points step-02, shutdown-cleanup step-04, plus upstream-read sites in watchtower daily-05/06, weekly-04/05). All verify scripts parse; loader functional test passes against live dream-cycle state.yaml (dated keys resolve, most-recent-first on ties).
- Guardrail JSON: boot step-02 retry text updated; step-06.5's "outputs" is generic English (briefing content) — untouched.
- Evolution logged: evolutions/.pending-changes.json entry `work-20261013-step-frontmatter-minimal-schema` (329 files).
- Error entry err-20261013T151635-DORL18: fix_status -> applied with fix_applied note.
- Final sweep: 0 step files with run-data frontmatter keys; all JSON valid; all verify scripts parse.

## TASK COMPLETE — report delivered via SubagentHandback.

## NOT IN SCOPE / NOTES
- projects/ai-certification/* copies are a separate certification project — untouched.
- watchtower config.yaml has its own `outputs:` config section — references to `config.yaml -> outputs.*` preserved.
- No commits (skills/git only when David asks).

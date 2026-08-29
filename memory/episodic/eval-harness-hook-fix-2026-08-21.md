---
type: working-archive
task_id: "session"
session_id: "5dcfee22-ff31-47ff-a35c-90ecbfbf17fb"
agent-source: master
created: 2026-08-21T20:30:00
expires: 2026-08-23T20:30:00
status: archived
context: "Eval-harness PostToolUse hook root-cause fix — 2026-08-21"
date: 2026-08-21
source_file: memory/working/eval-harness-hook-fix-2026-08-21.md
tags:
  - eval-harness
  - master
  - bug-fix
  - hook
  - dream-cycle
  - boot
  - watchtower
  - cost-tracking
related_people: []
  promoted: false
  last-promoted-check: 2026-08-25
  last-promoted-check: 2026-08-26
  last-promoted-check: 2026-08-27
  last-promoted-check: 2026-08-28
salience:
  score: 0
  last-promoted-check: 2026-08-29
---

# Eval-Harness Hook Fix — August 21, 2026

## Summary

Built out AI-workflow infrastructure (guardrail checkpoints, token/cost tracking, sentinel assertion files) across daily-review, morning-briefing/boot, watchtower, dream-cycle, and system-eval. While chasing why `boot`/`watchtower` never produce a properly-named eval record, found and fixed the actual root cause.

## Critical Finding

`.claude/settings.json` never registered a `PostToolUse` hook at all — `post-tool-use.py` (the script responsible for populating eval records from state.yaml/step-frontmatter writes) had never fired once, for any workflow, in any session, ever. This — not a naming-logic bug — is why `boot` and `watchtower` never got named eval records. Registered the hook (`Edit|Write` matcher).

That surfaced a second real bug: `create_eval_record_from_state()` and `create_eval_record_from_skill_run()` crashed on `can't subtract offset-naive and offset-aware datetimes` whenever a workflow's `session-started` lacked a UTC offset (exactly how `boot/state.yaml` writes it) — silently swallowed by a broad except, so nothing ever got written or logged clearly. Fixed both call sites to treat naive timestamps as UTC. Verified end-to-end with a controlled synthetic payload (created a correct, assertion-passing `boot` record; deleted it since it wasn't from a genuine hook firing).

Per direct instruction, reverted the markdown-instruction workarounds I'd initially added to boot/watchtower step files (telling the agent to call `new-eval.py`/`close-eval-record.py` directly) — that pattern depends on the model reliably following instructions every run, which is exactly the failure mode hooks exist to avoid. The registered hook + datetime fix is the real, deterministic fix. `dream-cycle`'s direct call to `close-eval-record.py` stays, since that one lives in actual Python code (`orchestrate.py`), not a prompt instruction.

## Cost/Token Backfill Finding

Reviewed all 52 `daily-review` eval records for real $ cost data per the Stage 4 audit-trail requirement. Concluded backfill is not possible for any of them: all run under `agent: chief` (Cowork runtime, which doesn't write to the local Claude Code session transcripts I can read), and 51 of 52 store a zero-width `started == completed` instant rather than a real execution window, so there's no window to slice even hypothetically. Declined to fabricate numbers. 22 unrelated `type: agent` records already have genuine, correctly-computed cost data (proving the pricing mechanism itself works) — those just aren't daily-review.

## State Changed

- `.claude/settings.json` — added `PostToolUse` hook registration
- `.claude/hooks/post-tool-use.py` — fixed naive/aware datetime crash in two functions
- `systems/eval-harness/schema.md` — `cost_usd` reclassified from informational to required (per correction — Stage 4 does require $ cost)
- Reverted markdown eval-open/close instructions from `workflows/boot/steps/step-01-load-context.md`, `step-07-verify-completion.md`, and `workflows/watchtower/steps/daily-step-01-gather.md`, `daily-step-06-report.md`, `weekly-step-01-synthesize.md`, `weekly-step-05-report.md`

## Open Item

Cowork's own token/cost logging (if any) is a separate, larger question — not solvable from the local Claude Code session transcripts. Would need to know whether Cowork exposes any usage log at all before daily-review can ever get real per-run cost data for its historical (chief-run) executions.

---
type: working-archive
task_id: "session"
session_id: "rigby-2026-10-26-boot-token-fixes"
agent-source: rigby
created: 2026-10-26T16:30:00Z
expires: 2026-10-28T16:30:00Z
status: archived
context: "Impact analysis for the five boot token-performance fixes — 2026-10-26"
date: 2026-10-26
source_file: memory/working/rigby-impact-2026-10-26-boot-token-fixes.md
tags:
  - rigby
  - briefing
  - plaud
  - boot
  - dream-cycle
  - knox
related_people:
salience:
  score: 9
  last-promoted-check: 2026-10-30
  promoted: true
---

# Impact Analysis — Boot Token-Performance Fixes (2026-10-26)

Targets: `workflows/boot/workflow.md`, `workflows/boot/verify/boot-verify.py`,
`reference/state-check-protocol.md`, `workflows/boot/state.yaml`,
`workflows/plaud-ingest/workflow.md`,
`workflows/boot/steps/step-04.5-watchtower-daily-handoff.md`,
`workflows/watchtower/workflow.md`.

## `workflows/boot/workflow.md`
- `CLAUDE.md:14` — boot entrypoint ("Read and follow ... in full").
- `agents/routing.md:30` — cites boot's inline step-01 exception.
- `workflows/boot/workflow.md` itself: spawn briefs for 01.5/01.2/02/03/04/04.5 and the 05-08 dispatch rely on the literal path string for eval attribution.
- `.claude/hooks/eval-turn-start.py:184`, `.claude/hooks/tests/test_detect_workflow.py:40` — path-based workflow detection.
- **Caution:** the literal `workflows/boot/workflow.md` string in every spawn brief is load-bearing for per-step attribution. Do not remove or reword it.

## `workflows/boot/verify/boot-verify.py`
- `workflows/boot/workflow.md:81,118,123,126` — step-03 and step-07 invoke `phase2` / `completion`.
- `workflows/boot/steps/step-03-verify-phase2.md:33`, `step-07-verify-completion.md:33,71` — invocation and crash fallback.
- `workflows/boot/state.yaml:279,315` — prior `steps_verified` notes reference it.
- No other workflow calls it. Safe to extend the `completion` subcommand; keep `phase2` behavior unchanged.

## `reference/state-check-protocol.md`
- Referenced by 35+ `workflows/*/workflow.md` STATE CHECK pointers (boot, watchtower, plaud-ingest, daily-review, dream-cycle, all verification workflows, etc.).
- **Caution:** a blanket "clear accumulated-context on fresh run" would break workflows whose STATE CHECK Variant declares persistent accumulated-context keys (notably watchtower's append-only `content_queue`, `obsidian_write_method`). The edit must carve out Variant-declared persistent keys.

## `workflows/boot/state.yaml`
- `skills/boot-context-analyzer/SKILL.md:37,38,43,104,207` — reads/measures boot state.
- `workflows/boot/verify/step-07-verify-completion.py` — asserts status complete.
- `.claude/hooks/eval-turn-start.py:253` — reads boot state to detect an imminent boot.
- `workflows/daily-review-verification/state.yaml` — historical references only.
- Post-boot, safe to clean. Keep the keys those consumers read: `status`, `session-id`, `session-started`, `completed-at`, `accumulated-context`.

## `workflows/plaud-ingest/workflow.md`
- `SYSTEM.md:142` — canonical Knox dispatch prompt.
- `workflows/boot/steps/step-01-load-context.md:29` — fire-and-forget spawn.
- `skills/plaud-discover/SKILL.md:254` — references step-01.
- `evolution.manifest.json:73` — listed as a component file.
- `workflows/plaud-ingest/state.yaml` — run state.
- **Caution:** the TOKEN PRE-CHECK PROHIBITION is load-bearing (err-20260730T143152-S0TRMO). Any preflight must never abort on a missing token file and must fall through to the full run on any uncertainty.

## `workflows/boot/steps/step-04.5-watchtower-daily-handoff.md`
- `workflows/boot/workflow.md:97,120` — spawn brief and steps table.
- `workflows/boot/steps/step-04-gather-meeting-context.md:74,103` — current-step pointer and return text.
- `workflows/watchtower/workflow.md:27` — names it as a daily invocation point.
- Safe to extend; keep the `watchtower_output` contract intact (step-05 renders it).

## `workflows/watchtower/workflow.md`
- `workflows/morning-briefing/workflow.md:64` — standalone briefing invocation.
- `workflows/boot/workflow.md:97` — boot step-04.5 invocation.
- `workflows/boot/steps/step-04.5-watchtower-daily-handoff.md:12,48` — hand-off contract.
- **Caution:** watchtower daily/weekly share one state.yaml; the STATE CHECK Variant forbids clearing `accumulated-context`. Adding an eval-record lifecycle must not touch that rule.

---
Proceed with caution: all seven targets have live dependents. Edits are additive/contract-preserving.

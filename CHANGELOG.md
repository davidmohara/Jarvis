# Changelog

All notable changes to IES (Improving Executive System). Versions were established retroactively on 2026-10-08 from git history (1,063 commits since 2026-02-05) to give the Stage 5 certification submission a formal release record. Tags mark stable points; dated entries summarize the dominant work of each era with representative commits.

## [Unreleased] — Stage 5 certification remediation (in flight, started 2026-10-08)

- Remediation plan approved and tracked locally: `projects/stage5-certification-remediation.md` (Tim Rayburn's examination report returned FAIL 2026-10-07; 9 findings, all mapped to phases).
- Phase 0 complete: workflow rationalization memo (`projects/workflow-rationalization-memo-2026-10-08.md`); Stage 4 candidate set rationalized to boot, morning-briefing, daily-review, plaud-ingest; weekly-review dropped.
- Phase 1 in flight: coordinator purity refactor (spawn-first enforcement, no direct git/shell/domain execution by the coordinator).
- Phase 2 in flight: per-step audit trail in the eval harness (per-step model, input tokens, output tokens, cost) with CSV/JSON export.
- Phase 3 in flight: Stage 3 evaluation artifacts for all 11 agents (`systems/eval-harness/stage3/`).
- Phase 5C (this file): CHANGELOG established, retroactive version tags created.
- Planned: v2.0.0 tagged at the Stage 5 resubmission.

## [v1.5.0] — 2026-09-16: access consolidation and deterministic grading

- OmniFocus access consolidated onto two skills (`omnifocus-data`, `omnifocus-tasks`) with the osascript fallback path verified end-to-end (6aeb691d, eb6eec1f).
- Deterministic Tier 2 grading on every skill invocation (3068d935) and per-turn token breakdown in daily-cost-check (5f7c283e).
- Reusable skills: schema-validator, delivery-router (c6da964c); calendar-handler, visual-verification (eda9d815).
- Golf skills converted to workflows with quality gates (628983a4).

## [v1.0.0] — 2026-08-22: Stage 4 certification build

- Guardrail checkpoints with real audit trail and sentinel files across workflows (a3acd571); Stage 4 boot system complete and production ready (4ee4e3a6).
- Eval-hook lifecycle rebuilt with intelligent retry behavior for guardrail checkpoints (2393b9a0, e9887470).
- Ground-truth verifier scripts and workflow-specific verifier dispatcher across 13 workflows (a562eaeb, 53bc7d23); guardrail output-field contracts documented in boot step frontmatter (ce9b61d0).
- Podcast-to-Pipeline campaign system (aedc13de); token efficiency optimizations, 8 consolidation improvements (2220912a).

## [v0.5.0] — 2026-06-19: system hardening and standing intelligence

- Git operations skill established as the only authorized path for all git operations (03967217).
- Two-tier skill architecture, stubs, model pins, SessionStart hook, release watch audit (55452fdb).
- Watchtower standing intelligence workflow (b853978f); both-sides political news monitor (a9876a8b).
- Routing hard stops with lazy-loaded routing.md and pre-action hook (a55b68b4, 2026-05-04).
- Session continuity index system (6866ea1d, 2026-05-08); automated content generation from Slack to Ghost (94745b6c).

## [v0.1.0] — 2026-02-05: initial system

- Initial commit: Executive Operating System (50cbe123); Jarvis identity, context, and boot sequence (6f61209c).
- OmniFocus integration with person-tag conventions (2110e68b, db0f5a59).
- Agent roster grew through spring: Sterling (2026-03-27), Galen with WHOOP integration (2026-04-01), tiered memory with dream cycle and skill manifest (2026-04-18).

---

Tag map (annotated tags on the listed commits): v0.1.0 → 50cbe123 · v0.5.0 → 55452fdb · v1.0.0 → 4ee4e3a6 · v1.5.0 → 6aeb691d · v2.0.0 → planned at Stage 5 resubmission.

# Working Memory: Stage 5 Certification Remediation (2026-10-08)

Tim Rayburn's Stage 5 exam (Teams, 2026-10-07) returned FAIL with 9 findings. Same day: remediation plan approved (projects/stage5-certification-remediation.md, local tracking only per David, no OmniFocus), and phases 0-5 plus hardening were built. All 9 findings now have evidence; the remaining work is the ~10-day instrumented data window and Phase 6 assembly.

## Decisions made (David)

- Stage 4 candidate set rationalized to the 4 actually-used workflows (boot, morning-briefing, daily-review, plaud-ingest); weekly-review dropped (0 eval records ever).
- Stage 3 scope: all 11 agents, candidate-step owners first. Naming rules: Ralph IS an agent (boot verification, agents/ralph.md); David is the human operator, never an agent; Jarvis is the Master agent itself.
- Local tracking only (no OmniFocus mirror for this effort).
- Git hardening: wrapper + transparent redirect approved; secrets-scan allowlist for fake-by-construction test fixtures approved.
- Push integration on the OneDrive-synced repo: David's terminal (agent commits locally, hands pull/push over on divergence).

## Built (commit 2b747e6a, plus 7a6dcb3f wrap-up)

- Phase 0: projects/workflow-rationalization-memo-2026-10-08.md (usage matrix, 34 zero-use workflow dirs, 7 consolidation candidates flagged).
- Phase 1: coordinator purity refactor (42 files, spawn-first Hard Stops, ies-channel.py subprocess fix, 4 remediation error entries).
- Phase 2: per-step audit trail (step_audit.py, export-step-audit.py, owning_agent attribution, merge-on-close fix, abort_reason guarantee, token_source provenance).
- Phase 3: systems/eval-harness/stage3/<agent>.md x11 with honest measured results and repro commands. Threshold gaps: chief, harper, knox, rigby below their own bars; ralph, galen, shep, quinn, sterling, chase need first instrumented runs.
- Phase 4A: deterministic per-step verifiers confirmed/wired for all 4 candidates; boot 06.5 made machine-checked; Ralph verification sub-workflows for all 4 (workflows/*-verification/). Honest limit: verifiers fire at subagent completion, not mid-run; in-step guardrail-checkpoint calls are the mid-run gates.
- Phase 4B: bypass tests BT-01..04; two real holes found in guardrail-checkpoint.py (case-variant escalate misrecord; unrecordable escalate dropped), both fixed and re-tested closed-loop (BT-02-fix-verification).
- Phase 4C baseline: daily-review 98%, morning-briefing 94% (28% strict was a status-labeling artifact), boot 75%, plaud-ingest ~89% pending no-op verification (projects/stage-4-evidence/success-rate-baseline-2026-10-08.*).
- Phase 5: agents/manifest.md, agents/adversarial-isolation.md, CHANGELOG.md + tags v0.1.0/v0.5.0/v1.0.0/v1.5.0 (v2.0.0 at resubmission).
- Hardening: git-gate (PreToolUse updatedInput transparent rewrite of raw git writes onto skills/git/scripts/ies-git) + wrapper (atomic, status refusal, destructive policy, commit lint, gated-dirs --ack-gated, secrets scan + allowlist, git-ops.jsonl audit of every op and refusal). Empirical: updatedInput must be minimal-shape {"command": ...}; full tool_input is silently ignored (err-20261008T210353-9XIRVF). Exit-2 blocking and JSON deny both honored. Hook edits propagate with OneDrive lag (probe after editing).
- Live punch-outs to David during the session: secrets-scan refusals x2 (allowlist approved), git-latest.json conflict resolution, stuck-rebase handoff (err-20261008T222241-UHTK59).

## Pending (data window, ~Oct 9-27)

- 3-5 instrumented runs per candidate workflow (token_source=windowed), export to systems/eval-harness/audit-exports/.
- Success-rate recompute restricted to instrumented runs; verify 18 unexplained aborts (boot 7, plaud-ingest 11).
- Fresh measured runs to close Stage 3 threshold gaps (see stage3 artifacts' gap lists).
- Adversarial catch examples accumulating structurally (assertions boot-004/morning-008/daily-007/plaud-002).
- Phase 6: evidence bundle per projects/stage-5-submission/index.md (cover note points 1-7 drafted there), v2.0.0 tag, resubmit to Tim via Teams.

## Systemic notes

- OneDrive-synced .git: multi-step git (pull --rebase) races with cross-machine sync and live hooks; single-op wrapper commits are fine, integration belongs in David's terminal.
- Harness agent-field attribution was polluted (general-purpose 471 records, master/jarvis split); step-level owning_agent now records truth going forward; historical records intentionally not rewritten.
- OmniFocus MCP server failed to connect this session (moot; local tracking chosen).

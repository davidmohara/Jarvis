# Stage 5 Certification Remediation Plan

**Status:** approved 2026-10-08 · **Owner:** Rigby (system work), Chief (data collection) · **Target:** resubmission ~3 weeks from kickoff
**Tracking:** local only, this document is the tracker (David's decision 2026-10-08: no OmniFocus mirror)
**Source:** Tim Rayburn's Stage 5 Certification Examination Report (Teams, 2026-10-07): FAIL. Verdict: real, sophisticated system; gaps are in evidence collection and formalization, not design.

## Phase tracker

| Phase | Work | Status | Due |
|-------|------|--------|-----|
| 0 | Workflow rationalization memo | complete 2026-10-08 (`projects/workflow-rationalization-memo-2026-10-08.md`) | 2026-10-09 |
| 1 | Coordinator purity refactor | complete 2026-10-08 (remediation entries `err-20261008T195835-EW45PB`, `err-20261008T195836-0BTS1J`, `err-20261008T195836-NN86G2`, `err-20261008T195836-X3VV9S`; fixed `systems/ies-channel/ies-channel.py`, `agents/master.md`, `agents/routing.md`, and all step files + workflow.md of boot, morning-briefing, daily-review, plaud-ingest) | 2026-10-14 |
| 2 | Per-step audit trail instrumentation | in-progress 2026-10-08: instrumentation landed (step_audit.py, export-step-audit.py, hardened record-step.py/close-eval-record.py/step-complete.py/post-tool-use.py/eval-agent-stop.py/eval-turn-stop.py; per-step model/tokens/cost + owning_agent captured; CSV/JSON export working). Remaining: 3-5 real instrumented executions per candidate workflow (boot, morning-briefing, daily-review, plaud-ingest) as the data-collection window. | 2026-10-16 |
| 3 | Stage 3 artifacts, all 11 agents | in-progress 2026-10-08 (artifacts drafted for 11 of 11 agents in `systems/eval-harness/stage3/`; measurement gaps listed in each artifact) | 2026-10-23 |
| 4 | Stage 4 evidence (guardrails, bypass tests, success rate) | 4A complete 2026-10-08: deterministic per-step verifiers (`workflows/<wf>/verify/*.py`, dispatched by `.claude/hooks/step-complete.py`) confirmed for every step of all 4 workflows; boot step-06.5 made machine-checked; adversarial verification wired for morning-briefing step-05, daily-review step-03c, plaud-ingest step-06 (Ralph + per-workflow lenses in `workflows/*-verification/`, recorded as `adversarial-verification` guardrails; assertions morning-008/daily-007/plaud-002); boot-verification refreshed to post-refactor boot. 4B complete 2026-10-08 (4 punch-out bypass tests in `projects/stage-4-evidence/bypass-tests/` with per-test logs + index README: BT-01 max-retries PASS, BT-02 escalation-bypass FAIL with 2 holes in `guardrail-checkpoint.py`, BT-03/BT-04 documented as procedural-only enforcement). 4C baseline complete 2026-10-08 (`projects/stage-4-evidence/success-rate-baseline-2026-10-08.{md,csv}`: daily-review 78%, plaud-ingest 48%, boot 36%, morning-briefing 28%); 4C data window pending. | 2026-10-27 |
| 5 | Stage 5 formalization (manifest, isolation doc, CHANGELOG/tags) | complete 2026-10-08: 5A `agents/manifest.md` (11 agents + David as human operator + shutdown-cleanup ownership reconciled to Rigby); 5B `agents/adversarial-isolation.md` (isolation mechanics, Ralph coverage, per-workflow adversarial wiring now live per Phase 4A); 5C CHANGELOG.md + tags v0.1.0/v0.5.0/v1.0.0/v1.5.0 (v2.0.0 planned at resubmission) | 2026-10-28 |
| 6 | Assemble bundle + resubmit to Tim | not started | 2026-10-30 |

**Compliance addendum (2026-10-08, David-directed):** shutdown-cleanup (the session-exit workflow, not a Stage 4 candidate) was brought to the full candidate instrumentation standard: all step Agent lines corrected to Rigby-spawned, both `git status` instructions replaced with lock-free lists, step-04 commit routed through the ies-git wrapper with a push-handoff rule for divergence (`err-20261008T222241-UHTK59`), new step-05 adversarial verification spawning Ralph (`workflows/shutdown-cleanup-verification/`, cleanup-claims-vs-commit-and-audit-trail lens), verifiers for all 5 steps (step-04's window-checked against `git-ops.jsonl`, both directions tested), guardrail checkpoint definition, and assertion `shutdown-005`. Covered in `agents/adversarial-isolation.md` and the submission index.

## Locked decisions

- **Candidate set rationalized to the 4 actually-used workflows**: boot, morning-briefing, daily-review, plaud-ingest. weekly-review dropped (0 eval records ever, never-started state.yaml). Cover note to Tim explains this.
- **Stage 3 scope: all 11 agents**, prioritized by candidate-workflow step ownership: Jarvis (Master/coordinator), Chief, Knox, Rigby, Ralph first; then Chase, Shep, Quinn, Harper, Sterling, Galen.
- **Naming rules** (correcting the report's misreads): Ralph is an agent (boot verification). David is not an agent, he is the human operator/controller. Jarvis is the Master agent, not a separate agent from Master.
- **Full coordinator purity refactor**, not just the 3 cited violations.
- **Speed over Tim's 6-8 week estimate**: compressed ~3 weeks, parallel tracks.

## Gap traceability (Tim's 9 findings → phases)

| # | Finding | Closed by |
|---|---------|-----------|
| 1 | Guardrails incomplete / not adversarial | Phase 4A |
| 2 | Punch-out mechanisms not bypass-tested | Phase 4B |
| 3 | No end-to-end success rate for any workflow | Phase 4C |
| 4 | Per-step token/cost audit trail missing | Phase 2 |
| 5 | No Stage 3 artifacts for component agents | Phase 3 |
| 6 | Coordinator purity violations | Phase 1 |
| 7 | No formal agent manifest / scoping | Phase 5A |
| 8 | Adversarial review isolation undocumented | Phase 5B |
| 9 | No CHANGELOG / tags / release history | Phase 5C |

## Existing infrastructure to reuse (do not rebuild)

- `systems/eval-harness/` — live harness: `assertion_checks.py`, `guardrail-checkpoint.py`, `close-eval-record.py`, `add-step-tracking.py`, `backfill-all-eval-costs.py`, `daily-cost-check.py`, `budget.json`, `grading/`. Records in `systems/eval-harness/runs/*.json` already carry `assessment` and `total_cost_usd`; the missing piece is **step-level** detail.
- Existing run data to mine: boot 45 records, daily-review 58, plaud-ingest 31, morning-briefing 18.
- Cited violation evidence: `systems/error-tracking/entries/err-20260611T113806-g0pfoq.json`, `err-20260716T220729-FNAAP8.json`.
- `workflows/boot-verification/` — Ralph's existing boot verification workflow (stale, refresh not rebuild).
- Git operations via `skills/git/SKILL.md`; OmniFocus task creation via `skills/omnifocus-tasks/SKILL.md`.

## Phases

### Phase 0: Workflow rationalization memo (1 session, Rigby)
Usage matrix for all 58 workflow dirs (eval-record recency, state.yaml, scheduled-task references). Short memo: candidate set = the 4 active workflows, weekly-review dropped, overlap consolidations flagged for later (morning-briefing vs boot step-05, daily-review vs shutdown-cleanup, client-meeting-prep vs calendar-prep). Consolidation noted, not blocking.

### Phase 1: Coordinator purity refactor (2-3 sessions, Rigby)
Audit `agents/master.md`, `agents/routing.md`, and every step file of the 4 candidates for direct-execution paths. Fix:
- `systems/ies-channel/ies-channel.py:145` subprocess call (move capability check out of coordinator path).
- Direct git ops → route through `skills/git/SKILL.md` (Rigby).
- Direct plaud staging checks → spawn Knox.
- Rewrite step language so every step spawns a named sub-agent; no manual model invocation by the coordinator.
Remediation log entry per fix ("git operations moved from coordinator to Rigby skill"), in error-tracking format, citing the original violation entries.

### Phase 2: Per-step audit trail (2 sessions + data window, Rigby)
Extend the eval harness so each step of an instrumented run records: model name, input tokens, output tokens, cost. Reuse `add-step-tracking.py`, the turn hooks, and `backfill-all-eval-costs.py`; extend `close-eval-record.py`. Capture 3-5 fully instrumented real executions per candidate workflow. Export per-step CSV/JSON.

### Phase 3: Stage 3 artifacts for all agents (parallel, 1-2 weeks, Rigby + Chief)
For each of the 11 agents (candidate-step owners first):
- Prompt definition (from `agents/*.md`).
- ≥3 named quality criteria with pass/fail thresholds.
- Measured results: X% pass on Y real executions, mined from existing eval records plus fresh runs.
- ≥2 iterations showing baseline → hypothesis → change → measured improvement (reconstruct from error log + eval history; fresh A/B where history is thin).
Artifacts land in `systems/eval-harness/stage3/<agent>.md` with evidence links.

### Phase 4: Stage 4 evidence per candidate workflow (data window, ~10 days floor)
- **4A Guardrails**: wire deterministic hooks (`guardrail-checkpoint.py`, `assertion_checks.py`) at every step transition of all 4 workflows. Manual-review checkpoints become hook-enforced. Adversarial agent with a distinct lens at each transition: Ralph for boot (refresh `workflows/boot-verification/`); define adversarial agents for the other three (e.g., daily-review output vs source data cross-check; morning-briefing calendar/email cross-check).
- **4B Punch-out bypass tests**: deliberately trigger max-retries, attempt to bypass escalation, attempt coordinator-direct execution; verify the system blocks each; save test logs as evidence.
- **4C Success rate**: composite completion metric over 10+ runs per workflow. Mine existing records where status data is complete; count forward with instrumented runs. Report as "X% of runs completed all steps successfully."

### Phase 5: Stage 5 formalization (1-2 sessions, Rigby)
- **5A Agent manifest**: table of every agent (Jarvis as Master/coordinator, plus Chief, Chase, Knox, Shep, Quinn, Harper, Rigby, Sterling, Galen, Ralph), role, owned workflow steps, distinct capabilities, boundaries, conflict resolution. Explicitly list the human operator (David, controller/punch-out target) as a non-agent participant.
- **5B Adversarial isolation doc**: how adversarial agents (Ralph et al.) are invoked (separate spawn, fresh context, no shared production context), what they check that producing agents don't, plus evidence of issues caught in real runs.
- **5C Version control**: `CHANGELOG.md` at repo root + git tags (v1.0 → v2.0 style) derived from git history, via `skills/git/SKILL.md`.

### Phase 6: Assemble and resubmit (1 session, Harper for cover note)
Evidence bundle structured 1:1 against Tim's 9 findings plus his strengths list. Cover note explains the 4-not-5 candidate rationalization and corrects the report's naming misreads (David is the human operator, not an agent; Jarvis is the Master agent itself). Deliver to Tim via Teams.

## Critical path and timing

Phase 2 instrumentation feeds Phase 4 data collection: 10 daily-cadence runs ≈ 10 calendar days, starting the day Phase 2 lands. Phases 1, 3, and 5 run parallel to the data window. Compressed total: **~3 weeks from kickoff**.

## Verification

- Each phase produces a checkable artifact (memo, remediation log, instrumented run records, stage3 files, bypass test logs, success-rate CSV, manifest, CHANGELOG).
- Pre-submission self-audit: walk Tim's 9 findings one by one and confirm the bundle contains evidence for each, in his own vocabulary ("bypass-testing evidence", "composite metric", "per-step input tokens, output tokens, cost").
- End-to-end test: run boot with the new hooks and confirm a fresh eval record contains step-level model/tokens/cost and a guardrail result at every transition.

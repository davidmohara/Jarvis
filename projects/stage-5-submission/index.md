# Evidence Index

**Updated:** 2026-10-26 · **Use:** each row maps a design guarantee to its evidence artifact and current measured status, so verification walks claim → artifact without wandering the repository.

## Guarantee → evidence map

| # | Guarantee | Evidence artifact | Status |
|---|-----------|-------------------|--------|
| 1 | Deterministic guardrails at every step transition: per-step verifiers (`workflows/<wf>/verify/step-*.py`, dispatched by step-complete.py) for all 4 candidates, boot step-06.5 machine-checked, plus Layer 0 schema validation (`validate-subagent-output.py`) on declared sub-agent outputs before any coordinator-visible pass. 13 step schemas across boot, morning-briefing, plaud-ingest. Adversarial verification as a guardrail (assertions morning-008 / daily-007 / plaud-002), Ralph-spawned with lens checklists for all 4 (`workflows/*-verification/`); catches recorded structurally in `stage4-evidence/adversarial-catches/` (5 entries as of 2026-10-16) | Complete; catch log live but thin (see its README) |
| 2 | Punch-out mechanisms bypass-tested | `stage4-evidence/bypass-tests/` (BT-01..BT-06 matrix + logs; BT-02 found 2 real escalation holes, both fixed same day with closed-loop re-test evidence in `BT-02-fix-verification-2026-10-08.md`; BT-05/BT-06 add git-redirect and command-position evidence) | Complete |
| 3 | End-to-end success rate per workflow | `stage4-evidence/success-rate-baseline-2026-10-08.{md,csv}` plus the 2026-10-26 recompute (`success-rate-recompute-2026-10-26.{md,csv}`, reproducible via `systems/eval-harness/success-rate.py`): strict and mechanical tiers, all-records and instrumented scopes, session-exit aborts counted separately, the "other" tier characterized record-by-record | Complete; recompute below |
| 4 | Per-step model/tokens/cost audit trail | `audit-exports/<workflow>/step-audit.{csv,json}` (per-step model/tokens/cost/owning_agent/token_source, plus correlation_id for end-to-end tracing); instrumentation in `systems/eval-harness/step_audit.py` + `export-step-audit.py` + `correlation.py` | Complete |
| 5 | Per-agent criteria artifacts: prompt, named criteria, measured results | `stage3/` (11 agents, 4 criteria each = 44); plan in `stage3-compliance-plan.md`; current verdicts below | Artifacts complete; measured verdicts below, disclosed as-is |
| 6 | Coordinator is dispatch-only (spawn-first steps, Hard Stops, gated git) | Phase-1 purity refactor across 42 files; iteration history in `stage3/master.md`; bypass-test evidence BT-03/BT-04/BT-06 | Complete; procedural-only paths disclosed in the bypass-test README |
| 7 | Formal agent manifest and scoping | `agents/manifest.md` (11 agents, roles, owned steps, boundaries, conflict resolution; the human operator documented as a non-agent participant) | Complete |
| 8 | Adversarial review isolation | `agents/adversarial-isolation.md` (isolation mechanics, Ralph coverage) + `stage4-evidence/adversarial-catches/` | Complete; catch log accumulating |
| 9 | Release history | `CHANGELOG.md` (v0.1.0 → v1.5.0 from 1,063 commits) + annotated tags; next tag at ship | Complete |
| 10 | Substance assessment + human elevation gate | `systems/eval-harness/substance/` (assessment, gate, append-only decision log; the operator's Continue recorded with identity and timestamp, classifications confirmed through the gate's own path) | Complete |
| 11 | Final review writer with deterministic headings | `workflows/final-review/` (Knox digest → prose-only writer → deterministic assembler → substance punch-out) | Complete; dry run over a real boot run at `workflows/final-review/runs/corr-20261026T224541-HXCV/` (findings from the run's record, prose by the spawned writer, deterministic assembly, gate covered; the run is itself recorded as an eval record linked by correlation ID) |

## Success rates (recompute 2026-10-26; full detail in `stage4-evidence/success-rate-recompute-2026-10-26.md`)

Two tiers, two scopes, applied consistently. "Strict" = status `success` or `complete` only. "Mech" = strict + `partial` (finished every step with degraded output), session-exit aborts excluded from the mech denominator. "Instrumented" = at least one step with real token attribution; thin n, directional. The "other" tier is characterized record-by-record in the recompute doc, not hidden in a bucket.

| Workflow | All-records: strict / mech | Instrumented: strict / mech (n) |
|---|---|---|
| boot | 32.8% / 54.2% (64 recs) | 33.3% / 70.6% (18) |
| morning-briefing | 34.8% / 95.7% (23 recs) | 100.0% / 100.0% (2) |
| daily-review | 75.0% / 98.4% (64 recs) | 100.0% / 100.0% (2) |
| plaud-ingest | 44.4% / 50.0% (36 recs) | 50.0% / 66.7% (4) |

Open characterization item: plaud-ingest's 11 no-reason aborts, consistent with no-op days but unverified; a verified no-op explanation would move its all-records mech to 62.1%. The distinct `no-op` terminal status now separates genuine no-ops going forward (4 records already closed that way).

## Per-agent criteria position (2026-10-16, attribution-aware recompute)

144 historically unattributed records were recovered at read time via transcript mining; historical records are never rewritten. Thresholds untouched throughout; below-bar results are disclosed, not lowered.

| Agent | Records | Strict success | Criteria verdict |
|---|---|---|---|
| master | 151 | 69.8% | J1-J4 below bars; J2 routing sentinel (boot-009) active |
| chief | 97 | 67.0% | C4 52.4% overall, 66.7% excluding scheduled runs — below 80% both ways |
| chase | 12 | 33.3% | H1-H3 have assertions; graded runs accumulating |
| harper | 23 | 88.9% | P3 69.4%, P4 71.4% — below bars |
| knox | 101 | 62.1% | K3 73.9% below 90%; K4 74.2% below 80% |
| quinn | 8 | 100% (n=8) | First runs landed 2026-10-16 |
| ralph | 16 | 50.0% | First attribution 2026-10-16; assertions wired |
| rigby | 86 | 81.6% | R3 86.5% below 90%; R4 70.0% below 80% |
| shep | 12 | 66.7% | First assertion-bearing runs 2026-10-16 |
| sterling | 7 | 75.0% | First assertion-bearing runs 2026-10-16 |
| galen | 5 | 100% (n=5) | First records ever 2026-10-16 |

## Data-honesty levers

- `owning_agent` attribution (no subagent-type label pollution; steps attribute to manifest agents)
- `token_source` (windowed vs. missing per-step token attribution; fabricated fallbacks are retired — a step whose window matches no turns gets honest nulls)
- Success-rate tiers (strict vs. mechanical, session-exit aborts excluded and counted separately)
- Substance classifications confirmed only through the gate's `confirm` path, which requires a covering human decision

## Verification-workflow naming note

The four `workflows/*-verification/` directories (morning-briefing, daily-review, plaud-ingest, shutdown-cleanup) are the adversarial reviewer's verification sub-workflows, siblings of the pre-existing `boot-verification/`, not additional candidate workflows; the 4-candidate set stands. shutdown-cleanup is held to the same instrumentation standard as the candidates without being one.

# Stage 5 Certification Submission Bundle

**Prepared:** 2026-10-16 · **For:** Tim Rayburn (Stage 5 examination) · **Bundle status:** in flight, data window closes 2026-10-21

## What this bundle is

A self-contained evidence package for the Stage 5 certification resubmission. Everything needed to walk Tim's 9 findings is inside this folder, so the examination does not require wandering the repository. The bundle was assembled 2026-10-16 from the live repo. Every item is a **copy**, not a move, so the source paths still hold the originals.

Source paths for the copied trees:

- `stage3/` mirrors `systems/eval-harness/stage3/*.md`
- `stage4-evidence/` mirrors `projects/stage-4-evidence/` (restored from `08c1f338^` on 2026-10-16; the tree had been deleted in commit `08c1f338`)
- `verification/` mirrors the four candidate `workflows/*-verification/workflow.md` files
- `agents/` mirrors `agents/manifest.md` and `agents/adversarial-isolation.md`
- `audit-exports/` mirrors `systems/eval-harness/audit-exports/` (per-step token/cost exports)
- `CHANGELOG.md` mirrors the repo-root `CHANGELOG.md`

## Contents

```
stage-5-submission/
├── README.md                      (this file)
├── index.md                       (the evidence index: 9 findings → artifacts → status)
├── stage3-compliance-plan.md      (Stage 3 remediation plan, all agents)
├── CHANGELOG.md                   (release history, v0.1.0 → v1.5.0)
├── stage3/                        (11 Stage 3 artifacts, one per agent)
│   ├── master.md  chief.md  chase.md  harper.md  knox.md  quinn.md
│   ├── ralph.md   rigby.md  shep.md   sterling.md  galen.md
├── stage4-evidence/               (Stage 4 bypass-test evidence, restored)
│   ├── bypass-tests/              (BT-01..BT-06 + README)
│   │   └── logs/                  (BT-01..BT-04, BT-06 run logs)
│   └── success-rate-baseline-2026-10-08.md / .csv
├── verification/                  (4 candidate-workflow Ralph verification sub-workflows)
│   ├── boot-verification-workflow.md
│   ├── morning-briefing-verification-workflow.md
│   ├── daily-review-verification-workflow.md
│   └── plaud-ingest-verification-workflow.md
├── audit-exports/                 (per-step token/cost exports, one dir per candidate)
│   ├── boot/step-audit.{csv,json}
│   ├── daily-review/step-audit.{csv,json}
│   ├── morning-briefing/step-audit.{csv,json}
│   └── plaud-ingest/step-audit.{csv,json}
└── agents/
    ├── manifest.md                (agent roster, roles, boundaries, conflict resolution)
    └── adversarial-isolation.md   (adversarial review isolation mechanics)
```

## The 9 findings, mapped to artifacts in this bundle

| # | Finding (Tim's vocabulary) | In-bundle artifact | Status |
|---|----------------------------|--------------------|--------|
| 1 | Guardrails incomplete, not all adversarial | `verification/` (4 candidate verification sub-workflows) | Complete: per-step verifiers plus Ralph adversarial verification for all 4 candidates, per `index.md` row 1 |
| 2 | Punch-out mechanisms not bypass-tested | `stage4-evidence/bypass-tests/` | Complete: BT-01..BT-06 matrix plus logs; BT-02 found 2 real holes, both fixed with closed-loop re-test evidence in `BT-02-fix-verification-2026-10-08.md`; BT-05/BT-06 add git-redirect and command-position evidence |
| 3 | No end-to-end success rate for any workflow | `stage4-evidence/success-rate-baseline-2026-10-08.md` and `.csv` | Baseline done; final numbers pending the instrumented data window (closes 2026-10-21) |
| 4 | Per-step input tokens, output tokens, cost missing | `audit-exports/` (per-step CSV/JSON for all 4 candidates) | Instrumentation done and a first export pass landed for boot, morning-briefing, daily-review, and plaud-ingest. The instrumentation scripts (`systems/eval-harness/step_audit.py`, `export-step-audit.py`) are not copied into the bundle. Final instrumented run window closes 2026-10-21. |
| 5 | No Stage 3 artifacts for component agents | `stage3/` (11 files) plus `stage3-compliance-plan.md` | Artifacts complete; of 44 criteria, **1 pass / 12 fail / 31 no data** (detail below). Final graded-run window closes 2026-10-21. |
| 6 | Coordinator purity violations | `stage3/master.md` (Phase 1 refactor narrative plus iteration history) | Complete; residual: personal-block exit instruction (David's edit). The cited remediation error entries (`err-20261008T195835-EW45PB` etc.) live in `systems/error-tracking/entries/`, not in this bundle. |
| 7 | No formal agent manifest / scoping | `agents/manifest.md` | Complete: 11 agents with roles, owned steps, boundaries, conflict resolution; David documented as human operator |
| 8 | Adversarial review isolation undocumented | `agents/adversarial-isolation.md` | Complete: isolation mechanics and Ralph coverage documented; catch examples accumulate during the data window |
| 9 | No CHANGELOG, version tags, release history | `CHANGELOG.md` | Complete: v0.1.0 → v1.5.0 from git history; v2.0.0 tagged at resubmission |

## Finding 5 detail: Stage 3 criteria position

Read from the 11 `stage3/<agent>.md` files on disk at assembly time (2026-10-16, artifact mtimes 08:49-08:53). Each agent has 4 criteria, so 44 criteria total. Verdict basis: **pass** = the file states a measured value that meets the threshold; **fail** = the file states a measured value below the threshold or an explicit violation; **no data** = the criterion is not directly asserted, not instrumented, or carries no measured value.

| Agent | Criteria verdicts | Pass / Fail / No data |
|-------|-------------------|-----------------------|
| master | J1 fail, J2 fail, J3 fail, J4 fail | 0 / 4 / 0 |
| chief | C1 no data, C2 fail, C3 no data, C4 fail | 0 / 2 / 2 |
| chase | H1 no data, H2 no data, H3 no data, H4 pass | 1 / 0 / 3 |
| harper | P1 no data, P2 no data, P3 fail, P4 fail | 0 / 2 / 2 |
| knox | K1 no data, K2 no data, K3 fail, K4 fail | 0 / 2 / 2 |
| quinn | Q1-Q4 no data | 0 / 0 / 4 |
| ralph | A1-A4 no data | 0 / 0 / 4 |
| rigby | R1 no data, R2 no data, R3 fail, R4 fail | 0 / 2 / 2 |
| shep | S1-S4 no data | 0 / 0 / 4 |
| sterling | T1-T4 no data | 0 / 0 / 4 |
| galen | G1-G4 no data | 0 / 0 / 4 |
| **Total** | | **1 / 12 / 31** |

Honest reading of that split:

- The **1 pass** is chase H4 (3 of 3 graded runs are A/B, above the 80% bar) and even that is thin: the stage3 file itself flags it as "still not evidence" at n=3.
- The **12 fails** are measured below-bar results, not missing data. They cluster on the two structural-assertion and Tier 3-grade criteria per agent (master J1-J4, chief C2/C4, harper P3/P4, knox K3/K4, rigby R3/R4). Several are genuinely close (rigby R3 at 86.5% vs a 90% bar) and several are not (chief C4 at 53.8% vs 80%).
- The **31 no-data** criteria are the ones the compliance plan flagged as unasserted. Phase 1 of that plan wired sentinel assertions for many of them on 2026-10-16, but no measured value exists on disk yet, so they cannot be scored pass or fail. Chase, Quinn, Shep, Sterling, Ralph, and Galen contribute most of this bucket.

No threshold, criterion, or assertion pass/fail rule was changed anywhere in this bundle. Where a bar is not met, the stage3 files disclose it rather than lower it; threshold changes are David's call.

## Known gaps (not in this bundle)

- **Finding 4 instrumentation scripts** (`step_audit.py`, `export-step-audit.py`): live in `systems/eval-harness/`, not copied into this bundle. The exports they produce are included at `audit-exports/`.
- **Finding 6 remediation error entries**: live in `systems/error-tracking/entries/`, not copied into this bundle.
- **Final success-rate numbers** (finding 3) and the **fresh graded-run window** (finding 5): both close 2026-10-21 and are pending.
- The `audit-exports/` set included here is a first pass over the current run window; it will be refreshed when the data window closes.

## Provenance

- Restored 2026-10-16 via `skills/git/scripts/ies-git restore --source=08c1f338^` for two path groups: `projects/stage-4-evidence/` (15 files) and `projects/stage5-certification-remediation.md`. Nothing else from `08c1f338` was restored (notably `projects/stage5-compliance-audit-2026-10-08.md` was deliberately left deleted).
- `index.md` rows 2, 3, 4, and 9 were re-checked against the restored tree: rows 2 and 3 now resolve (`stage4-evidence/bypass-tests/` and `stage4-evidence/success-rate-baseline-2026-10-08.{md,csv}`), row 9 (`CHANGELOG.md`) resolves, and row 4's `audit-exports` export path now exists and is included at `audit-exports/` (it landed from a parallel workstream during assembly).

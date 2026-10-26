# Delegation System Evidence Bundle

**Assembled:** 2026-10-26

## What this bundle is

A self-contained evidence package for the delegation system. The system's design guarantees are described in `submission-draft.md` (the package's root document, organized by guarantee); everything needed to verify those claims against evidence is inside this folder, so verification does not require wandering the repository. Every item is a **copy**, of live repo files, so the source paths still hold the originals.

Source paths for the copied trees:

- `stage3/` mirrors `systems/eval-harness/stage3/*.md` (11 per-agent criteria artifacts)
- `stage4-evidence/` mirrors `projects/stage-4-evidence/` (bypass-test matrix, adversarial catches, success-rate baselines)
- `verification/` mirrors the four candidate `workflows/*-verification/workflow.md` files
- `agents/` mirrors `agents/manifest.md` and `agents/adversarial-isolation.md`
- `audit-exports/` mirrors `systems/eval-harness/audit-exports/` (per-step model/token/cost exports with correlation IDs)
- `CHANGELOG.md` mirrors the repo-root `CHANGELOG.md`

The mechanism code itself (schema validation, correlation IDs, the substance gate, the report assembler) lives in the repository at the paths named in `submission-draft.md`; this bundle carries its outputs and the criteria artifacts, not the code.

## Contents

```
stage-5-submission/
├── submission-draft.md            (root document: the system's guarantees, stated and evidenced)
├── README.md                      (this file)
├── index.md                       (evidence index: guarantee → artifact → measured status)
├── stage3-compliance-plan.md      (per-agent criteria measurement plan)
├── stage3-remediation-plan.md     (per-agent iteration history)
├── CHANGELOG.md                   (release history, v0.1.0 → v1.5.0)
├── stage3/                        (11 criteria artifacts, one per agent)
│   ├── master.md  chief.md  chase.md  harper.md  knox.md  quinn.md
│   ├── ralph.md   rigby.md  shep.md   sterling.md  galen.md
├── stage4-evidence/
│   ├── bypass-tests/              (BT-01..BT-06 + README + run logs)
│   ├── adversarial-catches/       (adversarial review catches, recorded structurally)
│   └── success-rate-baseline-2026-10-08.md / .csv
├── verification/                  (4 candidate-workflow adversarial verification sub-workflows)
│   ├── boot-verification-workflow.md
│   ├── morning-briefing-verification-workflow.md
│   ├── daily-review-verification-workflow.md
│   └── plaud-ingest-verification-workflow.md
├── audit-exports/                 (per-step model/token/cost exports, one dir per candidate)
│   ├── boot/step-audit.{csv,json}
│   ├── daily-review/step-audit.{csv,json}
│   ├── morning-briefing/step-audit.{csv,json}
│   └── plaud-ingest/step-audit.{csv,json}
└── agents/
    ├── manifest.md                (agent roster, roles, boundaries, conflict resolution)
    └── adversarial-isolation.md   (adversarial review isolation mechanics)
```

## How to verify against this bundle

Start with `submission-draft.md`. Each of its seven sections states a guarantee and names its evidence. `index.md` carries the same mapping in table form, plus the current measured positions (success rates, criteria verdicts) with below-bar results disclosed as-is — no threshold, criterion, or pass/fail rule was changed anywhere in this bundle; where a bar is not met, the artifact says so.

## Candidate workflows

The delegation system's instrumented candidates are the four workflows in daily use: **boot**, **morning-briefing**, **daily-review**, and **plaud-ingest**. Usage data behind this set is in `workflow-rationalization-memo-2026-10-08.md` (repo path `projects/`). **shutdown-cleanup**, the session-exit workflow, is held to the same instrumentation standard (per-step verifiers, guardrail checkpoint, adversarial verification, git routed through the gated wrapper) though it is not a candidate.

## Known gaps (not in this bundle)

- The instrumentation scripts (`step_audit.py`, `export-step-audit.py`, `validate-subagent-output.py`) live in `systems/eval-harness/`, not copied in; their outputs are included at `audit-exports/`.
- Layer 0 schema coverage: schemas are declared per step where structured outputs exist (13 steps across boot, morning-briefing, plaud-ingest; daily-review records no structured outputs to validate, so it has none yet).
- Success-rate figures in `index.md` are the current window's; the instrumented-run recompute refreshes them.

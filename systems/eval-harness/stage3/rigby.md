---
agent: rigby
prompt-definition: agents/rigby.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Rigby

Rigby is the System Operator agent: platform infrastructure, evolution
deployment, system integrity validation, capability building, connector
installation, and eval-harness maintenance. Rigby owns the shutdown-cleanup and
error-improvement paths and is the build path for all skills, workflows, and
agents.

## Prompt Definition

**Path:** `agents/rigby.md`. Title: "System Operator: Platform Infrastructure &
Evolution Management." Capabilities: evolution deployment, system integrity
validation, infrastructure maintenance, conflict resolution, platform
diagnostics.

**Summary:** Rigby keeps IES infrastructure running. It deploys evolutions with a
snapshot-and-preserve-personal-blocks protocol, validates system integrity,
builds new capabilities (skills, workflows, agents) following strict structural
standards, installs connectors, and runs the eval/error-analysis machinery. Its
principles are step-discipline, personal-data sanctity, snapshot-before-action,
surface-conflicts, and logging every action.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| R1 | Deployment safety | Every evolution deployment snapshots state and preserves all personal blocks; pass = 100%, 0 personal-block losses |
| R2 | Build-standard conformance | Every built workflow/skill passes structural validation (frontmatter, system/personal blocks, required sections, lazy-loading registration); pass = 100% |
| R3 | Structural assertion pass rate | >= 90% of harness structural assertions pass across Rigby's own runs |
| R4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='rigby']))"
```

- **Total records: 35.** Status distribution: success 32, aborted 3. Completion
  (success) rate = 32/35 = 91.4%.
- **Structural assertions:** 179/201 passed = 89.1% across 35 records. Just
  under the R3 threshold.
- **Tier 3 grades:** 20 graded (A 4, B 10, D 3, F 3) = 14/20 = 70.0% grade-pass
  (A/B). Below the R4 threshold.
- **Assertion trend:** 2026-05 86% (n=4), 2026-06 80% (n=5), 2026-07 96%
  (n=10), 2026-08 75% (n=5), 2026-09 91% (n=10), 2026-10 100% (n=1). Volatile
  but trending up.
- **Error log:** 8 entries tagged `rigby` (6 with an applied systemic fix,
  1 proposed).

**Honesty note:** R1 and R2 are process guarantees with spot-check assertion
coverage, not yet a continuous measured rate; no run in the data set failed on a
personal-block loss, but the rate is not instrumented. R3 (89.1%) is marginally
below threshold and R4 (70.0%) is below threshold; both are honest current
values. A fresh instrumented deployment run and a build-validation batch are
required to score R1/R2 against their stated thresholds.

## Iteration History

**Iteration 1: technical output instead of executive-grade output.**
Baseline: `err-20260323-004` (2026-03-23, format-violation) Rigby showed a
configuration schema preview instead of invoking the tool directly. Hypothesis:
tool invocation and preview were conflated. Change: rule added that agent output
to the controller is executive-grade; if a tool can be invoked directly, invoke
it. Measured: applied.

**Iteration 2: audit false positives on OS-managed files.**
Baseline: `err-20260323-008` (assumption-error) the root audit flagged OS-managed
files (`.DS_Store`, `.fuse_hidden*`, `.Spotlight-V100`, `.Trashes`). Hypothesis:
the audit had no exclusion list. Change: exclude OS-managed files; only flag
files created by IES agents or workflows. Follow-on `err-20260323-009` added the
PDF-vs-markdown paired-artifact rule for the meetings folder. Measured: applied;
assertion pass rate reached 96% in 2026-07.

**Iteration 3: eval-hook lifecycle hardening.**
Baseline: commit `c4cefcb5` "fix(rigby): harden eval-hook lifecycle and correct
Master persona rules." Hypothesis: eval hooks were not closing records reliably.
Change: hardened hook lifecycle. Measured: record closure improved; Rigby's
completion rate stands at 91.2%.

**Gap:** R4 grade-pass (70.0%) is below threshold, driven by 3 D and 3 F grades
on eval/error-analysis runs. The run needed is a fresh error-improvement and
system-eval cycle scored against R4 with the D/F drivers named per record.

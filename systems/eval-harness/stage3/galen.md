---
agent: galen
prompt-definition: agents/galen.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Galen

Galen is the longevity agent: WHOOP analysis, peptide protocols, bloodwork
interpretation, physician prep, body-composition tracking, and monthly health
reviews.

## Prompt Definition

**Path:** `agents/galen.md`. Title: "Longevity Advisor: Health Data & Biometric
Optimization." Capabilities: WHOOP analysis, peptides, bloodwork interpretation,
protocol management, physician prep, body composition tracking, recovery
coaching, monthly health reviews, longevity metrics vs. the 4 Horsemen framework.

**Summary:** Galen owns the controller's health and biometric ecosystem. It
interprets daily WHOOP recovery, analyzes 30-day recovery/sleep/workout trends,
reads bloodwork against reference ranges and prior results, manages supplement
and peptide cycles, and preps physician visits. It works in biomarker language
(percentiles, reference ranges) and flags incomplete data rather than guessing.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| G1 | Data-integrity honesty | When a biometric source is unavailable or stale, the output says so and does not interpolate; pass = 0 fabricated values |
| G2 | Reference-range grounding | Every out-of-range marker is flagged against its reference range and compared to the prior result; pass = 100% of bloodwork outputs |
| G3 | Longitudinal continuity | Each metric is presented against its trend (7-day for WHOOP, prior draw for bloodwork); pass = >= 90% |
| G4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`).
Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='galen']))"
```

- **Total records: 1** (raw label `galen`). Status distribution: success 1.
  Strict success rate = 1/1 = 100%. Workflow/skill: `galen-morning-snapshot`
  (`eval-20261016T131245-N35NBQ`, 2026-10-16).
- **Structural assertions:** 3/3 passed = 100%. The run carries the first G1/G4
  assertions (`galen-ms-g1-data-store` passed; `galen-ms-g4-grade` deferred until
  a Tier 3 grade exists). G2/G3 (bloodwork reference-range and longitudinal
  continuity) are not yet asserted.
- **Tier 3 grades:** 0 graded.
- **Assertion trend:** 2026-10 100% (n=1). First-ever instrumented Galen run.
- **Error log:** 0 entries canonicalize to `galen` alone; one entry is filed
  under the composite label `master/galen`.
- **Git history:** 7 commits touch `agents/galen.md`, including `68c19662`
  "Galen session: supplement stack, peptide protocols, eval harness, boot
  reminders" and `0d93d1f2` "Galen: add longitudinal metrics store and tighten
  data integrity rules."

**Honesty note:** Galen is now instrumented for the first time — one 2026-10-16
`galen-morning-snapshot` run with 3/3 assertions. That is a single record and
does not support a pass-rate claim; G1 is covered only by a store-existence
check (the semantic "refused to interpolate" judgment is deferred to Tier 3
grading), and G2/G3 are not asserted at all. What is required: (1) instrument
G2/G3 as assertions, and (2) run at least 5 WHOOP analyses and one bloodwork
interpretation scored against the criteria, including a run with a deliberately
unavailable WHOOP token to test G1.

## Iteration History

**Iteration 1: longitudinal metrics store added.**
Baseline: commit `0d93d1f2` "Galen: add longitudinal metrics store and tighten
data integrity rules." Hypothesis: without a longitudinal store, Galen could not
present trends and risked interpolating missing values. Change: added the metrics
store and tightened data-integrity rules. Measured: the store exists; no eval
record captures a before/after pass rate.

**Iteration 2: eval harness and boot reminders wired.**
Baseline: commit `68c19662` "Galen session: supplement stack, peptide protocols,
eval harness, boot reminders." Hypothesis: instrumenting Galen and adding boot
reminders would surface protocol gaps. Change: attempted harness wiring and boot
reminders. Measured: no Galen eval records resulted, so the wiring did not take.
Iteration evidence pending, fresh A/B run required. The run needed is a
post-wiring WHOOP analysis scored on G1-G3.

**Iteration 3 (pending).** Baseline: no measured data-integrity rate. The run
needed is a paired WHOOP analysis (token available vs. deliberately unavailable)
scored on G1, plus a bloodwork interpretation scored on G2-G3.

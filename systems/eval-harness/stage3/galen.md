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

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='galen']))"
```

- **Total records: 0.** Galen has no eval records in the harness. This is the
  honest headline: no measured pass rate exists.
- **Structural assertions:** none.
- **Tier 3 grades:** none.
- **Error log:** one entry is associated with Galen, filed under the composite
  agent label `master/galen` (2026, low severity, data-accuracy). No entry is
  tagged `galen` alone.
- **Git history:** 7 commits touch `agents/galen.md`, including `68c19662`
  "Galen session: supplement stack, peptide protocols, eval harness, boot
  reminders" and `0d93d1f2` "Galen: add longitudinal metrics store and tighten
  data integrity rules."

**Honesty note:** Galen has never been instrumented. Zero eval records means
zero measured results, and the composite `master/galen` error label shows Galen
work was happening but was not attributed to Galen. What is required: (1) wire
the `galen-morning-snapshot` and `galen-whoop-analysis` skills into the eval
harness so runs record `agent: galen`, (2) instrument G1-G3 as assertions, and
(3) run at least 5 WHOOP analyses and one bloodwork interpretation scored against
the criteria, including a run with a deliberately unavailable WHOOP token to test
G1.

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

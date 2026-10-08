# Stage 4 Success-Rate Baseline (Phase 4C groundwork)

**Date:** 2026-10-08 · **Source:** all eval records in `systems/eval-harness/runs/eval-*.json` · **CSV:** `success-rate-baseline-2026-10-08.csv` (same folder)

## Metric definition

**Fully successful run** = record `status` in (success, complete) AND `assessment.mechanical.completed == true` AND `assessment.mechanical.all_steps_finished == true`. Composite success rate = fully successful / total records for the workflow. This is the "X% of runs completed all steps successfully" figure Tim's grader requires.

## Baseline (existing records, mined 2026-10-08)

| Workflow | Total runs | Fully successful | Success rate | Status breakdown |
|----------|-----------:|----------------:|-------------:|-------------------|
| daily-review | 58 | 45 | 78% | 45 success, 12 partial, 1 incomplete |
| plaud-ingest | 31 | 15 | 48% | 15 success, 11 aborted, 2 failure, 1 partial, 2 incomplete |
| boot | 45 | 16 | 36% | 14 success, 3 complete, 13 aborted, 8 partial, 4 failure, 2 incomplete, 1 in-progress |
| morning-briefing | 18 | 5 | 28% | 6 success, 11 partial, 1 incomplete |

## Refined tiers (abort-reason breakdown added 2026-10-08)

All 32 "partial" runs across the four candidates have `mechanical.completed == true` AND `all_steps_finished == true` — they finished every step but with degraded output (typically data-source gaps). They belong in a "completed with degradation" tier, not the failure column.

| Workflow | Strict | + degraded | Excluded (session-ended aborts) | Unexplained aborts | Failure/incomplete | Defensible rate (strict+degraded, session-exits excluded) |
|----------|-------:|-----------:|--------------------------------:|-------------------:|------------------:|----------------------------------------------------------:|
| daily-review | 45/58 (78%) | 57/58 (98%) | 0 | 0 | 1 incomplete | **57/58 = 98%** |
| morning-briefing | 5/18 (28%) | 16/18 (89%) | 0 | 0 | 1 incomplete | **16/17 = 94%** (1 incomplete unexplained) |
| plaud-ingest | 15/31 (48%) | 16/31 (52%) | 0 | 11 | 2 failure, 2 incomplete | **16/18 = 89%** if the 11 unexplained aborts verify as no-ops |
| boot | 16/45 (36%) | 24/45 (53%) | 6 | 7 | 4 failure, 2 incomplete, 1 in-progress | **24/32 = 75%** if the 7 unexplained aborts verify as no-ops |

**Unexplained aborts need characterization before certification.** All 11 plaud-ingest aborted records carry no abort_reason, empty notes, and zero tool failures — consistent with no-op runs when no new recordings are staged, but unverified. Same for boot's 7. Harness fix (Phase 2 scope): every abort must record a reason; no-op runs should be a distinct terminal status (e.g., `no-op`) so the success-rate metric can legitimately exclude them.

**morning-briefing's 28% strict rate is a status-labeling artifact, not a workflow failure**: 11 of 18 runs did all steps with degraded output. The certification submission should present strict and degraded tiers side by side, with the strict tier as the headline number.

## Caveats the Phase 4C refinement must resolve

1. ~~Aborted runs may be legitimate exclusions~~ — resolved above for the baseline; final numbers require the harness abort-reason fix plus verification of the 18 unexplained aborts.
2. ~~Partial runs need a decision~~ — resolved: report strict plus "completed with degradation" tiers side by side.
3. **10+ runs minimum per workflow** is already satisfied by record count for all four candidates; the certification number should come from the post-Phase-2 instrumented window (fresh runs with per-step audit trails) so success rate and audit trail come from the same executions.

## Next steps (Phase 4C, in the data window)

- Re-run this computation after Phase 2 instrumentation lands, restricted to instrumented runs.
- Add abort-reason breakdown to the export.
- Produce the final per-workflow success-rate CSV + the metric definition note for the submission bundle.

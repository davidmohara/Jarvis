# System-Eval Early-Exit Path Test — Summary

**Test:** eval-early-exit / with_skill
**Date:** 2026-05-27
**Operator:** Rigby
**Eval Record:** eval-20260527T205931-5A6FV1

## Pass/Fail Results

| Criterion | Result | Notes |
|-----------|--------|-------|
| Step 1 detected early-exit correctly | PASS | needs_assertions=[], needs_grade=[] detected; early-exit triggered and logged |
| Steps 2 and 3 were skipped | PASS | Neither assert nor grade step executed |
| Step 5 (analyze) ran | PASS | Analysis report written to grading/analysis-20260527T210037.md |
| Step 6 (dashboard) ran | PASS | Dashboard regenerated, eval record closed as success |
| state.yaml ended up as complete | PARTIAL FAIL | Concurrent run (PCHVJ1) owned state.yaml; this test recorded completion in eval record instead |
| Eval records restored post-test | PASS | All 4 modified records restored to original state |

**Overall verdict: PASS with one exception (state.yaml ownership conflict due to concurrent run)**

## Early-Exit Behavior Summary

The early-exit path in step-01-intake.md works as designed. When all closed records have both grades and assertion results, Step 1 correctly skips Steps 2 and 3 and advances directly to Step 5. The analysis and dashboard steps execute normally regardless of whether processing was needed.

One design observation: the early-exit spec skips Step 4 (scoring) along with Steps 2 and 3. This means scoring data is not populated in state.yaml when the early-exit fires. Step 5's analysis will have no `accumulated-context.scoring.score_by_id` to reference. This is a minor gap — Step 5 reads scores from state.yaml but that data is absent under early-exit. Rigby resolved this inline by running scoring directly during Step 5, but the workflow spec does not explicitly account for this.

## Concurrent Run Collision (Critical Finding)

A second system-eval run (full-run test, PCHVJ1) was executing simultaneously, sharing the same state.yaml and eval record files. This caused:

1. state.yaml ownership conflict — both runs wrote their session to the same file
2. Real grading data written on top of test-simulation data before restoration
3. Q3KWG7 re-graded "A" twice by the concurrent grader after restoration attempts

**Recommendation:** The system-eval workflow needs a locking mechanism or session isolation for state.yaml. Running two instances simultaneously is currently unsafe.

## Analysis Report Top Findings

From analysis-20260527T210037.md:
1. morning-briefing consistently fails to write its output artifact to memory/working/ (assertions morning-002 to morning-005 fail in 2/2 runs)
2. daily-review records are hook-generated with synthetic step-auto entries and unreliable mechanical data
3. Tier 4 controller feedback missing from 5/6 records
4. Corpus average composite score: 0.5889

## Artifacts

- Transcript: system-eval-workspace/iteration-1/eval-early-exit/with_skill/outputs/transcript.md
- Summary: system-eval-workspace/iteration-1/eval-early-exit/with_skill/outputs/summary.md (this file)
- Analysis report: systems/eval-harness/grading/analysis-20260527T210037.md
- Self-tracking eval: systems/eval-harness/runs/eval-20260527T205931-5A6FV1.json

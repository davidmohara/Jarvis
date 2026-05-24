---
status: not-started
step: step-04-benchmark-snapshot
---

# Step 04: Benchmark Snapshot

## YOUR TASK

Capture the eval harness baseline before applying the evolution. This step establishes a performance baseline by grading recent eval records and snapshotting the eval-harness/runs/ directory for comparative analysis after deployment.

## INPUT DATA (from state.yaml)

- `evolution_path` — Path to evolution package
- `snapshot_id` — ID of the snapshot created in Step 03

## REQUIRED ACTIONS

1. **Check for eval harness presence**
   - Verify `systems/eval-harness/` directory exists
   - If not present, skip this step (no baseline to capture) and proceed to Step 05
   - Log to state.yaml: `benchmark_snapshot: skipped (no eval harness)`

2. **Grade recent ungraded eval records (pre-deployment baseline)**
   - List all eval records in `systems/eval-harness/runs/*.json`
   - Filter for records where `assessment.grading` is null or missing
   - Read and grade each ungraded record inline (do not spawn a sub-skill — Rigby reviews the output quality directly)
   - Assign grades based on output files referenced in each record and the grader rubric in `systems/eval-harness/schema.md`
   - Update each record's `assessment.grading` block with the grade and grader_notes
   - Log count of newly graded records to state.yaml: `benchmark_snapshot.records_graded: N`
   - **Note:** If no ungraded records exist, skip this sub-step and proceed
   - **Note:** The comparative grading in Step 07 compares FUTURE runs (post-deployment) against this baseline. The comparison will only be meaningful after the system has been exercised post-deployment — Step 07 notes this explicitly.

3. **Snapshot eval-harness/runs/ directory**
   - Copy entire `systems/eval-harness/runs/` directory to snapshot location
   - Destination: `evolutions/snapshots/{snapshot_id}-eval-baseline/`
   - Preserve all JSON files with their grading data
   - Log snapshot path to state.yaml: `benchmark_snapshot.eval_baseline_path: evolutions/snapshots/{snapshot_id}-eval-baseline/`

4. **Calculate baseline metrics**
   - Compute success rate across all eval records (Tier 1 mechanical pass/fail)
   - Compute average composite score (if available)
   - Count records by grade (A-F) for graded records
   - Store metrics in state.yaml:
     ```
     benchmark_snapshot.baseline_metrics:
       total_records: N
       success_rate: X%
       avg_composite_score: Y
       grade_distribution: {A: N, B: N, C: N, D: N, F: N}
     ```

5. **Update state.yaml**
   - Set step status: `status: complete`
   - Write benchmark snapshot data to `accumulated-context`
   - Set `current-step: step-05-scan-personal-blocks`

## OUTPUT DATA (write to state.yaml accumulated-context)

```yaml
benchmark_snapshot:
  skipped: false
  eval_baseline_path: evolutions/snapshots/{snapshot_id}-eval-baseline/
  records_graded: N
  baseline_metrics:
    total_records: N
    success_rate: X%
    avg_composite_score: Y
    grade_distribution:
      A: N
      B: N
      C: N
      D: N
      F: N
```

## HALT CONDITIONS

- If eval harness directory does not exist: Skip this step, log reason, proceed to Step 05
- If eval-harness/runs/ is empty: Log warning `benchmark_snapshot.baseline_metrics.total_records: 0`, proceed with empty baseline
- If grading fails for any record: Log error, continue with other records, do not halt
- If no ungraded records exist: Skip grading sub-step, still snapshot and calculate metrics from already-graded records

## SUCCESS CRITERIA

- Eval harness presence checked and logged
- Ungraded records graded (if any)
- Eval-harness/runs/ directory copied to snapshot location
- Baseline metrics calculated and stored in state.yaml
- State.yaml updated with step complete status and next step pointer

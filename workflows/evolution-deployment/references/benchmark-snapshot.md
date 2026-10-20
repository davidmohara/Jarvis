<!-- system:start -->
# Benchmark Snapshot Protocol (evolution-deployment)

Invoked by step-07 task 3. Run exactly as written.


**Critical:** This captures the eval harness baseline AFTER the evolution is applied, not before. This ensures regression detection compares future runs against the post-deployment state.

1. **Check for eval harness presence**
   - Verify `systems/eval-harness/` directory exists
   - If not present, skip benchmarking and proceed to step 4
   - Log to state.yaml: `benchmark_snapshot: skipped (no eval harness)`

2. **Grade recent ungraded eval records**
   - List all eval records in `systems/eval-harness/runs/*.json`
   - Filter for records where `assessment.grading` is null or missing
   - Read and grade each ungraded record inline (Rigby reviews output quality directly)
   - Assign grades based on output files and grader rubric in `systems/eval-harness/schema.md`
   - Update each record's `assessment.grading` block with grade and grader_notes
   - Log count of newly graded records to state.yaml: `benchmark_snapshot.records_graded: N`
   - **Note:** If no ungraded records exist, skip this sub-step

3. **Create benchmark snapshot**
   - Generate benchmark ID: `bench-{evolution_id}-{timestamp}`
   - Copy entire `systems/eval-harness/runs/` directory to benchmark location
   - Destination: `systems/eval-harness/benchmarks/{benchmark_id}/`
   - Preserve all JSON files with their grading data
   - Log benchmark path to state.yaml: `benchmark_snapshot.benchmark_path: systems/eval-harness/benchmarks/{benchmark_id}/`

4. **Calculate baseline metrics**
   - Compute success rate across all eval records (Tier 1 mechanical pass/fail)
   - Compute average duration seconds
   - Compute average assertion pass rate
   - Count records by grade (A-F) for graded records
   - Store metrics in benchmark metadata file:
     ```
     systems/eval-harness/benchmarks/{benchmark_id}/metadata.json:
     {
       "benchmark_id": "bench-{evolution_id}-{timestamp}",
       "evolution_id": "{evolution_id}",
       "created": "ISO timestamp",
       "metrics": {
         "total_records": N,
         "success_rate": X%,
         "avg_duration_seconds": Y,
         "avg_assertion_pass_rate": Z%,
         "grade_distribution": {A: N, B: N, C: N, D: N, F: N}
       }
     }
     ```

5. **Cleanup old benchmarks (keep only prior 2)**
   - List all benchmarks in `systems/eval-harness/benchmarks/`
   - Sort by creation date (newest first)
   - Keep: current (just created) + prior 2
   - Delete all older benchmarks
   - Log cleanup action to state.yaml: `benchmark_snapshot.benchmarks_cleaned: N`

6. **Log benchmark snapshot to state.yaml**
   - Store in `accumulated-context`:
     ```
     benchmark_snapshot:
       skipped: false
       benchmark_path: systems/eval-harness/benchmarks/{benchmark_id}/
       benchmark_id: {benchmark_id}
       records_graded: N
       benchmarks_cleaned: N
       baseline_metrics:
         total_records: N
         success_rate: X%
         avg_duration_seconds: Y
         avg_assertion_pass_rate: Z%
         grade_distribution: {A: N, B: N, C: N, D: N, F: N}
     ```
<!-- system:end -->

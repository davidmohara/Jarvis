---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

# Step 07: Verify & Log

<!-- system:start -->
## Purpose

Final verification that personal blocks were preserved, system integrity is intact, and deployment completed successfully. Write evolution to history log. Surface changelog to user. Queue training prompts if present.

## Inputs

- `application_result` — From Step 06
- `files_processed` — From Step 06
- `personal_blocks_preserved` — From Step 06
- `personal_block_registry` — From Step 05
- `benchmark_snapshot` — From Step 04 (eval harness baseline data)
- `validated_manifest` — From Step 01
- `snapshot_id` — From Step 03
- `evolution_id` — From Step 01
- `evolution_version` — From Step 01

## Process

### 1. Verify Personal Block Integrity

**Critical verification step — ensures no personal data was lost.**

For each file in `personal_block_registry`:

1. Read the deployed file: `{project-root}/{file.path}`
2. Parse file to extract personal blocks (same logic as Step 04)
3. Compare extracted blocks to original registry:
   - Count must match
   - Content must match (exact string comparison)
4. If mismatch detected:
   - **CRITICAL ERROR** — personal block lost or corrupted
   - Surface error:
     ```
     ✗ INTEGRITY VERIFICATION FAILED
       File: {file.path}
       Expected blocks: {registry_count}
       Found blocks: {actual_count}

       Personal data may have been lost.

       IMMEDIATE ACTIONS:
       1. DO NOT PROCEED
       2. Rollback to snapshot: {snapshot_id}
       3. Report this error
     ```
   - Offer automatic rollback
   - **HALT** deployment

If all personal blocks verified:

```
✓ Personal block integrity verified
  Files checked: {count}
  Personal blocks confirmed present: {count}
  No data loss detected
```

### 2. System Integrity Check

Run basic system integrity checks:

1. **Agent files:** Verify all agent files have required metadata fields
2. **Workflow files:** Verify all workflow files have valid frontmatter
3. **Permissions:** If permissions.md was updated, verify syntax is valid
4. **References:** Check for broken references (e.g., workflow steps that don't exist)

If issues found:
- Log warnings (non-blocking)
- Surface to user for review

### 3. Benchmark Snapshot (capture post-deployment baseline)

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

### 4. Comparative Eval Grading (if benchmark snapshot exists)

**Important timing note:** Eval records created DURING this deployment workflow are not meaningful comparisons — the system has not been exercised yet. This step captures the current state immediately post-deployment. A meaningful comparison will only exist after the system has been exercised in production (next day or next use). The `eval_comparison` block is written now but expected to be `neutral` or `pending` until post-exercise eval records accumulate.

If `benchmark_snapshot.skipped` is false (eval harness baseline was captured):

1. **Compare with prior benchmark (if exists)**
   - List all benchmarks in `systems/eval-harness/benchmarks/`
   - Sort by creation date (newest first)
   - The second newest benchmark is the prior baseline (current is the one just created)
   - If no prior benchmark exists: log `eval_comparison.trend: pending` with note: "No prior benchmark to compare against. First evolution or benchmark cleanup removed all priors."
   - If prior benchmark exists: load its metadata.json

2. **Calculate current metrics from eval-harness/runs/**
   - Compute metrics for all eval records in `systems/eval-harness/runs/*.json`
   - This represents the current state (includes records from before, during, and after deployment)
   - Compute: success rate, avg duration, avg assertion pass rate, grade distribution

3. **Compare current metrics against prior benchmark**
   - Compare current metrics with prior benchmark metrics
   - Apply regression thresholds (hardcoded):
     - Success rate drops >10%: regression
     - Avg duration increases >25%: regression
     - Error rate doubles: regression
   - Determine trend: `improved | degraded | neutral`

4. **Log comparison results**
   - If trend is "improved": Surface as positive finding
   - If trend is "degraded": Surface as warning for review (potential regression)
   - If trend is "neutral": Log informational note
   - If trend is "pending": Log: "Eval comparison deferred — no prior benchmark exists."

If `benchmark_snapshot.skipped` is true (no eval harness):
- Skip comparative grading
- Log note: eval comparison skipped (no baseline available)

### 5. Write to Evolution History

Append entry to `{project-root}/evolutions/history.md`:

**Format:**

```markdown
## {evolution_name} ({evolution_version}) — Applied {date}

**Evolution ID:** {evolution_id}
**Applied:** {ISO timestamp}
**Snapshot:** {snapshot_id}
**Applied by:** {user or system}

### Files Changed

{for each file in file_list:}
- `{file.path}` — {action}{if merged: " ({personal_blocks_count} personal blocks preserved)"}
{end for}

### Conflicts

{if conflicts encountered:}
{list each conflict and resolution}
{else:}
None.
{end if}

### Personal Blocks Preserved

{if personal blocks:}
{for each file with personal blocks:}
- `{file.path}`: {list sections where blocks preserved}
{end for}
{else:}
No personal blocks in target files.
{end if}

### Status

{if no errors:}
✓ Deployment successful
{else:}
⚠️  Deployment completed with warnings (see errors below)
{list errors}
{end if}

### Eval Comparison (if benchmark snapshot exists)

{if eval_comparison was performed:}
**Trend:** {trend} (success rate: {success_rate_delta}, composite score: {avg_composite_score_delta})
**Baseline:** {baseline_metrics}
**Post-deployment:** {post_deployment_metrics}
{else:}
Eval comparison skipped (no baseline available)
{end if}

---

```

### 6. Update System Version

If evolution includes version bump:

Write or update `{project-root}/.ies-version`:

```
{evolution_version}
```

This tracks the current IES system version.

### 7. Surface Changelog to User

Present the evolution's changelog from manifest:

```
🎉 Evolution Applied: {evolution_name}

What's New:
{for each changelog entry:}
• {entry}
{end for}
```

If manifest includes `training_prompts`, mention them:

```
New capabilities unlocked! Try these:
{for each prompt:}
• {prompt.agent}: {prompt.prompt}
{end for}
```

### 8. Queue Training Prompts (if present)

If manifest includes `training_prompts`:

1. Check if project has training system integration
2. If yes: Pass training_prompts to training system for progressive unlock
3. If no: Log prompts to `{project-root}/evolutions/training-queue.json` for manual review

### 9. Output Final Summary

**If deployment fully successful:**

```
✅ Evolution deployment complete

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}
Rollback available: yes

History logged to: evolutions/history.md

{display changelog}
```

**If deployment had warnings/errors:**

```
⚠️  Evolution deployment completed with warnings

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {success_count}/{total_count}
Errors: {error_count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}

Issues encountered:
{list errors}

Recommendations:
- Review errors above
- Verify system functionality
- Rollback available if needed: rigby rollback {snapshot_id}

History logged to: evolutions/history.md
```

## Outputs

- `deployment_status` — Success/warning/failure
- `history_entry` — Written to evolutions/history.md
- `changelog_presented` — Boolean
- `training_prompts_queued` — Boolean
- `eval_comparison` — Comparative grading results (if benchmark snapshot exists)

## Workflow Complete

This is the final step. Evolution deployment workflow terminates here.

**User can now:**
- Use new evolution features
- Review evolution history: `rigby history`
- Rollback if needed: `rigby rollback {snapshot_id}`
- Test new capabilities mentioned in training prompts
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

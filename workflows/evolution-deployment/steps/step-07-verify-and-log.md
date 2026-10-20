---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

# Step 07: Verify & Log

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline


<!-- system:start -->
## Purpose

Final verification that personal blocks were preserved, system integrity is intact, and deployment completed successfully. Write evolution to history log. Surface changelog to user. Queue training prompts if present.

## Inputs

- `application_result` — From Step 06
- `files_processed` — From Step 06
- `personal_blocks_preserved` — From Step 06
- `personal_block_registry` — From Step 05
- `benchmark_snapshot` — Captured by this step (see Process section 3); eval harness baseline for comparative grading
- `validated_manifest` — From Step 01
- `snapshot_id` — From Step 03
- `evolution_id` — From Step 01
- `evolution_version` — From Step 01

## Process

### 1. Verify Personal Block Integrity

**Critical verification step — ensures no personal data was lost.**

For each file in `personal_block_registry`:

1. Read the deployed file: `{project-root}/{file.path}`
2. Parse file to extract personal blocks (same logic as Step 05)
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

Run the benchmark snapshot protocol in `references/benchmark-snapshot.md` (read it in this step): grade ungraded eval records, snapshot `systems/eval-harness/runs/` to a benchmark directory, compute baseline metrics, clean old benchmarks (keep current + prior 2), and log to state.yaml. Captures the baseline AFTER the evolution is applied so regression detection compares future runs against the post-deployment state.

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

**Format:** append the entry using the exact template in `references/history-entry-template.md` (read it before writing).

### 6. Update System Version

If evolution includes version bump:

Write or update `{project-root}/.ies-version`:

```
{evolution_version}
```

This tracks the current IES system version.

### 7. Surface Changelog to User

Present the changelog and (if present) training-prompts announcement using the exact formats in `references/output-templates.md` (read it in this step).

### 8. Queue Training Prompts (if present)

If manifest includes `training_prompts`:

1. Check if project has training system integration
2. If yes: Pass training_prompts to training system for progressive unlock
3. If no: Log prompts to `{project-root}/evolutions/training-queue.json` for manual review

### 9. Output Final Summary

Output the success or warnings summary using the exact templates in `references/output-templates.md`.

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

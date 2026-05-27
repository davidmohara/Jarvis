---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Summary & Close

## MANDATORY EXECUTION RULES

1. You MUST read accumulated-context from state.yaml — the summary is built from recorded data, not from memory.
2. You MUST deliver the summary before closing state — the controller needs it before the workflow ends.
3. You MUST set `status: complete` in state.yaml as the final action, after the summary is delivered.
4. You MUST write the skill-run signal last — it is the actual final write.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `accumulated-context` from state.yaml (all steps)
**Output:** Summary report delivered to controller; state closed; skill-run signal written

---

## YOUR TASK

### 1. Read accumulated-context

Read `workflows/error-improvement/state.yaml`. Pull:
- `entry_count_at_start`
- `analysis_period`
- `patterns_found` (count and top pattern)
- `approved_fixes` (count and list)
- `needs_your_call_decisions` (count and outcomes)
- `files_modified` (count and list)
- `assertions_total`, `assertions_passed`
- `months_compacted`, `entries_compacted`
- `compact_eligible_months` (to note if none were eligible)
- `session-started`

Also note: any open Needs Your Call items that received no decision (still pending for next cycle).

### 2. Deliver summary report

This is the complete picture of what happened — everything in one place.

```
## Error Improvement Cycle — [analysis_period]
Completed [date], [duration from session-started to now]

### What we started with
[entry_count_at_start] active entries ([date range])
[N] patterns identified — top: [category] → [failure_mode] ([N] occurrences)
Trend: [Improving / Stable / Degrading from Step 2 analysis]

### Fixes applied ([N])
[For each fix in approved_fixes — one line each:]
✓ [File] — [what changed] (addresses [N] entries)

[If none:]
No fixes applied — [reason: deferred by controller / no Apply Now items / etc.]

### Needs Your Call ([N] decisions)
[For each item with a decision:]
→ [pattern]: [decision made]

[If items remain undecided:]
Still open (carry to next cycle):
- [pattern description] — [N] occurrences

### Verification
[assertions_passed]/[assertions_total] assertions passed
[If any failed: list them here with status]

### Log compaction
[If months compacted:]
[entries_compacted] entries archived → [month list]
Remaining active entries: [current count]

[If no months eligible:]
No months eligible for compaction — all active entries are current-month or have open fixes.

### Evolution tracking
[N] files logged to pending-changes. Ready to package in the next evolution.

### Open items for next cycle
[List any Needs Your Call items with no decision, or patterns below threshold that are trending up]
[If none: "Log is clean — nothing deferred."]
```

### 3. Close state.yaml

Update `workflows/error-improvement/state.yaml`:

```yaml
status: complete
current-step: null
```

Also append final step timing:

```yaml
  step_timings:
    - step: step-07-summary
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
```

### 4. Close the eval record

Use `close-eval-record.py` to write the proper eval record. Build the `--steps` argument from `accumulated-context.step_timings` in state.yaml — comma-separated list of step names in order.

```bash
cd <IES root> && python3 systems/eval-harness/close-eval-record.py \
  --name error-improvement \
  --type workflow \
  --agent rigby \
  --status <success|partial|failure> \
  --trigger <manual|scheduled|weekly-review> \
  --started "<session-started from state.yaml>" \
  --steps "step-01-intake,step-02-analyze,step-03-triage,step-04-apply,step-05-verify,step-06-compact,step-07-summary"
```

Set `--status partial` if any Step 5 assertions failed but workflow completed with controller approval. Set `--status failure` only if the workflow could not produce its core outputs (analysis report, fix application).

The script will find the open eval record by `eval-record-id` from state.yaml (matching name + session) and close it, or create a new one on the Cowork path. Print what it returns (`closed: eval-...` or `created: eval-...`).

This call is always last — after state.yaml is closed.

---

## SUCCESS METRICS

- Summary report delivered with all sections populated from state.yaml data
- state.yaml `status: complete`
- Skill-run signal written

## FAILURE MODES

| Failure | Action |
|---------|--------|
| state.yaml missing or unreadable | Reconstruct summary from what was observed during this session. Note the state file issue. Still close and write signal. |
| state.yaml won't update to complete | Note it. The workflow is functionally done. Write the signal anyway. |
| Summary has gaps (a section's data wasn't recorded in state) | Fill what you can from session context. Mark missing data as "not recorded." Don't block on it. |
<!-- system:end -->

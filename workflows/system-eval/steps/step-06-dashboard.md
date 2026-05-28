---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 06: Dashboard, Close, Summary

## MANDATORY EXECUTION RULES

1. You MUST regenerate the dashboard before closing the eval record — the dashboard should reflect the grading and assertions completed in this run.
2. You MUST close the eval record via `close-eval-record.py` — do not leave it `in-progress`.
3. You MUST set `status: complete` in state.yaml — this is the terminal step.
4. You MUST deliver a summary to the controller — silence is not an option.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** All updated eval records + state.yaml accumulated context
**Output:** Updated dashboard HTML, closed eval record, final summary

---

## YOUR TASK

### 1. Regenerate the dashboard

Run the HTML generator:

```bash
python3 systems/eval-harness/generate-dashboard.py \
  --eval-dir systems/eval-harness/runs \
  --output systems/eval-harness/dashboard.html \
  --recent 100 \
  --period 30
```

Capture the exit code. If it fails, log the error — do not halt. Surface the path anyway, noting it may be stale.

Write the skill-run signal for `rigby-eval-dashboard`:

```json
{
  "skill": "rigby-eval-dashboard",
  "agent": "rigby",
  "trigger": "workflow:system-eval",
  "started": "<step start time>",
  "completed": "<ISO-8601 UTC now>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": [],
  "records_visualized": <N from score output>,
  "output_path": "systems/eval-harness/dashboard.html"
}
```

Write to `systems/eval-harness/skill-runs/rigby-eval-dashboard-latest.json`.

### 2. Close this workflow's eval record

Read `eval-record-id` from state.yaml (set by Step 1). Try the close script first:

```bash
python3 systems/eval-harness/close-eval-record.py \
  --name system-eval \
  --type workflow \
  --agent rigby \
  --status <success|partial|failure> \
  --trigger <manual|scheduled> \
  --started "<session-started from state.yaml>" \
  --steps "step-01-intake,step-02-assert,step-03-grade,step-04-score,step-05-analyze,step-06-dashboard"
```

**If the script creates a new record instead of closing the existing stub** (Cowork session_id mismatch — check the output; it will say "created:" instead of "closed:"), close the stub directly by writing to `systems/eval-harness/runs/{eval-record-id}.json` and updating these fields:
```json
{
  "completed": "<ISO-8601 UTC now>",
  "duration_seconds": <seconds from session-started to now>,
  "status": "<success|partial|failure>",
  "assessment": { "mechanical": { "completed": true, "all_steps_finished": true } }
}
```
Then delete the spurious new record the script created (it will be a fresh `eval-{timestamp}-{suffix}.json` written within the last 60 seconds).

Determine `--status`:
- `success` — all six steps completed with no blocking failures
- `partial` — one or more steps completed with non-blocking failures (e.g., score script errored but continued)
- `failure` — a step had to be skipped due to a blocking error

### 3. Set state.yaml to complete

```yaml
status: complete
current-step: null
accumulated-context:
  step_timings:
    - step: step-06-dashboard
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 4. Deliver summary

Output the following to the controller:

```
[Rigby]: System eval complete.

Records assessed: {records_total from state.yaml}
  Assertions run: {total_assertions_evaluated} across {total_records_asserted} records
  Grades assigned: {total_graded} ({grade_distribution: A:{N} B:{N} C:{N} D:{N} F:{N}})
  Avg composite score: {batch_average from scoring, or "N/A" if script failed}

Top finding: {top_recommendation from analysis}
Analysis report: {report_path}
Dashboard: systems/eval-harness/dashboard.html
```

If any steps had partial failures, append:
```
Partial failures:
  - {step}: {error description}
```

---

## SUCCESS METRICS

- Dashboard HTML regenerated
- Eval record closed (status: success, partial, or failure — not in-progress)
- state.yaml set to complete
- Summary delivered

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `generate-dashboard.py` fails | Log error. Surface the stale dashboard path with a note. Continue to close and summary. |
| `close-eval-record.py` fails | Manually write the final state to the eval record in `runs/{eval-record-id}.json`. Set `status` and `completed` fields directly. Log that the script failed. |
| state.yaml write fails | Report it in the summary. Do not silently accept an unclosed state. |
<!-- system:end -->

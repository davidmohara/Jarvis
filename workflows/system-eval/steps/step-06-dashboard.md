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

### 2. Patch and sync the dashboard to the pinned Cowork artifact

#### 2a. Patch the Chart.js script tag

Run this sed replacement on the generated file before pushing to the artifact:

```bash
sed -i '' \
  's|chart\.js@4\.4\.0/dist/chart\.umd\.min\.js|chart.js@4.5.0/dist/chart.umd.js" integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" crossorigin="anonymous|' \
  systems/eval-harness/dashboard.html
```

> **Note (2026-07-08):** `generate-dashboard.py` was patched to emit the approved Chart.js 4.5.0 tag directly. This sed command is a no-op on freshly generated dashboards but is kept as a safety net in case an older version of the script is used.

#### 2b. Push to the pinned Cowork artifact

**This step is MANDATORY. Do not skip it.**

First, load the tool schema (required before every call — it is always deferred):

```
ToolSearch with query "select:mcp__cowork__update_artifact"
```

Then call `mcp__cowork__update_artifact` with:

- **id:** `rigby-eval-dashboard`
- **html_path:** `systems/eval-harness/dashboard.html`
- **update_summary:** Brief description of what this run changed — include run date, records visualized, grades assigned, and avg score. Example: `"2026-07-08 run: 12 records, A:3 B:5 C:2 D:1 F:1, avg 0.74"`

**Verification:** After calling update_artifact, confirm the call succeeded. If the tool returns an error, retry once. If it fails again, log the failure in state.yaml under `dashboard_artifact_error` and continue — do not halt.

If the artifact update succeeded, write `dashboard_artifact_updated: true` to state.yaml. If it failed, write `dashboard_artifact_updated: false` with the error message.

### 3. Write working memory

Write a working memory file to `memory/working/` using this filename pattern:

```
system-eval-YYYY-MM-DD-HHmmss.md
```

Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "rigby-{YYYY-MM-DD}-{HHmmss}"
agent-source: rigby
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "System eval — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing records assessed, grades assigned, avg score, top pattern found, and any blocking failures. Keep it under 200 words.

After writing, verify the file exists and is >200 bytes via Bash (`wc -c {path}`). If verification fails, log `working-memory-status: failed` in state.yaml and continue — do not halt.

### 4. Close this workflow's eval record

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

### 5. Set state.yaml to complete

```yaml
status: complete
current-step: null
accumulated-context:
  step_timings:
    - step: step-06-dashboard
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 6. Deliver summary

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

### 7. Weekly feedback prompt (Option C)

After delivering the summary, surface up to 3 eval records from the past 7 days that:
- Have `controller_feedback.rating == null`
- Have a composite score below 0.75 (most in need of signal)
- Are NOT orphaned abort stubs (must have at least 1 step)

Sort by score ascending (lowest first — most in need of feedback).

Output this prompt to the controller:

```
[Rigby]: Quick feedback request — {N} recent runs could use a rating.
For each, reply "positive", "negative", or "skip":

1. {eval_id} — {name} on {date}, score {score}, grade {grade}
   "{grader_notes truncated to 80 chars}"

2. {eval_id} — ...

3. {eval_id} — ...

(Or reply "skip all" to defer.)
```

**If this is a scheduled (headless) run:** omit this prompt entirely. The controller is not present. Write a note to state.yaml under `feedback_prompt: skipped (headless)` and stop.

**If this is a manual/interactive run:** wait for the controller's reply. For each rating received, write it back to the eval record immediately:

```python
# For each rated record:
record["assessment"]["controller_feedback"]["rating"] = "{positive|negative}"
record["assessment"]["controller_feedback"]["timestamp"] = "{ISO-8601 now}"
# Write back to systems/eval-harness/runs/{eval_id}.json
```

Write `feedback_prompt: complete` to state.yaml after collecting ratings. If the controller replies "skip all" or gives no reply within the same turn, write `feedback_prompt: deferred`.

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
| Artifact update fails | Log the error to state.yaml under `dashboard_artifact_error`. Continue — dashboard on disk is the source of truth; artifact sync is non-blocking. |
| `close-eval-record.py` fails | Manually write the final state to the eval record in `runs/{eval-record-id}.json`. Set `status` and `completed` fields directly. Log that the script failed. |
| state.yaml write fails | Report it in the summary. Do not silently accept an unclosed state. |
<!-- system:end -->

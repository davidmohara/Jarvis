---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 04: Compute Composite Scores

## MANDATORY EXECUTION RULES

1. You MUST use `score_eval.py` for all composite score computations — never reimplement the formula manually.
2. You MUST score all closed records in `systems/eval-harness/runs/`, not just the ones updated in Steps 2-3.
3. You MUST capture the score output from the script — do not discard it.
4. If `score_eval.py` fails, report the error and advance — do not halt the workflow over a scoring failure.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** All closed eval records in `systems/eval-harness/runs/`
**Output:** Composite scores logged to state.yaml; script output surfaced in Step 6 summary

---

## CONTEXT BOUNDARIES

This step runs a Python script. It does not write to individual eval records — the score is computed and reported, not stored in the record file. The composite score is surfaced in the dashboard (Step 6) and the summary report.

---

## YOUR TASK

### 1. Collect all closed record IDs

List all files matching `systems/eval-harness/runs/eval-*.json`. For each, read the `status` field. Collect IDs where status is NOT `in-progress`.

Exclude the current system-eval run's own eval record (identified by the eval-record-id in state.yaml).

### 2. Run score_eval.py in batch mode

```bash
python3 systems/eval-harness/scoring/score_eval.py --batch <id1> <id2> <id3> ...
```

Pass all closed record IDs. Capture stdout.

The script outputs JSON:
```json
{
  "records": [
    {
      "id": "<eval-id>",
      "score": 0.72,
      "components": {
        "mechanical": 0.25,
        "assertion_rate": 0.35,
        "grade_score": 0.12,
        "feedback": 0.0,
        "no_errors": 0.10
      },
      "weights_used": { ... },
      "missing_components": ["feedback"]
    }
  ],
  "batch_average": 0.68,
  "count": 7
}
```

### 3. Store scoring results in state.yaml

```yaml
accumulated-context:
  scoring:
    records_scored: <N>
    batch_average: <float>
    score_by_id:
      <eval-id>: <score>
      <eval-id>: <score>
    score_script_error: null  # or error message if script failed
  step_timings:
    - step: step-04-score
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 4. Advance state

Update state.yaml:
```yaml
current-step: step-05-analyze
```

---

## SUCCESS METRICS

- score_eval.py ran successfully (or failure logged cleanly)
- All closed records scored
- Results stored in state.yaml
- Batch average captured for summary

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `score_eval.py` not found | Log error: "score_eval.py not found at expected path." Store `score_script_error` in state.yaml. Advance to Step 5. |
| `score_eval.py` fails with exception | Capture stderr. Store error in `score_script_error`. Advance to Step 5. Scores will be absent from summary. |
| No closed records to score | Log: "No closed records to score." Advance to Step 5. |
| Batch is too large (>50 records) | Split into batches of 20, run sequentially, merge results. |

## NEXT STEP

[Step 05 — Analyze](step-05-analyze.md)
<!-- system:end -->

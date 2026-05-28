---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 01: Intake & Inventory

## MANDATORY EXECUTION RULES

1. You MUST open an eval record before doing anything else — this run must be self-tracking.
2. You MUST inventory all records in `systems/eval-harness/runs/` and classify each one.
3. You MUST skip records with `status: in-progress` — they are not yet closed and not ready to assess.
4. You MUST write the inventory results to state.yaml before advancing.
5. If the runs directory is empty or has no closed records, exit cleanly — nothing to do.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `systems/eval-harness/runs/*.json`
**Output:** Classification of all closed eval records by what coverage is missing

---

## CONTEXT BOUNDARIES

This step only reads. It does not grade, assert, score, or write to any eval record. Its only writes are the new eval record (opened via `new-eval.py`) and state.yaml.

---

## YOUR TASK

### 1. Open this workflow's eval record

```bash
cd <IES root> && python3 systems/eval-harness/new-eval.py
```

Capture the returned eval id. Open the created file and update:

```json
{
  "type": "workflow",
  "name": "system-eval",
  "agent": "rigby",
  "trigger": "<manual | scheduled>",
  "status": "in-progress"
}
```

### 2. Initialize state.yaml

Write initial state:

```yaml
workflow: system-eval
agent: rigby
status: in-progress
session-started: <ISO-8601 UTC now>
session-id: rigby-<YYYY-MM-DD-HHmmss>
eval-record-id: <eval id from new-eval.py>
current-step: step-01-intake
original-request: <what triggered this run>
accumulated-context:
  step_timings:
    - step: step-01-intake
      started: <ISO-8601 UTC now>
      completed: ~
```

### 3. Inventory eval records

Read all files matching `systems/eval-harness/runs/eval-*.json`.

For each record, classify its coverage gaps:

| Gap Type | Condition |
|----------|-----------|
| `needs_assertions` | `assessment.structural.assertions_checked == 0` AND an assertion definition file exists for this workflow/skill in `systems/eval-harness/assertions/` |
| `needs_grade` | `assessment.grading.grade == null` AND `status` is `success`, `partial`, or `failure` (not `in-progress`) |
| `needs_score` | No composite score data present (eval harness does not currently store scores in the record — Step 4 will compute and log them separately) |
| `complete` | Has assertions, has grade — nothing to do for this record |
| `skip` | `status: in-progress` — not closed yet, skip |

A single record can appear in multiple gap buckets (e.g., needs both assertions and grade).

Store the classification in state.yaml:

```yaml
accumulated-context:
  records_total: <N>
  records_skipped_in_progress: <N>
  needs_assertions: [<eval-id>, ...]
  needs_grade: [<eval-id>, ...]
  records_complete: <N>
  assertion_files_available: [<workflow-name>, ...]  # workflows with assertion definitions
```

### 4. Early exit check

If `needs_assertions` is empty AND `needs_grade` is empty:
- All records are fully assessed — no grading or assertion work needed.
- Skip Steps 2 and 3, but still run Steps 4, 5, and 6. Composite scores should always be refreshed, and analysis + dashboard should always reflect current state.
- Surface: "[Rigby]: All records fully assessed. Skipping assertion and grading steps — running score, analyze, and dashboard refresh."
- Update `current-step: step-04-score` in state.yaml.

### 5. Update state.yaml for advance

```yaml
current-step: step-02-assert
accumulated-context:
  step_timings:
    - step: step-01-intake
      started: <start>
      completed: <ISO-8601 UTC now>
```

---

## SUCCESS METRICS

- Eval record opened and ID captured
- All records in `runs/` classified
- Inventory written to state.yaml
- No writes to any existing eval record

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `runs/` directory is empty | Exit cleanly: "[Rigby]: No eval records found. Nothing to assess." Set `status: complete` in state.yaml. |
| `new-eval.py` fails | Report error and halt: "[Rigby]: Could not open self-tracking eval record — {error}. Aborting." Set `status: aborted`. |
| A record file is malformed JSON | Log the filename, skip it, continue. Note the malformed file in state.yaml under `malformed_records`. |

## NEXT STEP

[Step 02 — Assert](step-02-assert.md)
<!-- system:end -->

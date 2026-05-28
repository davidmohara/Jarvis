---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 02: Structural Assertions

## MANDATORY EXECUTION RULES

1. You MUST only run assertions on records listed in `needs_assertions` from state.yaml — do not re-assert already-checked records.
2. You MUST load the assertion definition file for each workflow/skill before evaluating. If no definition exists, skip that record.
3. You MUST write assertion results back to each eval record's `assessment.structural` block.
4. You MUST NOT modify any other field in the eval record — only `assessment.structural`.
5. If `needs_assertions` is empty, skip this step and advance immediately.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `needs_assertions` list from state.yaml + assertion definition files in `systems/eval-harness/assertions/`
**Output:** Updated `assessment.structural` blocks in eval records

---

## CONTEXT BOUNDARIES

This step evaluates file-system assertions against workflow outputs. It checks whether expected output files exist, meet minimum size thresholds, and contain expected patterns. It does not read content for quality — that's grading (Step 3).

---

## YOUR TASK

### 1. Load work list

Read `accumulated-context.needs_assertions` from state.yaml. If empty, advance to Step 3.

### 2. For each record needing assertions

**a. Load the eval record**

Read `systems/eval-harness/runs/{eval-id}.json`. Extract `name` (workflow/skill name).

**b. Load the assertion definition**

Read `systems/eval-harness/assertions/{name}.json`. If no file exists for this workflow/skill, skip this record — log it in state.yaml under `no_assertion_definition`.

**c. Evaluate each assertion**

For each assertion in the definition file, evaluate the check type:

| Check Type | Evaluation Method |
|------------|------------------|
| `yaml_field_equals` | Read the YAML file at `path`, parse the `field`, compare to `value` |
| `file_exists` | Check if a file matching the glob pattern at `path` exists |
| `file_min_bytes` | Check if the file at `path` exists and its size >= `min_bytes` |
| `file_contains` | Check if the file at `path` contains text matching the `pattern` regex |
| `file_exists_pattern` | Check if any file matching glob at `path` has a JSON field `match_field` equal to `match_value` |
| `directory_file_count_max` | Count files in `path` matching `pattern` with optional `field_filter`; confirm count <= `max_count` |

For glob patterns, use the most recent file that matches (sorted by modification time, newest first). If no file matches a glob, the assertion fails.

**d. Build assertion results array**

```json
[
  { "assertion": "{assertion description}", "passed": true },
  { "assertion": "{assertion description}", "passed": false }
]
```

**e. Update the eval record's structural block**

```json
{
  "expected_outputs_written": <true if all file_exists assertions pass>,
  "outputs_non_empty": <true if all file_min_bytes assertions pass>,
  "assertions_checked": <total count>,
  "assertions_passed": <passed count>,
  "assertion_results": [...]
}
```

Write the updated eval record back to `systems/eval-harness/runs/{eval-id}.json`. Only update the `assessment.structural` block — leave all other fields unchanged.

### 3. Tally results

Track in state.yaml:

```yaml
accumulated-context:
  assertions_run:
    total_records_asserted: <N>
    total_assertions_evaluated: <N>
    total_assertions_passed: <N>
    records_fully_passing: <N>
    records_with_failures: <N>
    no_assertion_definition: [<eval-id>, ...]
  step_timings:
    - step: step-02-assert
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 4. Advance state

Update state.yaml:
```yaml
current-step: step-03-grade
```

---

## SUCCESS METRICS

- All records in `needs_assertions` have been evaluated (or skipped with reason)
- Each evaluated record's `assessment.structural` block is fully populated
- Assertion tally written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Assertion definition file is malformed JSON | Skip that record, log under `malformed_assertion_files` in state.yaml. Continue. |
| File read fails during assertion evaluation | Treat assertion as failed. Note in `assertion_results` with reason. |
| Eval record write fails | Retry once. If still fails, log the eval-id in `failed_writes` in state.yaml. Continue with remaining records. |
| All records in `needs_assertions` have no definition file | Log this, advance to Step 3. |

## NEXT STEP

[Step 03 — Grade](step-03-grade.md)
<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. Score ALL records in BOTH the train batch AND selection split
3. The baseline score used for gating is the **selection split average**, not the train batch
4. Never modify any skill files in this step
5. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `accumulated-context.skill_id`, `eval_record_ids` (train), `selection_record_ids` (selection) |
| Output | `baseline_score` (selection split average), `baseline_score_breakdown`, `best_score`, `best_skill_path` |

## CONTEXT BOUNDARIES

This step scores the current skill version using existing eval records. It does not run new skill executions. It does not propose or apply any edits.

## YOUR TASK

### 1. Load Eval Records

For each record ID in `selection_record_ids` (the gate split):

Read `systems/eval-harness/runs/{id}.json`. If the record is not found there, check structured eval directories under `systems/evals/`.

Extract: `status`, `assessment.structural`, `assessment.grading`, `assessment.controller_feedback`, `assessment.mechanical`

### 2. Compute Score Per Record

Read `systems/eval-harness/scoring/FORMULA.md` when scoring each record — that file is the single statement of the composite formula (weights, null-handling, success/failure threshold), shared with the build path. Never restate the weights locally.

If all records use assertion_rate = 0.5 (no assertions defined): note `no_assertions_defined: true` in output and surface to controller:

> "[Rigby]: No structural assertions are defined for '{skill_id}'. Scores will rely on mechanical pass/fail and grading only. Consider authoring assertions via `rigby-capability-build` to improve scoring signal."

Proceed despite the warning — optimization can still work with grading-only signal.

### 3. Compute Baseline Score

```
baseline_score = average(scores across all selection_record_ids)
```

Also compute for train batch records (for informational use in reflection, not for gating).

Store: `baseline_score`, `baseline_score_breakdown` (per-record scores and component breakdown)

### 4. Initialize Best Score

Set `best_score = baseline_score`. Set `best_skill_path = skill_path` (the current unmodified SKILL.md).

This is the threshold: a candidate skill must exceed `best_score` to be accepted.

### 5. Write State

Update `state.yaml`:
- `accumulated-context.baseline_score`
- `accumulated-context.best_score`
- `accumulated-context.best_skill_path`
- `current-step: step-03-reflect`

Report to controller:

> "[Rigby]: Baseline established. '{skill_id}' scores {baseline_score:.2f} across {N} selection records. Beginning round 1 of {total_rounds}."

## SUCCESS METRICS

- All selection records scored with documented component breakdown
- `baseline_score` is a float between 0.0 and 1.0
- `best_score` initialized to baseline
- State updated

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Selection record not found on disk | Skip it. Log to `missing_records`. If >50% missing, surface to controller before proceeding. |
| All records score 1.0 (ceiling) | Surface: "'{skill_id}' is already scoring at ceiling. Optimization may not find room to improve. Continue?" |
| All records score 0.0 | Surface: "All records show complete failure. Check if the skill is being invoked correctly before optimizing." |

## NEXT STEP

`step-03-reflect.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

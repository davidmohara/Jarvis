---
status: not-started
started-at: ~
completed-at: ~
outputs:
  skill_id: null
  skill_path: null
  edit_budget: null
  total_rounds: null
  epoch_size: null
  eval_record_ids: []
  selection_record_ids: []
  rejected_edits_path: null
  slow_update_history_path: null
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before any action
2. Confirm the target skill exists before proceeding — halt if not found
3. Separate eval records into a **train batch** (reflection evidence) and a **selection split** (gate evaluation) — never use the same records for both
4. Write `status: complete` and `completed-at` after all outputs are stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | Controller request specifying target skill (and optionally: edit_budget, total_rounds, epoch_size) |
| Output | Populated state.yaml accumulated-context; eval record IDs partitioned into train/selection splits |

## CONTEXT BOUNDARIES

This step configures the optimization run. It does not modify any skill files, does not score anything, and does not propose edits. It only reads the current skill and eval records to set up the run parameters.

## YOUR TASK

### 1. Confirm Target Skill

Read the original request from `state.yaml accumulated-context.original-request` (or the controller's current message). Extract the `skill_id`.

Locate the skill at `skills/{skill_id}/SKILL.md`. If the path does not exist, check `skills/{skill_id}/` for a file with a different name. If still not found, halt:

> "[Rigby]: Cannot find skill '{skill_id}'. Check the skill ID and try again."

Read the skill file. Compute an approximate token count (character count ÷ 4). If the skill exceeds `max_token_budget` (2000 tokens) already, surface a warning — the skill may need pruning before optimization.

Store: `skill_id`, `skill_path`

### 2. Configure Run Parameters

Apply defaults unless the controller specified overrides:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `edit_budget` | 4 | Maximum edits proposed per round (the "learning rate") |
| `total_rounds` | 4 | Number of optimization rounds to run |
| `epoch_size` | 2 | Rounds per epoch (slow update runs at epoch boundary) |
| `max_token_budget` | 2000 | Token ceiling for the final optimized skill |

Store these in `accumulated-context`.

### 3. Gather Eval Records

Scan `systems/eval-harness/runs/` for eval records matching this skill:

- Filter by: `name` equals `skill_id`, OR `tags` contains `skill_id`
- Filter by: `version_hash` — prefer records produced by the current version of the skill (hash the current SKILL.md with sha256); include older-version records only if fewer than 6 current-version records exist
- Sort by `started` descending (most recent first)
- Take up to 20 records total

Also scan `systems/evals/` for structured eval work directories matching the skill name. Include any eval records found there.

If fewer than 4 records are found total: surface to controller:

> "[Rigby]: Only {N} eval records found for '{skill_id}'. Optimization works best with 6+ records. Run the skill a few more times and return, or proceed with limited data?"

Wait for confirmation before continuing with fewer than 4 records.

### 4. Partition into Train and Selection Splits

Split the gathered records:

- **Train batch** (reflection evidence): 70% of records, randomly selected. Minimum 3 records.
- **Selection split** (gate evaluation): remaining 30%. Minimum 2 records.

If total records < 6: use all records for both splits (train = all, selection = all). Note in output: `small_dataset: true`.

Store: `eval_record_ids` (train batch), `selection_record_ids` (selection split)

### 5. Prepare Candidate and Buffer Paths

Set paths for files this workflow will create:

```
rejected_edits_path: skills/{skill_id}/rejected-edits.json
slow_update_history_path: skills/{skill_id}/slow-update-history.json
```

Create the `skills/{skill_id}/candidates/` directory if it doesn't exist.

If `rejected-edits.json` does not exist yet, create it with an empty structure:

```json
{
  "skill_id": "<skill_id>",
  "created": "<ISO-8601 timestamp>",
  "entries": []
}
```

### 6. Write State

Update `state.yaml` `accumulated-context` with all stored values. Write `current-step: step-02-score-baseline`.

## SUCCESS METRICS

- Skill file located and readable
- At least 4 eval records gathered (or controller confirmed fewer)
- Train/selection split defined with no overlap
- Candidate directory created
- Rejected-edits buffer initialized
- state.yaml updated with all outputs

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Skill not found | Halt. Report exact path searched. |
| Zero eval records | Halt. Instruct: "Run '{skill_id}' at least 4 times, then return to optimize." |
| Controller provides invalid skill_id | Ask for clarification. Show available skills from `skills/_manifest.jsonl`. |
| state.yaml write fails | Halt. Do not proceed without persisted state. |

## NEXT STEP

`step-02-score-baseline.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

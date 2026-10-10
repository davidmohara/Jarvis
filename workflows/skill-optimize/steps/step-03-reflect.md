---
status: not-started
started-at: ~
completed-at: ~
outputs:
  reflect_output_path: null
  edits_proposed: 0
  insufficient_data: false
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. Read `rigby-skill-reflect/SKILL.md` fully before invoking the skill
3. Pass the train batch IDs (not selection IDs) to the reflection skill
4. Do not modify the SKILL.md being optimized in this step
5. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `accumulated-context.skill_id`, `skill_path`, `eval_record_ids` (train), `edit_budget`, `rejected_edits_path`, `rounds_completed` |
| Output | Edit proposal file at `skills/{skill_id}/candidates/round-{N}-edits.json` |

## CONTEXT BOUNDARIES

This step invokes the reflection skill and waits for the edit proposal output. It does not apply edits or modify the skill. It only calls the reflection skill and confirms the output was written.

## YOUR TASK

### 1. Load Reflection Skill

Read `skills/rigby-skill-reflect/SKILL.md` fully. This contains the complete reflection protocol.

### 2. Set Round Number

`round_number = accumulated-context.rounds_completed + 1`

The round number is used to name the output file: `skills/{skill_id}/candidates/round-{round_number}-edits.json`

### 3. Pass Inputs to Reflection Skill

Set in `state.yaml accumulated-context` for the reflection skill to read:
- `skill_id` — already set
- `skill_path` — already set
- `eval_record_ids` — the **train batch** (not selection split)
- `edit_budget` — from accumulated-context
- `rejected_edits_path` — from accumulated-context
- `round_number` — computed above

### 4. Execute rigby-skill-reflect

Follow the rigby-skill-reflect SKILL.md protocol completely:

- Load target skill (Step 1 of that skill)
- Load eval records (Step 2)
- Load session transcripts (Step 3)
- Partition into minibatches (Step 4)
- Failure analysis (Step 5)
- Success analysis (Step 6)
- Load rejected-edit buffer (Step 7)
- Merge and rank edits (Step 8)
- Format and write output to `skills/{skill_id}/candidates/round-{round_number}-edits.json` (Step 9)

### 5. Confirm Output Written

Verify the output file exists. Read it and confirm:
- `edits` array is present (may be empty if `insufficient_data: true`)
- `eval_batch.total` matches the number of train records passed in
- `insufficient_data` field is present

Store in this step's outputs:
- `reflect_output_path`: `skills/{skill_id}/candidates/round-{round_number}-edits.json`
- `edits_proposed`: `edits_after_budget` from the output file
- `insufficient_data`: from the output file

### 6. Handle Insufficient Data

If `insufficient_data: true`:

> "[Rigby]: Not enough trajectory data to reflect meaningfully this round. Skipping to report — add more eval records and retry."

Update state: `current-step: step-08-report`. Do not proceed to step-04.

### 7. Handle Zero Edits Proposed

If `edits_proposed = 0` (but `insufficient_data: false`):

This means the reflection found no patterns not already covered. Log it. Increment `consecutive_zero_edit_rounds`. Proceed to step-04 — the gate will confirm no change.

### 8. Write State

Update `state.yaml` `current-step: step-04-apply-candidate`.

## SUCCESS METRICS

- Reflection output file written at expected path
- `edits_proposed` captured
- State updated

## FAILURE MODES

| Failure | Action |
|---------|--------|
| rigby-skill-reflect SKILL.md not found | Halt. Report: "Reflection skill missing. Cannot proceed." |
| Output file not written after reflection | Retry once. If still missing, halt and surface error. |
| Reflection produces malformed JSON | Halt. Log: "Reflection output is not valid JSON at {path}. Manual review required." |

## NEXT STEP

`step-04-apply-candidate.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs:
  candidate_path: null
  edits_applied: 0
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. NEVER overwrite the live `SKILL.md` in this step — write to `candidates/` only
3. Never modify content inside `<!-- SLOW_UPDATE_START -->` / `<!-- SLOW_UPDATE_END -->` markers
4. Apply edits in priority order (index 0 first)
5. If an edit's `target` text cannot be found verbatim in the skill, skip that edit and log it
6. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | Current SKILL.md content + edit proposals from `candidates/round-{N}-edits.json` |
| Output | Candidate skill version at `skills/{skill_id}/candidates/round-{N}-candidate.md` |

## CONTEXT BOUNDARIES

This step produces a candidate skill file only. The live SKILL.md is not touched. The validation gate in step-06 decides whether this candidate becomes the new SKILL.md.

## YOUR TASK

### 1. Load Current Best Skill

Read the file at `accumulated-context.best_skill_path`. This is the current best accepted skill (starts as the original SKILL.md, advances as rounds are accepted).

Extract the content, preserving all markers exactly:
- `<!-- system:start/end -->` and `<!-- personal:start/end -->` markers for evolution compatibility
- `<!-- SLOW_UPDATE_START/END -->` markers for the slow-update protected region

### 2. Load Edit Proposals

Read `skills/{skill_id}/candidates/round-{round_number}-edits.json`. Extract the `edits` array.

If `edits` is empty: write the current best skill as the candidate unchanged (it will score identically to baseline and be rejected in step-06, which is the correct behavior — no wasted commits).

Set `candidate_path = skills/{skill_id}/candidates/round-{round_number}-candidate.md`

### 3. Apply Edits in Priority Order

Process each edit in `priority_rank` order (lowest rank number first):

**`append`**: Add `content` at the end of the main skill body, before the `## SKILL COMPLETE` section if one exists. Do not append inside the slow-update protected region.

**`insert_after`**: Find the first occurrence of `target` text in the main body (outside protected regions). Insert `content` immediately after it (new line). If `target` not found: skip, log to `skipped_edits[]`.

**`replace`**: Find the first occurrence of `target` text (outside protected regions). Replace it with `content`. If `target` not found: skip, log to `skipped_edits[]`.

**`delete`**: Find the first occurrence of `target` text (outside protected regions). Remove it. If `target` not found: skip, log to `skipped_edits[]`.

After each operation, verify the resulting text is valid markdown (no unclosed tags, no broken section structure).

### 4. Validate Candidate

After applying all edits:

1. Confirm `<!-- SLOW_UPDATE_START/END -->` content is unchanged (if it existed)
2. Confirm `<!-- system:start/end -->` and `<!-- personal:start/end -->` markers are all paired and intact
3. Compute approximate token count. If it exceeds `max_token_budget` (2000 tokens): log a warning but proceed — the gate will decide whether to accept
4. Count how many edits were applied vs. skipped

### 5. Write Candidate File

Write the modified skill content to `skills/{skill_id}/candidates/round-{round_number}-candidate.md`.

Add a header comment for traceability (as an HTML comment, not visible in skill rendering):

```
<!-- CANDIDATE: round={round_number}, edits_applied={N}, generated={ISO-8601 timestamp} -->
```

### 6. Write State

Update `state.yaml`:
- `accumulated-context.candidate_path` (for step-05 to reference)
- `current-step: step-05-score-candidate`

Store in this step's outputs:
- `candidate_path`
- `edits_applied`: count of successfully applied edits

## SUCCESS METRICS

- Candidate file written at `skills/{skill_id}/candidates/round-{N}-candidate.md`
- All protected regions unchanged
- All markdown markers intact
- `edits_applied` count accurate

## FAILURE MODES

| Failure | Action |
|---------|--------|
| best_skill_path file not found | Halt. The best skill to edit from is missing. |
| All edits skipped (targets not found) | Write candidate = current skill unchanged. Log: "All proposed edits had unfindable targets — candidate is identical to current." Proceed to gate (will reject, correctly). |
| Candidate write fails | Halt. Do not proceed without persisted candidate. |
| Protected region contaminated | Halt immediately. Log error. Restore candidate from best_skill_path. Do not proceed. |

## NEXT STEP

`step-05-score-candidate.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

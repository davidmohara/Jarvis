---
status: not-started
started-at: ~
completed-at: ~
outputs:
  candidate_score: null
  candidate_score_breakdown: {}
  delta: null
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. Score candidate against the **selection split** (same records used for baseline) — not the train batch
3. Use the same scoring formula as step-02 — no deviations
4. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `candidate_path`, `selection_record_ids`, `best_score` |
| Output | `candidate_score`, `delta` (candidate_score − best_score) |

## CONTEXT BOUNDARIES

This step scores the candidate skill against existing eval records. It does not run new skill executions — it uses the same existing records the baseline was scored against. The score here determines whether the candidate is accepted in step-06.

Note: In a full SkillOpt implementation, you would re-run the skill with the candidate version and collect new trajectories. In IES, we use existing records as the held-out validation set because Jarvis runs in a real-work context where synthetic re-runs aren't practical. This is a pragmatic adaptation — the signal is weaker but the gate still prevents regression.

## YOUR TASK

### 1. Load Candidate Skill

Read `accumulated-context.candidate_path`. Note any changes from the current best skill (for the report step).

### 2. Score Candidate Against Selection Records

For each record in `selection_record_ids`:

Apply the same composite scoring formula:

```
score = (mechanical × 0.25) + (assertion_rate × 0.35) + (grade_score × 0.20) + (feedback × 0.10) + (no_errors × 0.10)
```

**Important note on scoring with existing records:** Because the records were generated with the *current* skill (not the candidate), the scores reflect the current skill's behavior. The candidate score will be identical to the baseline unless:

1. The candidate edits address assertions that the current skill was failing (in which case we can manually check if the edit would have fixed those specific assertion failures)
2. The controller has provided new feedback ratings on recent runs
3. New eval records have been added since baseline was scored

Check each of the above before declaring the candidate score identical to baseline. If new records exist in `systems/eval-harness/runs/` that weren't in the original batch: include them in scoring.

**Simulated improvement assessment:** For each failed assertion in the selection records, read the assertion definition from `systems/eval-harness/assertions/{skill_id}.json`. Then examine each accepted edit — does the edit directly address the procedural gap that caused this assertion to fail? If yes: credit that assertion as "would pass with candidate" and score it as passed. Document this as a `simulated_improvement` in the breakdown.

This simulation is conservative — only credit improvements that are clearly addressed by a specific edit.

### 3. Compute Delta

```
delta = candidate_score − best_score
```

Store: `candidate_score`, `candidate_score_breakdown`, `delta`

### 4. Write State

Update `state.yaml`:
- `accumulated-context.last_round_delta = delta`
- `current-step: step-06-gate`

Report delta to context for the gate step.

## SUCCESS METRICS

- Candidate scored against all selection records
- `delta` computed accurately
- Simulated improvements documented if any

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Candidate file not found | Halt. Step-04 output is missing. |
| Selection records all missing | Halt. Cannot score without records. Surface to controller. |
| Delta computation error | Log the error, set delta = 0, surface for manual review. |

## NEXT STEP

`step-06-gate.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

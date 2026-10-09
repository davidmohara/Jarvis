---
name: skill-optimize
description: SkillOpt-style optimization loop for IES skill documents. Reads eval records as rollout evidence, reflects on failures and successes, proposes bounded edits, gates acceptance on score improvement, accumulates rejected edits as negative feedback, and runs epoch-wise slow updates for durable procedural lessons.
agent: rigby
model: sonnet
---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | Tool/Path | Purpose |
|--------|-----------|---------|
| Target skill | `skills/{skill_id}/SKILL.md` | The skill document being optimized |
| Eval records | `systems/eval-harness/runs/*.json` | Rollout evidence (scored trajectories) |
| Session transcripts | `memory/sessions/index.json` | Trajectory detail for reflection |
| Rejected edits buffer | `skills/{skill_id}/rejected-edits.json` | Negative feedback from prior rounds |
| Slow-update history | `skills/{skill_id}/slow-update-history.json` | Prior epoch guidance for meta update |
| Pending changes log | `evolutions/.pending-changes.json` | Tracks files created by this workflow |

### Paths

```
workflows/skill-optimize/
├── workflow.md          ← this file
├── state.yaml           ← execution state
└── steps/
    ├── step-01-setup.md     ← configure target and eval batch
    ├── step-02-score-baseline.md   ← compute baseline score
    ├── step-03-reflect.md   ← invoke rigby-skill-reflect
    ├── step-04-apply-candidate.md  ← write candidate skill version
    ├── step-05-score-candidate.md  ← score candidate vs baseline
    ├── step-06-gate.md      ← accept or reject candidate edits
    ├── step-07-slow-update.md      ← epoch-wise durable consolidation
    └── step-08-report.md    ← surface results and next actions
```

### Key Metrics

- **Baseline score**: composite score of current skill across the eval batch
- **Candidate score**: composite score of candidate skill across same eval batch
- **Delta**: candidate_score − baseline_score (must be > 0 to accept)
- **Accepted edits**: count of edits committed to SKILL.md this round
- **Rounds run**: how many optimization rounds have completed for this skill

---

## STATE CHECK

Before starting any step, read `state.yaml` and apply the correct case:

| State | Action |
|-------|--------|
| `status: in-progress` | Resume from `current-step`. Do not restart. |
| `status: not-started` or `status: complete` | Initialize fresh. Write initial state. Proceed to Step 1. |
| `status: aborted` | Surface to controller: "Previous skill-optimize run was aborted. Resume or start fresh?" Wait for decision. |

---

## EXECUTION

**Dispatch model:** This workflow runs as a **Rigby** subagent spawned by the coordinator, never inline in the coordinator's session. Rigby executes the steps below in order.

Run steps in order. Read each step file fully before executing it.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `steps/step-01-setup.md` | spawned subagent (Rigby) |
| 2 | `steps/step-02-score-baseline.md` | spawned subagent (Rigby) |
| 3 | `steps/step-03-reflect.md` | spawned subagent (Rigby) |
| 4 | `steps/step-04-apply-candidate.md` | spawned subagent (Rigby) |
| 5 | `steps/step-05-score-candidate.md` | spawned subagent (Rigby) |
| 6 | `steps/step-06-gate.md` | spawned subagent (Rigby) |
| 7 | `steps/step-07-slow-update.md` | spawned subagent (Rigby) |
| 8 | `steps/step-08-report.md` | spawned subagent (Rigby) |

Begin: `steps/step-01-setup.md`

---

## TERMINATION CONDITIONS

The workflow terminates after Step 08 when any of the following are true:

- `rounds_completed` ≥ `total_rounds` configured in Step 01
- 3 consecutive rounds produced zero accepted edits (convergence)
- The skill has reached the `max_token_budget` (default: 2000 tokens)
- Controller explicitly requests termination

On termination, Step 08 marks `status: complete` in state.yaml and presents the final skill diff.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

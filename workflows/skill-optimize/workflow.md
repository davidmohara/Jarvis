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

Run steps in order. Read each step file fully before executing it.

1. [Step 01 — Setup](step-01-setup.md): Identify target skill, configure edit budget and epoch, gather eval record IDs
2. [Step 02 — Score Baseline](step-02-score-baseline.md): Score current skill across the eval batch; establish baseline
3. [Step 03 — Reflect](step-03-reflect.md): Invoke `rigby-skill-reflect` to produce bounded edit proposals
4. [Step 04 — Apply Candidate](step-04-apply-candidate.md): Write candidate skill version from accepted proposals
5. [Step 05 — Score Candidate](step-05-score-candidate.md): Score candidate skill across the held-out selection split
6. [Step 06 — Gate](step-06-gate.md): Accept or reject candidate; update rejected-edits buffer
7. [Step 07 — Slow Update](step-07-slow-update.md): Epoch-boundary consolidation (runs after epoch_size rounds)
8. [Step 08 — Report](step-08-report.md): Surface results, next actions, promote to pending-changes

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

---
status: not-started
started-at: ~
completed-at: ~
outputs:
  decision: null
  new_best_score: null
  new_best_skill_path: null
  accepted_edits_this_round: 0
  rejected_edits_logged: 0
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. The acceptance rule is strict: delta MUST be > 0 — ties are rejected
3. Never promote a candidate that ties or regresses the baseline
4. Always update the rejected-edits buffer, even on acceptance (rejected edits are any edits that were proposed but skipped during application)
5. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `delta`, `candidate_path`, `best_score`, `best_skill_path`, `rejected_edits_path` |
| Output | `decision` (accept/reject), updated `best_score`/`best_skill_path` if accepted, updated rejected-edits buffer |

## CONTEXT BOUNDARIES

This step makes the accept/reject decision and updates the rejected-edits buffer with negative feedback. It does NOT run new skills or propose new edits. It either promotes the candidate or discards it.

## YOUR TASK

### 1. Apply Gate Rule

```
if delta > 0:
  decision = "accept"
else:
  decision = "reject"
```

This is the only rule. No exceptions for "close enough" or "approximately the same." Ties (delta = 0) are rejected.

### 2a. If ACCEPT

**Promote candidate to best skill:**

Read the candidate from `candidate_path`.
Write it to `accumulated-context.best_skill_path` (which starts as the original SKILL.md for round 1; in later rounds, it may already be a promoted candidate).

Actually overwrite the live SKILL.md with the candidate content:

```
Copy: skills/{skill_id}/candidates/round-{N}-candidate.md
→ To: skills/{skill_id}/SKILL.md
```

Update state:
- `accumulated-context.best_score = candidate_score`
- `accumulated-context.best_skill_path = skills/{skill_id}/SKILL.md`
- `accumulated-context.accepted_edits_total += edits_applied_this_round`

Report:
> "[Rigby]: Round {N} accepted. Delta: +{delta:.3f}. {M} edits committed to {skill_id}/SKILL.md. Best score now {new_score:.2f}."

**Log to pending-changes:**

Append to `evolutions/.pending-changes.json`:
```json
{
  "work_item_id": "skill-optimize-{skill_id}",
  "file": "skills/{skill_id}/SKILL.md",
  "action": "merge",
  "description": "Optimization round {N} — {M} edits accepted (delta +{delta:.3f})",
  "timestamp": "<ISO-8601>"
}
```

### 2b. If REJECT

**Do not modify SKILL.md.**

`decision = "reject"`
`new_best_score = best_score` (unchanged)
`new_best_skill_path = best_skill_path` (unchanged)

Report:
> "[Rigby]: Round {N} rejected. Delta: {delta:.3f}. SKILL.md unchanged. Logging edits to rejected buffer."

### 3. Update Rejected-Edits Buffer

Read `rejected_edits_path`. This file accumulates all edits that were proposed but not committed, across all rounds.

**Always add to the buffer** — both from a rejected round AND from edits that were skipped during step-04 (edits proposed by reflect but whose targets weren't found):

For each proposed edit that was NOT committed (either round rejected, or edit skipped):
```json
{
  "round": <N>,
  "edit": { <the original edit object from the edits JSON> },
  "reason": "round_rejected | target_not_found | budget_clip",
  "delta_caused": <delta from this round — 0 if target_not_found or budget_clip>,
  "timestamp": "<ISO-8601>"
}
```

Append all such entries to `rejected_edits_path.entries[]` and write the file back.

`rejected_edits_logged = count of entries added`

### 4. Increment Round Counter

```
accumulated-context.rounds_completed += 1
```

If `delta = 0` or accepted edits = 0: `accumulated-context.consecutive_zero_edit_rounds += 1`
Else: `accumulated-context.consecutive_zero_edit_rounds = 0`

### 5. Determine Next Step

Check termination conditions:
- `rounds_completed >= total_rounds` → next step: `step-08-report`
- `consecutive_zero_edit_rounds >= 3` → next step: `step-08-report` (convergence)
- Best skill token count > `max_token_budget` → next step: `step-08-report` (size ceiling)
- Round number is a multiple of `epoch_size` → next step: `step-07-slow-update`
- Otherwise → next step: `step-03-reflect` (next round)

Update `state.yaml current-step` accordingly.

## SUCCESS METRICS

- Gate applied strictly (delta > 0 only)
- SKILL.md updated only on acceptance
- Rejected-edits buffer updated
- Round counter incremented
- Next step determined and written to state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Candidate file missing at promotion time | Halt. File disappeared between step-04 and now. |
| SKILL.md write fails on acceptance | Halt. Retry once. If still fails, surface to controller — candidate is ready but commit failed. |
| rejected-edits buffer write fails | Log error. Proceed — this is important but not blocking. |

## NEXT STEP

Determined dynamically — see step 5 above.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

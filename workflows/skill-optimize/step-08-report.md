---
status: not-started
started-at: ~
completed-at: ~
outputs:
  final_score: null
  total_accepted_edits: 0
  improvement_delta: null
  report_path: null
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. Always write the optimization report to disk — it is the audit trail
3. Confirm pending-changes is updated with all files modified during this workflow
4. Clean up candidate files older than the accepted versions (keep the winning candidate, purge the rest)
5. Set `state.yaml status: complete` as the final action

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | Full accumulated-context, all round outputs |
| Output | Optimization report at `skills/{skill_id}/optimization-report-{date}.md`; cleaned candidate dir; state marked complete |

## CONTEXT BOUNDARIES

This step summarizes, reports, and closes the optimization run. It does not propose or apply any more edits. If the controller wants another run, they start the workflow fresh.

## YOUR TASK

### 1. Compute Final Statistics

From accumulated-context and round history:

```
total_rounds_run = rounds_completed
accepted_rounds = count of rounds where delta > 0
rejected_rounds = total_rounds_run - accepted_rounds
total_accepted_edits = accumulated-context.accepted_edits_total
baseline_score = accumulated-context.baseline_score
final_score = accumulated-context.best_score
improvement_delta = final_score - baseline_score
convergence_reason = "rounds_exhausted | consecutive_zero_edits | size_ceiling | controller_terminated"
```

### 2. Compute Skill Diff

Read the original skill (from the first round's baseline) and the final best skill (from `best_skill_path`).

Show a clear diff of what changed — sections added, sections modified, sections deleted. This is the audit trail the controller uses to verify the optimization produced sensible output.

Format:

```
## Changes Made

### Added
- {section or rule added, with the text}

### Modified
- {what changed and why, per accepted edit}

### Deleted
- {what was removed}

### Slow-Update Region
- {content of the protected region, if any was written}
```

### 3. Generate Optimization Report

Write `skills/{skill_id}/optimization-report-{YYYY-MM-DD}.md`:

```markdown
# Skill Optimization Report: {skill_id}
**Date:** {YYYY-MM-DD}
**Rounds:** {total_rounds_run} ({accepted_rounds} accepted, {rejected_rounds} rejected)
**Edits committed:** {total_accepted_edits}
**Score:** {baseline_score:.2f} → {final_score:.2f} (+{improvement_delta:.2f})
**Convergence:** {convergence_reason}

## Changes Made
{diff from step 2}

## Failure Patterns Addressed
{list of recurring patterns from reflect outputs that were successfully addressed}

## Unresolved Patterns
{failure patterns that persisted across all rounds without a successful fix — these warrant controller attention}

## Rejected Edit Summary
{count and categories of rejected edits — helps identify where the loop struggled}

## Next Recommended Action
{one of:}
- "Run another optimization cycle with more eval records to address unresolved patterns."
- "Skill appears converged — run in production and collect more eval data before next cycle."
- "Author structural assertions for '{skill_id}' to strengthen the scoring signal before the next cycle."
- "Unresolved patterns require architectural changes beyond skill-level optimization — surface to Rigby for capability build."
```

### 4. Clean Candidate Directory

In `skills/{skill_id}/candidates/`:

- Keep: the winning candidate file (if any round was accepted)
- Keep: the latest round's edit proposal JSON (for audit)
- Delete: all other intermediate candidate files from this run

### 5. Confirm Pending-Changes Updated

Read `evolutions/.pending-changes.json`. Confirm entries exist for:
- `skills/{skill_id}/SKILL.md` (if any edits were accepted)
- `skills/{skill_id}/optimization-report-{date}.md`
- `skills/{skill_id}/rejected-edits.json`
- `skills/{skill_id}/slow-update-history.json` (if slow update ran)

If any are missing, add them now with action `"add"` or `"merge"` as appropriate.

### 6. Close State

Write `state.yaml`:
- `status: complete`
- `current-step: null`
- All final scores in accumulated-context

### 7. Present to Controller

Report concisely:

> "[Rigby]: Optimization complete for '{skill_id}'.
> {N} rounds, {M} edits accepted. Score: {baseline:.2f} → {final:.2f} (+{delta:.2f}).
> {convergence_reason_plain_english}.
> Report written to skills/{skill_id}/optimization-report-{date}.md.
> [Unresolved patterns if any: brief description]"

If `improvement_delta = 0`: add a note — "No improvement found in this cycle. Recommend authoring structural assertions and collecting more diverse eval records before retrying."

## SUCCESS METRICS

- Report written to disk
- Candidate directory cleaned
- Pending-changes current
- state.yaml marked complete
- Controller receives clear summary with next action

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Report write fails | Log error, still mark state complete. Present results to controller verbally. |
| Pending-changes write fails | Log error. Report to controller: "Pending-changes update failed — manually add skill/{skill_id}/SKILL.md to the pending log." |

## NEXT STEP

None — workflow complete. Return to Rigby for next instructions.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

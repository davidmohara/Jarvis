# Boot Workflow Guardrail Checkpoints

## Architecture

Each step in the boot workflow has an optional guardrail checkpoint that validates step outputs before proceeding.

**When:** After step completes (status: complete written to frontmatter)
**Who:** step-complete.py hook runs the checkpoint
**Result:** pass / flag / escalate
**Punch-out:** If escalate, workflow halts and awaits controller decision

## Step Boundaries

Guardrail checkpoints are positioned at **step group boundaries**, not inside steps:

```
Step-01 completes
  ↓
Guardrail checkpoint fires (step-01-checkpoint)
  ↓
  Result: pass → continue to step-01.5
  Result: flag → log warning, continue to step-01.5
  Result: escalate → PUNCH OUT — halt workflow, await controller
```

## Defining Guardrails

Each checkpoint is a JSON file named `{step-name}.json`:

```json
{
  "checkpoint_name": "unique-checkpoint-name",
  "description": "Human-readable description",
  "rules": [
    {
      "name": "rule-id",
      "type": "check_type",
      "field": "frontmatter_field_name",
      "critical": true,
      "reason": "Why this check matters"
    }
  ]
}
```

### Rule Types

**check_field_exists**
- Verifies field is present in step outputs
- critical: true → escalate if missing
- critical: false → flag if missing, continue

**check_field_not_empty**
- Verifies field exists and is not empty
- critical: true → escalate if empty
- critical: false → flag if empty, continue

**escalate_if** (future)
- Custom escalation condition
- critical: must be true to escalate

## Checkpoint Outcomes

Each checkpoint returns one of four results:

**pass** — Step succeeded, continue to next group
**flag** — Step has warnings but is usable, continue to next group
**retry** — Step is incomplete, send back to model to finish (don't involve operator)
**escalate** — Critical issue model can't fix, punch out to operator

### Retry Policy (Incomplete Steps)

If a step didn't finish, send it back to the model via **retry** signal:
- Missing required fields → retry (not escalate)
- Empty required fields → retry (not escalate)
- Step incomplete but fixable → retry

**retry_on_missing: true** — Field is missing or empty → retry the step
**retry_on_missing: false** — Field is missing or empty → flag (warn, don't retry)

Example:
```json
{
  "name": "briefing_generated",
  "type": "check_field_exists",
  "field": "briefing_file",
  "retry_on_missing": true,    // If briefing_file missing → retry step
  "reason": "Send step back to model if briefing wasn't generated"
}
```

### Escalation Policy (Critical Issues)

**Only escalate on CRITICAL issues the model can't fix:**
- Missing timestamps (can't extract tokens) → escalate
- Step status not 'complete' (didn't actually finish) → escalate
- API/Permission errors → escalate
- Data integrity failures → escalate

**Do NOT escalate on:**
- Missing optional fields → flag
- Incomplete step → retry (let model finish it)
- Warnings or non-blocking issues → flag

Use `critical: true` only for issues that need operator intervention. Everything else is either retry (incomplete) or flag (warnings).

## Audit Trail Recording

When step-complete.py runs, it records the checkpoint result in the eval record:

```json
{
  "guardrails": [
    {
      "name": "step-01-checkpoint",
      "after_step": "step-01-load-context",
      "result": "pass",
      "reason": "Step completed successfully",
      "escalated_to_human": false,
      "timestamp": "2026-08-22T12:22:55.593962+00:00",
      "validation_errors": []
    }
  ]
}
```

If escalate, eval record also gets:

```json
{
  "punch_out_signal": {
    "step": "step-01",
    "checkpoint": "step-01-checkpoint",
    "reason": "CRITICAL: [reason]",
    "awaiting_controller_decision": true,
    "timestamp": "2026-08-22T12:22:55.593962+00:00"
  }
}
```

## Controller Decision on Punch-Out

When workflow escalates, controller must manually update eval record:

```json
{
  "punch_out_signal": {
    "step": "step-01",
    "checkpoint": "step-01-checkpoint",
    "reason": "CRITICAL: [reason]",
    "awaiting_controller_decision": false,
    "controller_decision": "approve",
    "controller_notes": "Reason for approval/denial",
    "decided_at": "2026-08-22T12:30:00Z"
  }
}
```

If decision='approve', Master can continue from that step.
If decision='deny', workflow halts (not resumed until manual intervention).

## Existing Checkpoints

- **step-01-load-context.json** — Verify identity files loaded
- **step-02-gather-data.json** — Verify Phase 2 tasks completed  
- **step-06.5-guardrail-checkpoint.json** — Pre-completion review (data freshness, briefing integrity, no leakage)

## Adding New Checkpoints

1. Create `{step-name}.json` in this directory
2. Define rules with appropriate critical flags
3. step-complete.py will automatically load and run on that step
4. Audit trail will record results

## Future Enhancements

- Per-checkpoint audit logs (separate from eval record)
- Automated escalation notifications (email/Slack to controller)
- Bypass attempt tracking (detecting when controller overrides checkpoints)
- Multi-controller approval workflows (for critical steps)

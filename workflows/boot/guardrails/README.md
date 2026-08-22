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

## Escalation Policy

**Only escalate on CRITICAL issues:**
- Missing timestamps (can't extract tokens)
- Step status not 'complete' (didn't actually finish)
- Critical field failures (e.g. data freshness check)

**Do NOT escalate on:**
- Missing optional fields
- Warnings or non-blocking issues
- Empty optional outputs

Use `critical: false` for warnings. They get flagged in the audit trail but workflow continues.

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

---
stage: 4
workflow: boot
architecture: step-boundary-hooks
date: 2026-08-22
---

# Boot Workflow — Stage 4 Architecture

## Overview

Boot has been redesigned with:
- **Per-step token extraction** — Real tokens captured at each step boundary
- **Per-step guardrail validation** — Automated checks at each group boundary
- **Explicit punch-outs** — Escalation signals halt workflow for controller decisions
- **Granular audit trail** — Every step recorded with tokens, validation result, punch-out status

## Previous Architecture (Pre-Stage 4)

```
Master Agent runs all 7 steps sequentially (inline)
  ↓
  (no hooks between steps)
  ↓
SubagentStop fires once at end
  ↓
eval-agent-stop.py extracts TOTAL tokens only
  ↓
One guardrail checkpoint (step-06.5)
  ↓
Eval record has:
  - total_tokens_input/output (real, from transcript)
  - steps[].tokens_input/output = null (not extracted)
```

**Limitations:**
- Per-step tokens unavailable (couldn't trace token consumption to origin)
- Single guardrail checkpoint at end (couldn't validate intermediate steps)
- Punch-outs only at one boundary (couldn't escalate at logical decision points)
- Audit trail missing step-level detail

## New Architecture (Stage 4 Compliant)

```
Execution Groups (Sequential):
┌─ GROUP 1: step-01
│  └→ Agent completes, writes frontmatter
│     ↓
│     step-complete.py hook fires:
│       1. Extract step-01 tokens (from transcript time window)
│       2. Run guardrail checkpoint (step-01-checkpoint)
│       3. Record result in eval record
│       4. If escalate: punch out, await controller decision
│     ↓
│     Continue to GROUP 2
│
├─ GROUP 2: step-01.5
│  └→ (same pattern as above)
│
├─ GROUP 3: step-02
│  └→ (same pattern)
│
... (repeat for all 9 groups)
```

**Benefits:**
- ✓ Per-step tokens extracted at every boundary
- ✓ Guardrail checkpoints at natural decision points
- ✓ Explicit punch-outs with controller decisions
- ✓ Complete audit trail: each step has tokens + validation + punch-out status

## Key Components

### 1. Execution Groups (workflow.md)

Workflow declares 9 execution groups, each with a step and optional guardrail checkpoint:

```yaml
execution_groups:
  - group: 1
    step: step-01-load-context
    parallel: false
    guardrail: step-01-checkpoint
  - group: 2
    step: step-01.5-unified-calendar-pull
    parallel: false
    guardrail: step-01.5-checkpoint
  ... (etc)
```

**Sequential execution:** Master spawns step agents one at a time, waits for completion.
**Future:** Can mark groups as parallel (e.g., Phase 2 tasks could run in parallel).

### 2. Step-Complete Hook (.claude/hooks/step-complete.py)

Fires when a step writes its frontmatter with `status: complete`.

**Responsibilities:**
1. Extract step frontmatter (started-at, completed-at)
2. Call `usage_between(transcript_path, started-at, completed-at)` to get real tokens for that step
3. Load guardrail checkpoint definition (if exists)
4. Run validation rules
5. Decide: pass / flag / escalate
6. If escalate: write punch_out_signal to eval record (sets awaiting_controller_decision: true)
7. If pass/flag: update eval record and return success

**Escalation Logic:**
- ESCALATE on CRITICAL issues only: missing timestamps, failed assertions, data integrity
- FLAG on warnings: missing optional fields, suspicious but recoverable
- PASS by default

### 3. Guardrail Checkpoints (workflows/boot/guardrails/)

JSON files defining validation rules per step. Examples:

**step-01-checkpoint:**
```json
{
  "rules": [
    {
      "name": "identity_files_loaded",
      "type": "check_field_exists",
      "field": "files_loaded",
      "critical": true  // Escalate if missing
    }
  ]
}
```

**step-06.5-checkpoint:**
```json
{
  "rules": [
    {
      "name": "all_data_sources_live",
      "type": "check_field_exists",
      "field": "data_freshness_report",
      "critical": true  // Must verify live data before completion
    },
    {
      "name": "no_data_leakage",
      "type": "check_field_exists",
      "field": "leakage_check",
      "critical": true  // Must verify no confidential data leaked
    }
  ]
}
```

Rules can be:
- **check_field_exists** — Field must be present in step outputs
- **check_field_not_empty** — Field must have non-empty value
- **escalate_if** — Custom condition (future)

Each rule has `critical: true/false` to determine escalation behavior.

### 4. Eval Record Audit Trail

When step completes:

```json
{
  "steps": [
    {
      "name": "step-01-load-context.md",
      "started": "2026-08-22T12:21:00Z",
      "completed": "2026-08-22T12:22:00Z",
      "status": "complete",
      "tokens_input": 12345,        // Real tokens extracted by hook
      "tokens_output": 456,         // Real tokens extracted by hook
      "cost_usd": 0.0456,          // Calculated from real tokens
      "model": "sonnet",           // From transcript
      "duration_seconds": 60.0
    }
  ],
  "guardrails": [
    {
      "name": "step-01-checkpoint",
      "after_step": "step-01-load-context",
      "result": "pass",            // or flag or escalate
      "reason": "Step completed successfully",
      "escalated_to_human": false,
      "timestamp": "2026-08-22T12:22:55.593962Z",
      "validation_errors": []
    }
  ],
  "punch_out_signal": {           // Only if escalated
    "step": "step-01",
    "checkpoint": "step-01-checkpoint",
    "reason": "CRITICAL: [reason]",
    "awaiting_controller_decision": true,
    "timestamp": "2026-08-22T12:22:55Z"
  }
}
```

## Punch-Out Workflow

When guardrail escalates:

1. **Step-complete.py** writes punch_out_signal with awaiting_controller_decision: true
2. **Master** detects punch_out_signal, halts workflow, notifies controller
3. **Controller** reviews eval record, makes decision:
   ```json
   {
     "punch_out_signal": {
       "step": "step-01",
       "awaiting_controller_decision": false,  // Decision made
       "controller_decision": "approve",        // or "deny"
       "controller_notes": "Reason",
       "decided_at": "2026-08-22T12:30:00Z"
     }
   }
   ```
4. **Master** resumes from that step if approve, or halts if deny

## Stage 4 Compliance

| Requirement | How Met |
|-------------|---------|
| Per-step tokens | step-complete.py extracts via usage_between() at each boundary |
| Per-step validation | Guardrail checkpoint runs after each step |
| Punch-out evidence | punch_out_signal recorded in eval record with reason |
| Bypass testing | Can test escalation at any step boundary |
| End-to-end success rate | Computed from eval record (pass = all assertions passed AND no critical escalations) |
| Audit trail | Each step has tokens, model, cost, duration, validation result |

## Future Enhancements

1. **Parallel execution groups** — Mark step groups as parallel for Phase 2 tasks
2. **Per-checkpoint audit logs** — Separate audit log for all escalations across sessions
3. **Automated notifications** — Email/Slack controller when punch-out occurs
4. **Multi-level escalation** — Different rules for different severity levels
5. **Bypass attempt tracking** — Track when controller overrides checkpoints

## Running Boot with New Architecture

Boot runs the same way, but with new capabilities:

```bash
# Start fresh boot
python3 workflows/boot/workflow.md

# If punch-out occurs at step-05:
# 1. Workflow halts
# 2. Controller reviews eval record
# 3. Controller updates punch_out_signal.controller_decision
# 4. Master resumes (or halts if deny)

# After all steps complete:
# - eval record has per-step tokens
# - All guardrail results recorded
# - Success rate computed from assertions
```

No code changes needed to run boot — just the new hook and guardrail definitions.

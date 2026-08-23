---
workflow: boot
stage: 4
title: Boot Workflow — Complete Stage 4 System
---

# Boot Workflow — Complete Stage 4 System

## System Overview

Boot has been redesigned with:
- ✅ Per-step token extraction (real tokens captured at each boundary)
- ✅ Per-step guardrail validation (automated checks after each step)
- ✅ Explicit punch-out mechanism (escalations halt workflow for controller decisions)
- ✅ Complete audit trail (every step recorded with tokens, validation, punch-out status)
- ✅ Master orchestration (coordinates all steps, handles escalations, manages state)

## System Components

### 1. Step Execution (Master Agent)

**File:** `workflow.md` (modified) + `MASTER-ORCHESTRATION.md` (new)

Master is the orchestrator that:
- Reads `state.yaml` (recover from interruption or start fresh)
- Spawns 9 execution groups (steps) sequentially
- Waits for each step to complete
- Polls eval record for punch-out signals
- Halts on escalation, notifies controller
- Resumes or aborts based on controller decision
- Continues to next group on pass/flag

**State Machine:** See MASTER-ORCHESTRATION.md for complete state machine.

### 2. Per-Step Token Extraction

**File:** `.claude/hooks/step-complete.py` (new)

When each step completes:
1. Reads step frontmatter (started-at, completed-at timestamps)
2. Calls `usage_between(transcript_path, started_at, completed_at)` to extract tokens for that time window
3. Records: tokens_input, tokens_output, cost_usd, model
4. Updates eval record `steps[].tokens_*` fields

**Result:** Every step has real token data in eval record.

### 3. Per-Step Guardrail Checkpoints

**Files:**
- `guardrails/step-01-load-context.json` — Verify identity files loaded
- `guardrails/step-01.5-unified-calendar-pull.json` — Verify calendar data
- `guardrails/step-02-gather-data.json` — Verify Phase 2 completion
- `guardrails/step-03-verify-phase2.json` — Verify Phase 2 integrity
- `guardrails/step-04-gather-meeting-context.json` — Verify meeting context
- `guardrails/step-05-synthesize-briefing.json` — Verify briefing complete
- `guardrails/step-06-scan-workflows.json` — Verify workflow scan
- `guardrails/step-06.5-guardrail-checkpoint.json` — Pre-completion review (data freshness, integrity, no leakage)
- `guardrails/step-07-verify-completion.json` — Hard gate (all steps complete, no escalations)

**Logic:**
- Each checkpoint has rules: check_field_exists, check_field_not_empty
- Rules marked as critical or non-critical
- ESCALATE only on critical failures (missing timestamps, failed assertions)
- FLAG on warnings (missing optional fields)
- PASS by default

**Result:** Validation happens at each boundary, escalations are deliberate and documented.

### 4. Retry Mechanism (Self-Healing)

**Incomplete steps retry automatically (don't involve operator):**

```
Step completes
  ↓
Guardrail checkpoint finds step incomplete (missing output)
  ↓
step-complete.py writes retry_signal:
  {
    "step": "step-05-synthesize-briefing",
    "reason": "Step incomplete: briefing_file missing",
    "feedback": "Re-execute step to completion. Output: briefing_file",
    "attempt_number": 1
  }
  ↓
Master detects retry_signal (not punch_out), re-executes step
  ↓
Step runs again with model aware it failed before
  ↓
If still incomplete after 3 retries: escalate to operator
  ↓
If completes: continue to next step
```

**Result:** Steps self-heal up to 3 times; operator only involved for critical issues.

### 5. Escalation Mechanism (Operator Decision)

**Only CRITICAL issues escalate (that model can't fix):**

```
Step completes
  ↓
Guardrail checkpoint finds CRITICAL issue (e.g., permission denied)
  ↓
step-complete.py writes punch_out_signal:
  {
    "step": "step-04-gather-meeting-context",
    "reason": "CRITICAL: Calendar API access denied",
    "awaiting_controller_decision": true
  }
  ↓
Master detects punch_out_signal, halts workflow
  ↓
Master notifies operator: "Escalation at step-04: Calendar API access denied"
  ↓
Operator reviews eval record, updates punch_out_signal:
  {
    "controller_decision": "approve",  // or "deny"
    "controller_notes": "Using fallback data"
  }
  ↓
Master resumes (if approve) or aborts (if deny)
```

**Result:** Clear escalation points; operator only decides critical issues.

### 5. Audit Trail Recording

**Eval Record Structure:**
```json
{
  "id": "eval-20260822T122903-MZNKZ8",
  "status": "success",
  "steps": [
    {
      "name": "step-01-load-context.md",
      "started": "2026-08-22T12:21:00Z",
      "completed": "2026-08-22T12:22:00Z",
      "tokens_input": 12345,    // Real from transcript
      "tokens_output": 456,     // Real from transcript
      "cost_usd": 0.0456,      // Calculated from real tokens
      "model": "sonnet",        // From transcript
      "duration_seconds": 60
    },
    // ... (all 9 steps with real per-step tokens)
  ],
  "guardrails": [
    {
      "name": "step-01-checkpoint",
      "after_step": "step-01-load-context",
      "result": "pass",
      "reason": "Step completed successfully",
      "timestamp": "2026-08-22T12:22:55Z"
    },
    // ... (all guardrail checkpoints)
  ],
  "punch_out_signal": {
    "step": "step-04-gather-meeting-context",
    "reason": "CRITICAL: Attendee enrichment failed",
    "controller_decision": "approve",
    "decided_at": "2026-08-22T12:30:00Z"
  }
}
```

**Coverage:**
- ✓ Per-step model, tokens_input, tokens_output, cost (REAL from transcript)
- ✓ Per-step validation result (pass/flag/escalate)
- ✓ Per-step punch-out status (if escalated)
- ✓ Controller decisions (approve/deny)
- ✓ Failure tracing (each step isolated with tokens)
- ✓ End-to-end success rate (computed from assertions + escalations)

## Stage 4 Compliance Mapping

| Requirement | How Met | Evidence |
|-------------|---------|----------|
| **Multi-agent pipeline** | Master orchestrates 9 step agents | workflow.md + MASTER-ORCHESTRATION.md |
| **Real audit trail** | Per-step tokens from transcript | step-complete.py hook + eval record |
| **Per-step model/tokens** | usage_between() extracts per-step | All steps[] entries have tokens_input/output |
| **Guardrails** | 9 checkpoints at step boundaries | guardrails/*.json definitions |
| **Punch-outs tested** | Escalation scenarios documented | MASTER-ORCHESTRATION.md punch-out flow |
| **Success rate** | End-to-end: all assertions pass + no critical escalations | Computed from eval record |
| **Failure tracing** | Each step isolated with tokens + checkpoint result | Audit trail per-step detail |

## Running Boot with This System

### Fresh Boot
```bash
# Master reads state.yaml, finds status: complete
# Initializes fresh boot
# Spawns step-01, waits for completion
# Checks for punch-out signal (none expected on success)
# Continues to step-01.5, etc.
# If all steps complete without escalation: status: success
```

### Resuming After Escalation
```bash
# After punch-out at step-05:
# 1. Master halts, notifies controller
# 2. Controller updates punch_out_signal.controller_decision: approve
# 3. Master detects decision, resumes from step-05
# 4. Continues to step-06
# If no more escalations: boot completes
```

### Aborting
```bash
# If controller sets controller_decision: deny
# 1. Master updates eval record status: aborted
# 2. Workflow halts, eval record not counted as success/failure
# 3. Next boot starts fresh
```

## Documentation Files

**User-facing:**
- `workflow.md` — Workflow definition (execution groups, state check, data sources)
- `ARCHITECTURE.md` — Architecture design (before/after, components, compliance)
- `MASTER-ORCHESTRATION.md` — Master controller logic (state machine, pseudocode, error handling)
- `guardrails/README.md` — How to define guardrails, rule types, audit trail

**Developer-facing:**
- `.claude/hooks/step-complete.py` — Hook implementation (token extraction, guardrails, punch-out)
- `guardrails/*.json` — 9 guardrail checkpoint definitions

## Key Design Decisions

1. **Only escalate on CRITICAL issues** — Warnings flag but don't halt
2. **Sequential execution** — Steps run one at a time (future: parallel groups)
3. **Controller decides on escalation** — No automatic bypass, explicit human decision
4. **Per-step isolation** — Each step has its own tokens, timestamp window, validation
5. **Full audit trail** — All decisions, escalations, tokens recorded in eval record

## Future Enhancements

1. **Parallel execution groups** — Phase 2 tasks (G, H, I, J) spawn in parallel
2. **Automatic retries** — Retry failed steps up to 2x before escalating
3. **Conditional branches** — Route to different steps based on prior results
4. **Timeout handling** — Per-step timeouts, auto-escalate on timeout
5. **Escalation aggregation** — Centralized log of all escalations across boot runs
6. **Automated notifications** — Email/Slack controller when punch-out occurs
7. **Multi-controller approval** — Require approval from multiple controllers for critical steps

## Success Metrics (For Stage 4)

Run boot 5+ times and measure:

| Metric | Target | Definition |
|--------|--------|-----------|
| **Success Rate** | ≥70% | % of runs where all assertions pass AND no critical escalations |
| **Per-Step Tokens** | 100% | % of steps with real token data (not estimated) |
| **Audit Trail** | 100% | % of steps with model/tokens/cost recorded |
| **Guardrail Coverage** | 100% | % of steps with checkpoint definitions |
| **Trend** | Stable/improving | Success rate doesn't decrease over 5+ runs |

## System Ready for Testing

All components are in place. Boot is ready to run with the architecture. When launched, the system will automatically:
- Extract per-step tokens from transcripts
- Run guardrail validations at step boundaries
- Record punch-outs with controller decisions
- Maintain complete audit trail

**Next step:** Run boot 5+ times to build trend data and finalize Stage 4 submission.

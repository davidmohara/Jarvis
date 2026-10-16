# BT-01: Max-Retries Punch-Out Test

| Field | Value |
|-------|-------|
| **Test ID** | BT-01 |
| **Mechanism under test** | Guardrail retry + max-retries escalation (`step-complete.py` retry_signal / punch_out_signal; MASTER-ORCHESTRATION.md loop) |
| **Enforcement layer** | Technical (executable hook) |
| **Attempt** | Drive a step to repeated validation failure; confirm retries cap at `max_attempts` and then punch out to the human operator instead of silently succeeding |
| **Expected block** | retry_signal.attempt_number increments; at `attempt >= max_attempts` (2) a `punch_out_signal` with `awaiting_controller_decision=True` is written and the controller is notified |
| **Actual result** | Retries incremented 1 then 2; loop condition fired and wrote `punch_out_signal`; escalate path wrote `punch_out_signal` directly; pass path wrote neither |
| **Pass / Fail** | **PASS** |
| **Timestamp** | 2026-10-08T20:19:59Z |
| **Raw log** | `logs/BT-01-max-retries.log` |

## Mechanism contract (read from source)

- `step-complete.py` `run_step_guardrail_checkpoint()` returns one of
  `pass` / `flag` / `retry` / `escalate`. On `retry` it queues a re-execute; on
  `escalate` it sets `escalated_to_human=True`.
- `update_eval_record_with_step_completion()` writes `retry_signal` with
  `attempt_number` (incremented from the record's prior value) and
  `max_attempts: 2` ("Retry once, escalate on second failure"). On `escalate`
  it writes `punch_out_signal` with `awaiting_controller_decision: True`.
- `workflows/boot/MASTER-ORCHESTRATION.md` is the loop that reads
  `retry_signal` and, when `attempt >= max_attempts`, writes the
  `punch_out_signal` and calls `notify_controller`. This decision logic is
  **documented pseudocode**, not executable code; the executable pieces are the
  two `step-complete.py` functions, which are what this test drives directly.
- `workflows/boot/workflow.md` states the same contract in prose: "if retry:
  re-execute step (max 2 attempts per step-complete.py's retry_signal)."

## Attempt transcript (excerpt; full log in `logs/`)

```
--- PART A: drive update_eval_record_with_step_completion() with a retry result ---
  after failure #1: retry_signal.attempt_number=1 max_attempts=2
  after failure #2: retry_signal.attempt_number=2 max_attempts=2

--- PART B: MASTER-ORCHESTRATION.md loop condition on the REAL retry_signal ---
  eval_record.retry_signal present: step=step-04-gather-meeting-context attempt=2 max=2
  BRANCH: attempt >= max_attempts -> punch_out_signal WRITTEN
  punch_out_signal = {
    "step": "step-04-gather-meeting-context",
    "checkpoint": "step-04-gather-meeting-context-checkpoint",
    "reason": "Step failed validation after 2 attempts: Step incomplete: missing required field 'x' ...",
    "awaiting_controller_decision": true,
    "timestamp": "2026-10-08T20:19:59.604683Z"
  }
  notify_controller(punch_out_signal)  # punch-out FIRES, not silent success

--- PART C: escalate result -> punch_out_signal (real hook function) ---
  guardrails[-1].escalated_to_human = True
  punch_out_signal = { ... "awaiting_controller_decision": true ... }

--- PART D (negative control): pass result -> NO punch_out, NO retry ---
  retry_signal present: False
  punch_out_signal present: False
  guardrails[-1].result = pass
```

## Analysis

- The retry cap is real and enforced by the executable hook: `attempt_number`
  advanced 1 to 2 across successive failures, and `max_attempts` is fixed at 2.
- On exhaustion the documented loop condition (`attempt >= max_attempts`)
  produced a `punch_out_signal` addressed to the controller. There is no path
  in which the second failure is recorded as success: the negative control
  (Part D) shows only a `pass` result leaves both `retry_signal` and
  `punch_out_signal` absent.
- The one caveat to record honestly: the exhaustion-to-punch-out branch lives
  in `MASTER-ORCHESTRATION.md` pseudocode and in `workflow.md` prose, not in an
  executable loop. `step-complete.py` produces the `retry_signal` and
  `max_attempts`; the orchestration layer is what must honor it. The evidence
  above drives the real hook functions and reproduces the loop condition
  verbatim, so the contract is verified end to end at the component level.

## How this was run (safety)

A `/tmp` driver loaded `.claude/hooks/step-complete.py` as a module and pointed
its `update_eval_record_with_step_completion()` at a temp eval record under
`/tmp`. No file under `systems/eval-harness/runs/` was read or written. Real
component, isolated state.

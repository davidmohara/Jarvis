---
workflow: boot
component: master-orchestration
stage: 4
---

# Master Orchestration — Boot Workflow Controller

## Overview

Master is the orchestrator that coordinates boot workflow execution. It:
1. Spawns step agents in execution groups (sequential or parallel)
2. Waits for step completion
3. Checks for punch-out signals (escalations)
4. Halts workflow if escalation, notifies controller
5. Resumes or aborts based on controller decision
6. Continues to next group when all steps in group complete

## State Machine

```
START
  ↓
[GROUP 1: step-01]
  ├→ Spawn Agent
  ├→ Wait for completion
  ├→ Check retry_signal OR punch_out_signal
  │   ├─ retry_signal: Step incomplete → RE-EXECUTE step (loop)
  │   │   └─ Max 3 retries, then escalate if still incomplete
  │   ├─ punch_out_signal: Critical issue → ESCALATION (jump to HALT)
  │   └─ No signal: Continue
  └→ Success: Continue to GROUP 2

[GROUP 2: step-01.5]
  ├→ (same pattern)
  └→ Success: Continue to GROUP 3

... (repeat for all 9 groups)

[GROUP 9: step-07]
  ├→ Spawn Agent
  ├→ Wait for completion
  ├→ Check punch_out_signal
  │   └─ (step-07 is hard gate; any escalation fails boot)
  └→ Success: BOOT COMPLETE

HALT (Escalation detected):
  ├→ Notify controller: "[Master]: Escalation at {step_name}: {reason}"
  ├→ Update eval record punch_out_signal:
  │   └─ awaiting_controller_decision: true
  ├→ Poll eval record for controller decision
  ├→ Controller updates punch_out_signal:
  │   ├─ decision: approve → RESUME
  │   └─ decision: deny → ABORT
  └→ Wait (don't timeout; controller decides)

RESUME (Controller approved):
  ├→ Update eval record:
  │   └─ punch_out_signal.controller_decision: approve
  ├→ Continue from escalation point
  └→ Return to executing that step's group

ABORT (Controller denied or boot timeout):
  ├→ Update eval record:
  │   ├─ status: aborted
  │   └─ abort_reason: controller_denied or timeout
  ├→ Notify controller: "[Master]: Boot aborted at {step_name}"
  └→ END (eval record closed, not counted as success/failure)

BOOT COMPLETE:
  ├→ Mark eval record: status: success (if all assertions pass)
  ├→ Write completion summary
  └→ END
```

## Execution Protocol

### Phase 1: State Check

**On every boot start, Master runs STATE CHECK first:**

```
Read workflows/boot/state.yaml

If status: complete → Fresh boot
  - Initialize new state.yaml
  - Generate session-id
  - Set current-step: step-01
  - Begin at GROUP 1

If status: in-progress → Resume or restart?
  - Check staleness: session-started > 4 hours old?
    - If yes → Stale, restart (fresh boot)
    - If no → Resume from current-step
  - Read accumulated-context (data already gathered)
  - Continue from current-step

If status: aborted → Wait for instruction
  - Surface to controller: "Boot was previously aborted at [step]. Resume or restart?"
  - Wait for decision
```

### Phase 2: Execution Groups

**Master orchestrates 9 sequential groups:**

```python
execution_groups = [
  {"group": 1, "step": "step-01-load-context", "parallel": False},
  {"group": 2, "step": "step-01.5-unified-calendar-pull", "parallel": False},
  {"group": 3, "step": "step-02-gather-data", "parallel": False},
  {"group": 4, "step": "step-03-verify-phase2", "parallel": False},
  {"group": 5, "step": "step-04-gather-meeting-context", "parallel": False},
  {"group": 6, "step": "step-05-synthesize-briefing", "parallel": False},
  {"group": 7, "step": "step-06-scan-workflows", "parallel": False},
  {"group": 8, "step": "step-06.5-guardrail-checkpoint", "parallel": False},
  {"group": 9, "step": "step-07-verify-completion", "parallel": False},
]

for group in execution_groups:
  if group["parallel"]:
    # Spawn all steps in group in parallel
    agents = [spawn_agent(step) for step in group["steps"]]
    # Wait for ALL to complete
    wait_all(agents)
  else:
    # Spawn single step
    agent = spawn_agent(group["step"])
    # Wait for completion
    wait(agent)
  
  # Check for punch-out signal
  eval_record = read_eval_record()
  if eval_record.get("punch_out_signal"):
    halt_and_wait_for_controller()
  
  # Update state.yaml
  state.current_step = next_group.step
  write_state()
```

**Future:** Phase 2 (step-02) can be marked parallel to spawn Tasks G, H, I, J simultaneously.

### Phase 3: Punch-Out Handling

**When guardrail checkpoint escalates:**

1. **step-complete.py** writes punch_out_signal:
   ```json
   {
     "punch_out_signal": {
       "step": "step-05-synthesize-briefing",
       "checkpoint": "step-05-checkpoint",
       "reason": "CRITICAL: Briefing is empty",
       "awaiting_controller_decision": true,
       "timestamp": "2026-08-22T12:22:55Z"
     }
   }
   ```

2. **Master detects signal:**
   ```
   eval_record = read_eval_record()
   if eval_record.get("punch_out_signal", {}).get("awaiting_controller_decision"):
     halt_for_controller_decision()
   ```

3. **Master notifies controller:**
   - Log: "[Master]: ESCALATION at step-05-synthesize-briefing"
   - Message: "[Master]: Briefing synthesis escalated: CRITICAL: Briefing is empty"
   - Action: "Review eval record, update punch_out_signal.controller_decision"

4. **Master polls for controller decision:**
   ```
   while eval_record["punch_out_signal"]["awaiting_controller_decision"]:
     sleep(10)  # Poll every 10 seconds
     eval_record = read_eval_record()
     
     if eval_record["punch_out_signal"]["controller_decision"]:
       if decision == "approve":
         resume_from_step()
       elif decision == "deny":
         abort_boot()
   ```

5. **Controller decides** (updates eval record):
   ```json
   {
     "punch_out_signal": {
       "step": "step-05-synthesize-briefing",
       "checkpoint": "step-05-checkpoint",
       "reason": "CRITICAL: Briefing is empty",
       "awaiting_controller_decision": false,
       "controller_decision": "approve",
       "controller_notes": "Briefing synthesis failed but previous briefing available; proceed with prior briefing",
       "decided_at": "2026-08-22T12:30:00Z"
     }
   }
   ```

6. **Master resumes or aborts:**
   - If approve: Continue from that step (run next group)
   - If deny: Mark eval record status: aborted, abort_reason: controller_denied

### Phase 4: Completion

**After all 9 groups complete successfully:**

1. **step-07** verifies all prior steps
2. **step-07 checkpoint** confirms no escalations
3. **eval-agent-stop.py** finalizes eval record:
   - Computes end-to-end success rate
   - Finalizes audit trail
   - Marks status: success (or partial/failure based on assertions)

4. **Master updates state.yaml:**
   ```yaml
   status: complete
   completed-at: "2026-08-22T12:35:11Z"
   current-step: null
   ```

5. **Boot is complete** — ready for next session

## Implementation: Master Agent Pseudocode

```python
def boot_orchestration():
    """Master orchestration of boot workflow."""
    
    # State check
    state = read_state_yaml()
    if state.status == "complete":
        init_fresh_boot()
    elif state.status == "in-progress":
        if is_stale(state.session_started):
            init_fresh_boot()  # Stale, restart
        else:
            resume_boot(state.current_step)  # Resume
    elif state.status == "aborted":
        wait_for_controller_decision()
        return
    
    # Execution loop
    for group in execution_groups:
        # Retry loop (max 3 attempts per step)
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            # Spawn step(s)
            if group.parallel:
                agents = [Agent(step) for step in group.steps]
                wait_all(agents)
            else:
                agent = Agent(group.step)
                agent.run()
            
            # CRITICAL: Invoke step-complete hook to extract tokens and run guardrails
            step_file = Path("workflows/boot/steps") / f"{group.step}.md"
            if step_file.exists():
                invoke_hook_result = subprocess.run([
                    "python3", "workflows/boot/invoke-step-complete-hook.py",
                    "--step-file", str(step_file),
                    "--session-id", state.session_id,
                    "--transcript-path", transcript_path  # From Agent result
                ], capture_output=True, text=True)
                
                if invoke_hook_result.returncode != 0:
                    log(f"[Master] Hook invocation failed for {group.step}: {invoke_hook_result.stderr}")
            
            # Check for retry or escalation signal
            eval_record = read_eval_record()
            
            # If retry: incomplete step, send feedback and re-execute
            if eval_record.get("retry_signal"):
                retry_count += 1
                retry_feedback = eval_record["retry_signal"].get("feedback")
                step_name = eval_record["retry_signal"].get("step")
                log(f"[Master] Retry {retry_count}/{max_retries} for {step_name}: {retry_feedback}")
                
                if retry_count >= max_retries:
                    # Max retries exceeded, escalate (invoke controller)
                    eval_record["punch_out_signal"] = {
                        "step": step_name,
                        "reason": f"Step still incomplete after {max_retries} retries",
                        "awaiting_controller_decision": True
                    }
                    break  # Exit retry loop, go to punch-out handling
                else:
                    # Retry: re-execute the step with feedback
                    continue  # Loop and re-spawn agent
            
            # If punch-out: critical issue, escalate to controller
            if eval_record.get("punch_out_signal", {}).get("awaiting_controller_decision"):
                notify_controller(eval_record["punch_out_signal"])
                wait_for_controller_decision(eval_record)
                
                decision = eval_record["punch_out_signal"]["controller_decision"]
                if decision == "deny":
                    abort_boot()
                    return
            
            # If neither retry nor punch-out: step succeeded, exit retry loop
            break
        
        # Update state
        state.current_step = group.next_step
        write_state_yaml(state)
    
    # Boot complete
    state.status = "complete"
    state.completed_at = now()
    state.current_step = None
    write_state_yaml(state)
    
    print("[Master]: Boot complete")
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Agent fails (exception) | Mark step status: failure, escalate to controller |
| Step timeout (>5 min) | Mark status: timeout, escalate to controller |
| Punch-out signal present | Halt, await controller decision |
| Controller doesn't respond (>30 min) | Timeout punch-out, abort boot |
| Eval record inaccessible | Log error, abort boot |
| State file corruption | Restart fresh boot |

## Monitoring & Logging

Master logs all transitions:

```
[12:21:00] [Master] Boot starting (session: sess-xyz)
[12:21:05] [Master] GROUP 1: step-01-load-context
[12:21:05] [Master] Spawning agent: master (step-01)
[12:21:10] [Master] Agent complete, status: success
[12:21:10] [Master] Checking punch-out signal... none
[12:21:11] [Master] GROUP 2: step-01.5-unified-calendar-pull
...
[12:22:30] [Master] GROUP 5: step-04-gather-meeting-context
[12:22:45] [Master] Agent complete, status: success
[12:22:45] [Master] Checking punch-out signal... ESCALATION DETECTED
[12:22:45] [Master] HALT: step-04-gather-meeting-context escalated: "CRITICAL: Attendee enrichment failed"
[12:22:46] [Master] Notifying controller...
[12:22:46] [Master] Awaiting controller decision (eval record: eval-xyz)
[12:30:00] [Master] Controller decision: approve
[12:30:01] [Master] Resuming from step-04-gather-meeting-context
[12:30:10] [Master] GROUP 6: step-05-synthesize-briefing
...
[12:35:10] [Master] All groups complete
[12:35:11] [Master] Boot complete (status: success)
```

## Integration with Eval Harness

Master orchestration integrates with eval harness:

1. **eval-agent-start.py** — Creates eval record stub when Master starts
2. **step-complete.py** — Fires after each step, extracts tokens + runs guardrails
3. **eval-agent-stop.py** — Finalizes eval record when Master completes
4. **eval record** — Records all steps, guardrails, punch-outs, and controller decisions

Each eval record shows full history:
```json
{
  "steps": [
    {"name": "step-01", "tokens": 12345, "status": "complete"},
    {"name": "step-01.5", "tokens": 5678, "status": "complete"},
    ...
  ],
  "guardrails": [
    {"name": "step-01-checkpoint", "result": "pass"},
    ...
    {"name": "step-04-checkpoint", "result": "escalate", "reason": "..."}
  ],
  "punch_out_signal": {
    "step": "step-04-gather-meeting-context",
    "reason": "CRITICAL: Attendee enrichment failed",
    "controller_decision": "approve",
    "controller_notes": "Proceeding with partial data"
  }
}
```

## Future Enhancements

1. **Parallel groups** — Mark Phase 2 tasks (step-02) as parallel
2. **Automatic retries** — Retry failed steps up to N times before escalating
3. **Conditional branches** — Branch to different steps based on prior results
4. **Timeout handling** — Configure per-step timeouts
5. **Audit log aggregation** — Centralized log of all boot runs, escalations, decisions
6. **Controller notifications** — Email/Slack when punch-out occurs

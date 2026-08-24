---
workflow: boot
component: master-orchestration
---

# Master Orchestration

State machine for boot workflow execution.

## State Check

```
Read state.yaml
if status == complete: fresh run → init state → step-01
if status == in-progress:
  if session-started > 4h old: fresh run (stale)
  else: resume from current-step
if status == aborted: ask controller
```

## Execution Loop

```python
for group in execution_groups:
  while True:
    agent = spawn_step(group.step)
    agent.run()
    
    eval_record = read_eval_record()
    
    if eval_record.get("retry_signal"):
      retry_signal = eval_record["retry_signal"]
      attempt = retry_signal.get("attempt_number", 1)
      max_attempts = retry_signal.get("max_attempts", 2)
      
      if attempt >= max_attempts:
        # Max retries exceeded, escalate to controller
        eval_record["punch_out_signal"] = {
          "step": retry_signal["step"],
          "checkpoint": retry_signal["checkpoint"],
          "reason": f"Step failed validation after {attempt} attempts: {retry_signal['reason']}",
          "awaiting_controller_decision": True,
          "timestamp": current_timestamp()
        }
        write_eval_record(eval_record)
        notify_controller(eval_record["punch_out_signal"])
        wait_for_controller_decision(eval_record)
        
        if eval_record["punch_out_signal"]["controller_decision"] == "deny":
          abort_boot()
          return
      else:
        # Retry: Pass instruction back to model and re-execute step
        inject_retry_instruction(eval_record, group.step)
        continue
    
    if eval_record.get("punch_out_signal", {}).get("awaiting_controller_decision"):
      notify_controller(eval_record["punch_out_signal"])
      wait_for_controller_decision(eval_record)
      
      if eval_record["punch_out_signal"]["controller_decision"] == "deny":
        abort_boot()
        return
    
    break

state.current_step = next_step
write_state()

mark_boot_complete()
```

## Punch-Out Flow

```
Step completes → eval-agent-stop.py fires
→ invoke_step_complete_hooks() for all completed steps
→ step-complete.py runs guardrail checkpoint
→ If escalate: punch_out_signal written to eval record
→ Master polls for controller_decision
→ Controller approves/denies
→ Master resumes or aborts
```

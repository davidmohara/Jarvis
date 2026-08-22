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
  retry_count = 0
  while retry_count < 3:
    agent = spawn_step(group.step)
    agent.run()
    
    eval_record = read_eval_record()
    
    if eval_record.get("retry_signal"):
      retry_count += 1
      if retry_count >= 3:
        escalate_to_controller()
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

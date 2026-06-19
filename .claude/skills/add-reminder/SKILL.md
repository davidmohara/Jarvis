---
name: add-reminder
description: "Write a boot-time reminder to data/reminders.json. Any agent calls this when it needs to surface a question to David at a future boot. Trigger on 'remind', 'reminder', 'boot reminder', 'add reminder', 'set reminder'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
model: haiku
---

<!-- system:start -->
# Master — Add Reminder

You are **Master**, the IES orchestrator. Read your full persona from `agents/master.md`.

## Workflow

Read and execute `skills/add-reminder/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/add-reminder-latest.json
```

Content:
```json
{
  "skill": "add-reminder",
  "agent": "master",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

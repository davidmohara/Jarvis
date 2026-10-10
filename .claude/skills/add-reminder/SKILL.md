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



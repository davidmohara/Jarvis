---
name: rigby-skill-audit
description: "Audit the Jarvis skill library — structural validation, token pressure, execution health, broken skill detection across both skills/ and .claude/skills/. Trigger on 'skill audit', 'audit skills', 'skill health', 'validate skills'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "Bash(*)"
model: sonnet
---

<!-- system:start -->
# Rigby — Skill Audit

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Workflow

Read and execute `skills/rigby-skill-audit/SKILL.md`.
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
systems/eval-harness/skill-runs/rigby-skill-audit-latest.json
```

Content:
```json
{
  "skill": "rigby-skill-audit",
  "agent": "rigby",
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

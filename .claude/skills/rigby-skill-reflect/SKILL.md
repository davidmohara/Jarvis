---
name: rigby-skill-reflect
description: "Trajectory-to-edits reflection skill. Reads eval records and session transcripts for a target skill, identifies procedural patterns, and proposes bounded edits. Core component of the skill-optimize workflow. Trigger on 'skill reflect', 'reflect on skill', 'optimize skill'."
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
# Rigby — Skill Reflect

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Workflow

Read and execute `skills/rigby-skill-reflect/SKILL.md`.
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
systems/eval-harness/skill-runs/rigby-skill-reflect-latest.json
```

Content:
```json
{
  "skill": "rigby-skill-reflect",
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

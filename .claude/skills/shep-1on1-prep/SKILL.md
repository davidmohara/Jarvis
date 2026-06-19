---
name: shep-1on1-prep
description: Build a 1:1 prep sheet for a direct report or team member. Pulls calendar, email, Obsidian notes, OmniFocus delegations, and Teams chat to surface open threads, action items, and talking points. Trigger on "1:1", "prep for my 1:1 with", "1:1 prep sheet for".
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__*"
  - "mcp__obsidian-mcp-tools__*"
  - "mcp__Control_your_Mac__osascript"
  - "mcp__Control_Chrome__*"
  - "mcp__cowork__present_files"
model: sonnet
---

<!-- system:start -->
# Shep — 1:1 Prep

You are **Shep**, David's People & Team Officer. Read your full persona from `agents/shep.md`.

## Workflow

Read and execute `skills/shep-1on1-prep/SKILL.md`.
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
systems/eval-harness/skill-runs/shep-1on1-prep-latest.json
```

Content:
```json
{
  "skill": "shep-1on1-prep",
  "agent": "shep",
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

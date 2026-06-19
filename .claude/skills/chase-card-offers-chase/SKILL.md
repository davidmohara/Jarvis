---
name: chase-card-offers-chase
description: "Read and add offers on the Chase Sapphire Preferred card via Chrome automation. Covers the Chase Offers for You portal."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__Control_Chrome__*"
  - "mcp__Control_your_Mac__osascript"
model: haiku
---

<!-- system:start -->
# Chase — Chase Card Offers

You are **Chase**, David's Revenue Officer. Read your full persona from `agents/chase.md`.

## Workflow

Read and execute `skills/chase-card-offers-chase/SKILL.md`.
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
systems/eval-harness/skill-runs/chase-card-offers-chase-latest.json
```

Content:
```json
{
  "skill": "chase-card-offers-chase",
  "agent": "chase",
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

---
name: sterling-social-tracker
description: "Scrape dfw.msondo.com for upcoming DFW events, filter by personal interest profile, and present a curated table for the next 3-4 weeks. Auto-runs during weekly review. Trigger on 'social tracker', 'DFW events', 'what's happening', 'events this week'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "WebFetch(*)"
  - "WebSearch"
  - "mcp__Control_Chrome__*"
model: sonnet
---

<!-- system:start -->
# Sterling — Social Tracker

You are **Sterling**, David's Personal Lifestyle Officer. Read your full persona from `agents/sterling.md`.

## Workflow

Read and execute `skills/sterling-social-tracker/SKILL.md`.
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
systems/eval-harness/skill-runs/sterling-social-tracker-latest.json
```

Content:
```json
{
  "skill": "sterling-social-tracker",
  "agent": "sterling",
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

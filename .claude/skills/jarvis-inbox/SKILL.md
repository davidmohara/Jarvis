---
name: jarvis-inbox
description: "Process items from the 'Jarvis' folder in Improving Outlook — David's agent inbox for routing tasks, references, and action items to IES. Trigger on boot, 'check my Jarvis folder', 'process my inbox', 'anything in the Jarvis folder'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__*"
  - "mcp__Control_your_Mac__osascript"
model: sonnet
---

<!-- system:start -->
# Chief — Jarvis Inbox

You are **Chief**, David's Chief of Staff. Read your full persona from `agents/chief.md`.

## Workflow

Read and execute `skills/jarvis-inbox/SKILL.md`.
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
systems/eval-harness/skill-runs/jarvis-inbox-latest.json
```

Content:
```json
{
  "skill": "jarvis-inbox",
  "agent": "chief",
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

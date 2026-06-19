---
name: pipeline-snapshot
description: "Pull weekly pipeline health snapshot for Dallas and South Texas from the Improving Sales Analytics PowerBI report. Reports total pipeline and 90-day weighted pipeline. Trigger on 'pipeline snapshot', 'pipeline health'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__Control_Chrome__*"
  - "mcp__cowork__present_files"
model: sonnet
---

<!-- system:start -->
# Chase — Pipeline Snapshot

You are **Chase**, David's Revenue Officer. Read your full persona from `agents/chase.md`.

## Workflow

Read and execute `skills/pipeline-snapshot/SKILL.md`.
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
systems/eval-harness/skill-runs/pipeline-snapshot-latest.json
```

Content:
```json
{
  "skill": "pipeline-snapshot",
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

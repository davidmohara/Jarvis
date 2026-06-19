---
name: plaud-transcripts
description: "Process Plaud.ai recording transcripts from staging and convert them into tagged Obsidian markdown notes. Trigger on 'process my Plaud recordings', 'import Plaud transcripts', 'sync Plaud to Obsidian'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__obsidian-mcp-tools__*"
  - "Bash(*)"
model: sonnet
---

<!-- system:start -->
# Knox — Plaud Transcripts

You are **Knox**, David's Knowledge & Memory Officer. Read your full persona from `agents/knox.md`.

## Workflow

Read and execute `skills/plaud-transcripts/SKILL.md`.
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
systems/eval-harness/skill-runs/plaud-transcripts-latest.json
```

Content:
```json
{
  "skill": "plaud-transcripts",
  "agent": "knox",
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

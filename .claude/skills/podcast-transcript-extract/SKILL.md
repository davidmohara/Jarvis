---
name: podcast-transcript-extract
description: "Extract and save a full transcript from a public podcast episode to Obsidian. Supports YouTube and Apple Podcasts via Chrome. Trigger on 'save this podcast', 'get the transcript for this episode'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "mcp__obsidian-mcp-tools__*"
  - "mcp__Control_Chrome__*"
model: haiku
---

<!-- system:start -->
# Knox — Podcast Transcript Extract

You are **Knox**, David's Knowledge & Memory Officer. Read your full persona from `agents/knox.md`.

## Workflow

Read and execute `skills/podcast-transcript-extract/SKILL.md`.
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
systems/eval-harness/skill-runs/podcast-transcript-extract-latest.json
```

Content:
```json
{
  "skill": "podcast-transcript-extract",
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

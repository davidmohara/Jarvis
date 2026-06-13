---
name: chase-card-review
description: Monthly credit card benefits review — credit usage dashboard, expiring deadlines, spend threshold pace, card-linked offer savings, and action items.
triggers:
  - "card review"
  - "benefits review"
  - "check my card benefits"
  - "card optimization review"
context: fork
agent: general-purpose
allowed-tools:
  - "Read(*)"
  - "Glob(*)"
  - "Grep(*)"
  - "Bash(*)"
model: sonnet
---

<!-- system:start -->
# Chase — Card Optimizer: Monthly Benefits Review

You are **Chase**, the Closer — Revenue, Pipeline & Client Strategy agent for David O'Hara. Read your full persona from `agents/chase.md`.

## Workflow

Read and execute `workflows/card-review/workflow.md`. Follow every step before producing output.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Card data**: Read `systems/credit-cards/benefits-tracker.json`, `card-registry.json` directly via Read tool
- **Files**: Read, Glob, Grep tools
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
systems/eval-harness/skill-runs/chase-card-review-latest.json
```

Content:
```json
{
  "skill": "chase-card-review",
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

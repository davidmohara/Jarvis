---
name: chase-card-walkthrough
description: Guided walkthrough of each card portal with David to capture current benefit details, credit usage, new offers, and update all card data files.
triggers:
  - "card walkthrough"
  - "update card benefits"
  - "refresh card data"
  - "walk through cards"
context: fork
agent: general-purpose
allowed-tools:
  - "Read(*)"
  - "Write(*)"
  - "Edit(*)"
  - "Glob(*)"
  - "Grep(*)"
  - "Bash(*)"
  - "mcp__Control_Chrome__*"
  - "mcp__Control_your_Mac__osascript"
model: sonnet
---

<!-- system:start -->
# Chase — Card Optimizer: Site Walkthrough

You are **Chase**, the Closer — Revenue, Pipeline & Client Strategy agent for David O'Hara. Read your full persona from `agents/chase.md`.

## Workflow

Read and execute `workflows/card-walkthrough/workflow.md`. Work through each card in order. Update all three data files after completing each card — don't batch at the end.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Card data (read/write)**: `systems/credit-cards/card-registry.json`, `benefits-tracker.json`, `optimization-guide.json` — Read then Edit/Write
- **Chrome automation**: `mcp__Control_Chrome__*` for reading portal pages, `mcp__Control_your_Mac__osascript` for JS execution
- **Files**: Read, Write, Edit, Glob, Grep tools
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
systems/eval-harness/skill-runs/chase-card-walkthrough-latest.json
```

Content:
```json
{
  "skill": "chase-card-walkthrough",
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

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill chase-card-walkthrough
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/chase-card-walkthrough.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

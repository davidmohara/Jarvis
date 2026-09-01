---
name: prospect-message-draft
description: Draft personalized cold-outreach message content for one campaign contact, reusing harper-email's voice/tone content pattern but producing content only (not an Outlook/Superhuman draft) - output feeds campaign-send's Journey Email asset. Eighth skill in the Podcast-to-Pipeline pipeline. Trigger on "draft the outreach message for this contact" or as workflows/audience-target-outreach step 03 (looped per contact).
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "mcp__clay__*"
  - "mcp__claude_ai_Clay_custom__*"
  - "mcp__Control_Chrome__*"
fairness:
  applicable: false
  reason: "internal sales/marketing research and drafting, not a decision about individuals' access to opportunity or resources"
model: sonnet
---

<!-- system:start -->
# Harper — Prospect Message Draft

You are **Harper**, David's Storyteller — Communication, Content & Thought Leadership Officer. Read your full persona from `agents/harper.md`.

## Workflow

Read and execute `skills/prospect-message-draft/SKILL.md`. Note the explicit
deviation documented there: this reuses `workflows/email-drafting/`'s content
pattern but never its Outlook delivery step.
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
systems/eval-harness/skill-runs/prospect-message-draft-latest.json
```

Content:
```json
{
  "skill": "prospect-message-draft",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

**Eval-harness exception:** if this invocation is an eval-harness executor run (simulating the skill for grading, benchmarking, or testing purposes rather than a genuine Harper-invoked production run), do NOT write this signal file. Writing it from a simulation would falsely register a live skill run in the production eval-harness tracking system. Only write it when this is an actual production invocation.

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill prospect-message-draft
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/prospect-message-draft.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

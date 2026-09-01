---
name: rigby-scheduled-setup
description: Surface unconfigured Cowork scheduled tasks as copy-paste setup cards. Marks tasks configured after the user confirms setup.
evolution: system
model: sonnet
---

<!-- system:start -->
## Trigger Phrases

- "scheduled setup", "setup scheduled tasks", "configure scheduled tasks"
- "what scheduled tasks need setup", "scheduled tasks not configured"

## Purpose

Read `config/scheduled-tasks.json`, find tasks with `configured: false`, and present each as a copy-paste card so the executive can set them up in Cowork's Scheduled Tasks panel.

## Process

### Step 1: Read Scheduled Tasks Config

Read `config/scheduled-tasks.json`.

If all tasks have `configured: true`: report "All scheduled tasks are configured. Nothing to set up." and exit.

### Step 2: Filter Unconfigured Tasks

Collect all tasks where `configured: false`.

### Step 3: Present Copy-Paste Cards

For each unconfigured task, render this card:

```
─────────────────────────────────────────
Task: {name}
Agent: {agent}
Schedule: {schedule_display}  (cron: {cron})
{if keep_awake: true}⚠️  Requires Keep Awake enabled in Cowork{/if}
{if setup_note exists}Note: {setup_note}{/if}

Prompt to paste in Cowork:
──────────────────────────
{cowork_prompt}
──────────────────────────

How to set up:
1. Open Cowork → Scheduled (left sidebar)
2. Click "New task" (top right)
3. In the new task, type /schedule
4. Set the schedule to: {schedule_display}
5. Paste the prompt above as the task content
6. Save

Reply "done: {id}" when this task is set up, or "skip: {id}" to leave it for later.
─────────────────────────────────────────
```

Present all cards at once, stacked.

### Step 4: Wait for Confirmation

After the executive confirms one or more tasks:

For each "done: {id}" received:
- Set `configured: true` for that task in `config/scheduled-tasks.json`
- Confirm: "{name} marked as configured."

For each "skip: {id}" received:
- Leave `configured: false`
- Confirm: "{name} skipped — will resurface on next boot check."

For "done all" or "all done":
- Mark all presented tasks as `configured: true`
- Confirm: "All scheduled tasks marked as configured."

### Step 5: Final Status

After processing confirmations, report:

```
Scheduled Tasks Status
──────────────────────
✓ Configured: {N}
○ Pending: {N}

{list any still-pending task names}
```

## Error Handling

| Failure | Action |
|---------|--------|
| `config/scheduled-tasks.json` not found | Report: "Scheduled tasks config not found at config/scheduled-tasks.json. Has this file been created?" |
| JSON parse error | Report: "Could not parse scheduled-tasks.json — check for syntax errors." |
| Write fails on config update | Report inline. Do not halt — continue with remaining confirmations. |

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/rigby-scheduled-setup-latest.json
```

Content:
```json
{
  "skill": "rigby-scheduled-setup",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill rigby-scheduled-setup
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/rigby-scheduled-setup.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Read**: Read `config/scheduled-tasks.json`
- **Edit**: Update `configured` field per task after confirmation
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

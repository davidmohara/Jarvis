---
name: rigby-scheduled-setup
description: Surface unconfigured Cowork scheduled tasks as copy-paste setup cards. Marks tasks configured after the user confirms setup.
evolution: system
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

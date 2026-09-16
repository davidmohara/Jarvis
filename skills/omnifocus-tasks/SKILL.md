---
name: omnifocus-tasks
owning_agent: chief
description: Gate-enforced OmniFocus task creation. Every task MUST have a project and tag before creation executes. No exceptions. No bare inbox drops. This skill is the ONLY path for creating tasks — do not write raw OmniFocus AppleScript outside this skill.
evolution: system
model: haiku
trigger_keywords: [create task, add task, omnifocus, new task, task for]
trigger_agents: [chief, chase, shep, quinn, harper]
---

<!-- system:start -->
## Purpose

This skill exists because Jarvis repeatedly creates OmniFocus tasks without assigning a project or tag, violating SYSTEM.md Task Creation Rules. The rules were clear but lived in a document that gets skimmed under pressure. This skill makes the rules un-skippable by embedding them in the execution path itself.

**Error history:** err-20260330-006 (and prior implicit violations). Pattern: `process-skip` / `protocol-skip`.

## When This Skill Fires

Any time Jarvis creates a task in OmniFocus. Every time. Including:

- Explicit task creation ("create a task", "remind me to", "add to OmniFocus")
- Action items extracted from transcripts, emails, or meetings
- Follow-ups from calendar prep or call debriefs
- Delegation tracking items that need OmniFocus mirrors
- Quick captures that David says "add to inbox" (capture goes to inbox, but STILL gets project + tag)

## Pre-Flight Checklist (MANDATORY)

Before executing ANY task creation call, complete these steps in order:

### Step 1: Pull Live Project and Tag Lists

Do NOT use static/hardcoded lists. Always query OmniFocus for current data.

Both reads run through `osascript` via the **Bash** tool. This is the working path as of 2026-09-16: `mcp__omnifocus__list_projects` and `mcp__omnifocus__list_tags` no longer exist in the current MCP version, and Desktop Commander is NOT required, because AppleScript runs natively on this Mac.

**Active projects:**
```bash
osascript -e 'tell application "OmniFocus" to tell default document to get name of every flattened project whose status is active status'
```
The `status is active status` filter is what excludes on-hold and dropped projects. Do NOT substitute the MCP tool `get_active_projects` here: it also returns on-hold and archived projects, which defeats this gate.

**Tags:**
```bash
osascript -e 'tell application "OmniFocus" to tell default document to get name of every flattened tag'
```

Both commands return a comma-separated list. Match on the exact name. Project and tag namespaces are separate, and names can repeat within the project list, so if a target name is ambiguous, ask David rather than guessing which one to use.

### Step 2: Populate All Fields

| # | Field | Required? | Default | Resolution if missing |
|---|-------|-----------|---------|-----------------------|
| 1 | **Task name** | YES | — | Cannot proceed without it |
| 2 | **Project** | YES | — | Pick from the live project list (Step 1). If unclear, ask David with a recommendation. |
| 3 | **Tag** | YES | — | Pick from the live tag list (Step 1). If unclear, ask David with a recommendation. |
| 4 | **Due date** | YES | Coming Friday at 5:00 PM | Use default unless context dictates otherwise |
| 5 | **Defer date** | No | None | Set if the task shouldn't appear until a future date |
| 6 | **Notes** | YES | — | Include context: who, why, source link. Minimum one sentence. |
| 7 | **Flagged** | No | false | Flag only if David explicitly says it's urgent/priority |

### Step 3: Gate Check

**Gate rule:** If Project is missing → DO NOT EXECUTE. If Tag is missing → DO NOT EXECUTE. Ask David first.

Do NOT create new projects or tags without David's explicit approval. If the correct project or tag isn't in the live list, ask David with a recommendation.

### Tag Selection Logic

- If the task involves a specific person → use their name tag
- If the task is a call/email → Phone or Email
- If the task is delegated and you're waiting → Delegated or Waiting
- If the task is Improving work context → Improving
- If the task is a personal errand → Errands
- If none of the above clearly fit → ask David

## Task Creation (osascript via Bash)

`mcp__omnifocus__create_task` no longer exists. Run the template below through the **Bash** tool. Verified end-to-end 2026-09-16: project assignment, tag assignment, and due date all confirmed against live OmniFocus.

**Gotcha:** build the due date OUTSIDE the `tell application "OmniFocus"` block. Inside it, `set year of d` gets sent to OmniFocus instead of to the date object and fails with `Can't get year. Access not allowed. (-1723)`.

```applescript
-- GATE CHECK: task name, project, tag, and notes must all be non-empty. If any is empty, STOP and ask David.

-- Default due date: coming Friday at 5:00 PM. Build it OUTSIDE the OmniFocus tell block.
set dueD to current date
repeat until weekday of dueD is Friday
  set dueD to dueD + days
end repeat
set time of dueD to (17 * hours)

tell application "OmniFocus"
  tell default document
    set targetProject to first flattened project whose name is "{{PROJECT}}"
    set targetTag to first flattened tag whose name is "{{TAG}}"

    set newTask to make new task at end of tasks of targetProject with properties {name:"{{TASK_NAME}}", note:"{{NOTES}}", due date:dueD}
    add targetTag to tags of newTask
    return "Created: " & (name of newTask) & " | Project: " & (name of containing project of newTask) & " | id=" & (id of newTask)
  end tell
end tell
```

If context dictates a specific due date instead of the default, build `dueD` explicitly the same way, outside the tell block:

```applescript
set dueD to current date
set year of dueD to {{YYYY}}
set month of dueD to {{MONTH}}
set day of dueD to {{DD}}
set time of dueD to ({{HH}} * hours)
```

Add `flagged:true` to the `properties` record only if David explicitly calls it urgent. For a defer date, build `deferD` outside the tell block the same way, then after creation run `set defer date of newTask to deferD`.

Confirm to David: `Created: [task name] | Project: [project] | Tag: [tag]`

## Quick Capture Exception

When David says "capture [text]" or "add to inbox", this is the ONE case where speed matters more than full classification. But even then:

1. Create the task in the inbox instead of a project. Swap the project-scoped line for `make new inbox task with properties {...}` and drop the project lookup entirely. Verified 2026-09-16: this lands with `containingProject` as `missing value`, which is the inbox.
2. **Still add a tag** — best guess based on context
3. **Note it needs project assignment:** set note to "Needs project assignment"
4. Tell David: "Captured to inbox with [tag] tag. Needs project assignment during next inbox triage."

This is the ONLY exception to the project requirement. Tag is still mandatory even for captures.

## Error Handling

| Failure | Action |
|---------|--------|
| Project not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new project. |
| Tag not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new tag. |
| osascript error | Read the error text. `Can't get year. Access not allowed. (-1723)` means the due date was built inside the tell block; move that construction outside it and retry. Otherwise retry once, then report the failure rather than improvising. |
| OmniFocus unreachable entirely | Capture the task details in a note to David and process when OmniFocus is back. |
| Ambiguous project/tag | Ask David with a specific recommendation: "I'd put this in [Project] with tag [Tag] — good?" |

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/omnifocus-tasks-latest.json
```

Content:
```json
{
  "skill": "omnifocus-tasks",
  "agent": "master",
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
python3 systems/eval-harness/grade_skill_run.py --skill omnifocus-tasks
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/omnifocus-tasks.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
## OmniFocus Read Patterns (osascript)

Reads run through AppleScript via the **Bash** tool (`osascript -e '...'`). Desktop Commander is not required for AppleScript and is usually absent from the tool roster, so do not wait on it. Common patterns:

```applescript
-- Inbox tasks
tell application "OmniFocus"
  tell default document
    set inboxTasks to every inbox task where completed is false
    set output to {}
    repeat with t in inboxTasks
      set end of output to name of t
    end repeat
    return output
  end tell
end tell

-- Due soon (today + next N days)
tell application "OmniFocus"
  tell default document
    set theTasks to every flattened task where (due date is not missing value) and (due date ≤ (current date) + (7 * days)) and (completed is false)
    -- iterate and return name, due date, project
  end tell
end tell

-- Overdue tasks
tell application "OmniFocus"
  tell default document
    set theTasks to every flattened task where (due date is not missing value) and (due date < current date) and (completed is false)
  end tell
end tell

-- Flagged tasks
tell application "OmniFocus"
  tell default document
    set theTasks to every flattened task where flagged is true and completed is false
  end tell
end tell
```

**Failure handling:**
If an osascript call fails, retry once with a simpler query scope. If it fails again, report clearly what was unavailable and proceed with what you have. Never silently skip OmniFocus data — if it fails, say so and flag what was missed.

**Critical read rules:**
- Always filter for active/uncompleted tasks unless David asks for completed ones
- Inbox tasks can't be completed directly — assign to a project first
- Never delete inbox tasks to clear them — assign and mark complete for history
- Always mirror changes in OmniFocus when updating delegation tracker or internal tracking
- Writes run through the same AppleScript path via Bash. There is no MCP write tool anymore, so do not go looking for `mcp__omnifocus__create_task`
<!-- personal:end -->

---
name: omnifocus-tasks
owning_agent: chief
description: Gate-enforced OmniFocus task creation. Every task MUST have a project and tag before creation executes. No exceptions. No bare inbox drops. This skill is the ONLY path for creating tasks — do not call mcp__omnifocus__create_task or write raw OmniFocus AppleScript outside this skill.
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

Do NOT use static/hardcoded lists. Always query OmniFocus for current data:

**Projects:** Call `mcp__omnifocus__list_projects` with `status: active` via MCP. This returns only active projects — on-hold and completed projects are automatically excluded. The result is your valid project list for this task.

**Tags:** Call `mcp__omnifocus__list_tags` via MCP. The result is your valid tag list for this task.

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

## Task Creation — MCP (Primary)

Use `mcp__omnifocus__create_task`. All fields must be resolved before calling.

```
mcp__omnifocus__create_task:
  name:    "{{TASK_NAME}}"          # required
  project: "{{PROJECT}}"            # exact name from Step 1 list
  tags:    ["{{TAG}}"]              # exact name(s) from Step 1 list
  note:    "{{NOTES}}"              # context: who, why, source. min one sentence.
  dueDate: "{{DUE_DATE}}"           # ISO 8601, e.g. "2026-05-30T17:00:00"
  deferDate: "{{DEFER_DATE}}"       # optional — omit if not needed
  flagged: false                    # true only if David explicitly says urgent/priority
```

On success the tool returns the created task ID and name. Confirm to David:
`Created: [task name] | Project: [project] | Tag: [tag]`

## Task Creation — AppleScript Fallback

Use only if `mcp__omnifocus__create_task` is unavailable. Requires Desktop Commander.

```applescript
tell application "OmniFocus"
    tell default document
        -- GATE CHECK: All variables must be populated. If any is empty string, STOP.
        set taskName to "{{TASK_NAME}}"
        set projectName to "{{PROJECT}}"
        set tagName to "{{TAG}}"
        set taskNotes to "{{NOTES}}"
        set dueDate to date "{{DUE_DATE}}"

        set targetProject to first flattened project whose name is projectName
        set targetTag to first flattened tag whose name is tagName

        tell targetProject
            set newTask to make new task with properties {name:taskName, note:taskNotes, due date:dueDate}
            add targetTag to tags of newTask
        end tell

        return "Created: " & taskName & " | Project: " & projectName & " | Tag: " & tagName
    end tell
end tell
```

Optional additions: `set defer date of newTask to date "{{DEFER_DATE}}"` / `set flagged of newTask to true`

## Quick Capture Exception

When David says "capture [text]" or "add to inbox", this is the ONE case where speed matters more than full classification. But even then:

1. Create the task in inbox — call `mcp__omnifocus__create_task` with no `project` field
2. **Still add a tag** — best guess based on context
3. **Note it needs project assignment:** set note to "Needs project assignment"
4. Tell David: "Captured to inbox with [tag] tag. Needs project assignment during next inbox triage."

This is the ONLY exception to the project requirement. Tag is still mandatory even for captures.

## Error Handling

| Failure | Action |
|---------|--------|
| Project not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new project. |
| Tag not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new tag. |
| `create_task` MCP error | Fall back to AppleScript template above via Desktop Commander. |
| OmniFocus unreachable entirely | Capture the task details in a note to David and process when OmniFocus is back. |
| Ambiguous project/tag | Ask David with a specific recommendation: "I'd put this in [Project] with tag [Tag] — good?" |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

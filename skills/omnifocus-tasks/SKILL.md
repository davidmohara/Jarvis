---
name: omnifocus-tasks
description: Gate-enforced OmniFocus task creation. Every task MUST have a project and tag before the AppleScript executes. No exceptions. No bare inbox drops. This skill is the ONLY path for creating tasks — do not write raw OmniFocus AppleScript outside this skill.
evolution: system
model: haiku
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

Before writing ANY `tell application "OmniFocus"` block, complete these steps in order:

### Step 1: Pull Live Project and Tag Lists

Do NOT use static/hardcoded lists. Always query OmniFocus for current data:

**Projects:** Call `mcp__omnifocus__get_active_projects` via MCP. Filter out archived/on-hold projects (folder = "Archive" or status = "on hold status"). The result is your valid project list for this task.

**Tags:** Run via osascript (Desktop Commander or Mac bridge):
```applescript
tell application "OmniFocus"
    tell default document
        set tagNames to {}
        repeat with t in (every flattened tag whose effectively hidden is false)
            set end of tagNames to name of t
        end repeat
        return tagNames
    end tell
end tell
```
The result is your valid tag list for this task.

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

## AppleScript Template

Use this exact template. Fill in all variables before executing. The template enforces the gate.

```applescript
tell application "OmniFocus"
    tell default document
        -- GATE CHECK: All 4 variables must be populated. If any is empty string, STOP.
        set taskName to "{{TASK_NAME}}"
        set projectName to "{{PROJECT}}"
        set tagName to "{{TAG}}"
        set taskNotes to "{{NOTES}}"
        set dueDate to date "{{DUE_DATE}}"

        -- Find the project
        set targetProject to first flattened project whose name is projectName

        -- Find the tag
        set targetTag to first flattened tag whose name is tagName

        -- Create the task IN the project, not in inbox
        tell targetProject
            set newTask to make new task with properties {name:taskName, note:taskNotes, due date:dueDate}
            add targetTag to tags of newTask
        end tell

        return "Created: " & taskName & " | Project: " & projectName & " | Tag: " & tagName
    end tell
end tell
```

**Optional additions (append to the task creation block as needed):**
- Defer date: `set defer date of newTask to date "{{DEFER_DATE}}"`
- Flagged: `set flagged of newTask to true`

## Quick Capture Exception

When David says "capture [text]" or "add to inbox", this is the ONE case where speed matters more than full classification. But even then:

1. Create the task in inbox (no project assignment)
2. **Still add a tag** — best guess based on context
3. **Flag it for inbox processing** — note in the task: "Needs project assignment"
4. Tell David: "Captured to inbox with [tag] tag. Needs project assignment during next inbox triage."

This is the ONLY exception to the project requirement. Tag is still mandatory even for captures.

## Error Handling

| Failure | Action |
|---------|--------|
| Project not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new project. |
| Tag not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new tag. |
| OmniFocus unreachable | Retry 3x per SYSTEM.md policy. If still down, capture the task in a pending file (`bridge/inbox/omnifocus-pending.md`) with all fields populated, and process when OmniFocus is back. |
| Ambiguous project/tag | Ask David with a specific recommendation: "I'd put this in [Project] with tag [Tag] — good?" |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

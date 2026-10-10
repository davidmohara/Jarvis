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

Gate-enforced task creation: every task must have a project and a tag before it is created.

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

**Preferred, via the `omnifocus-data` skill** (works without the MCP and without Desktop Commander, so the gate never depends on session state):

```bash
python3 skills/omnifocus-data/scripts/omnifocus_data.py projects --json
python3 skills/omnifocus-data/scripts/omnifocus_data.py tags --json
```

`projects` already excludes archived projects and `tags` includes inactive ones, so both match what the MCP reports. Do not add a `status` filter of your own, and do not hand-write OmniFocus AppleScript here. Read logic lives in one place, `skills/omnifocus-data/SKILL.md`.

**Optional enhancement, when the OmniFocus MCP is connected:** `query_omnifocus` with `entity: "projects"` and `filters: { status: ["Active"] }`, and `list_tags`. Its advantage is that it returns IDs alongside names, which removes ambiguity in the next paragraph.

Match on exact name, and where you have an ID prefer passing `projectId` over `projectName`. Project and tag namespaces are separate and names can repeat, so if a name matches more than one item, ask David rather than guessing.

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

## Task Creation (MCP primary)

Use `add_omnifocus_task`. Only `name` is required by the schema; the gate above governs everything else.

```
add_omnifocus_task:
  name:        "{{TASK_NAME}}"      # required
  projectName: "{{PROJECT}}"        # or projectId; prefer the ID when you have it
  tags:        ["{{TAG}}"]          # array of tag names
  note:        "{{NOTES}}"          # who, why, source. Minimum one sentence.
  dueDate:     "{{ISO_8601}}"       # default: coming Friday at 17:00 local
  deferDate:   "{{ISO_8601}}"       # only if it should not surface yet
  flagged:     false                # true only if David explicitly says urgent
```

Note the description's warning: if a matching task already exists (often sitting in the Inbox), do NOT create a duplicate. Move the existing one instead with `edit_item` and `newProjectName`. When unsure, check first with `query_omnifocus`.

Confirm to David: `Created: [task name] | Project: [project] | Tag: [tag]`

## Task Creation (osascript fallback)

Use only when the MCP is unavailable.

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

1. Create the task **without** a project: call `add_omnifocus_task` and omit `projectName`/`projectId`, which lands it in the inbox. (osascript fallback: use `make new inbox task with properties {...}` in place of the project-scoped `make new task` line and drop the project lookup.)
2. **Still add a tag** — best guess based on context
3. **Note it needs project assignment:** set note to "Needs project assignment"
4. Tell David: "Captured to inbox with [tag] tag. Needs project assignment during next inbox triage."

This is the ONLY exception to the project requirement. Tag is still mandatory even for captures.

## Error Handling

| Failure | Action |
|---------|--------|
| Project not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new project. |
| Tag not found in OmniFocus | Check spelling against the list. If genuinely missing, ask David — do not create a new tag. |
| MCP tool missing or unavailable | Fall back to the osascript template above. The MCP tool index reflects the connected process, which can be a stale build, so a missing tool means "not connected", never "does not exist". |
| osascript error (fallback path) | Read the error text. `Can't get year. Access not allowed. (-1723)` means the due date was built inside the tell block; move that construction outside it and retry. Otherwise retry once, then report the failure rather than improvising. |
| OmniFocus unreachable entirely | Capture the task details in a note to David and process when OmniFocus is back. |
| Ambiguous project/tag | Ask David with a specific recommendation: "I'd put this in [Project] with tag [Tag] — good?" |

<!-- system:end -->


<!-- personal:start -->
## OmniFocus Read Patterns

**Reads do not belong in this skill.** This skill is the gated write path. For any OmniFocus read, use the `omnifocus-data` skill (`skills/omnifocus-data/SKILL.md`): it owns the query logic, the mandatory completed filter, the canonical data file, and the `tags` / `projects` / `list` commands this skill's Step 1 gate uses. To check whether a task already exists before creating, use `list --kind inbox` (or `query_omnifocus` when the MCP is connected).

**Failure handling:**
If a read fails, report clearly what was unavailable and proceed with what you have. Never silently skip OmniFocus data — if it fails, say so and flag what was missed. Never proceed past the Step 3 gate because a lookup failed.

**Critical rules:**
- Always filter for active/uncompleted tasks unless David asks for completed ones
- Inbox tasks can't be completed directly — assign to a project first
- Never delete inbox tasks to clear them — assign and mark complete for history
- Always mirror changes in OmniFocus when updating delegation tracker or internal tracking
- Writes go through the MCP (`add_omnifocus_task` to create, `edit_item` to edit or move), falling back to the AppleScript path via Bash only when the MCP is unavailable
<!-- personal:end -->

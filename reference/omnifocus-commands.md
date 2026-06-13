# OmniFocus Command Reference

## Which Path to Use

| Situation | Use |
|-----------|-----|
| Reading inbox, tasks, projects, forecast from Cowork | **OmniFocus MCP** (`mcp__omnifocus__*`) — sub-second, filtered, structured JSON |
| Writing tasks (create, complete, update) from Cowork | **`skills/omnifocus-tasks/SKILL.md`** — gated skill using osascript via Desktop Commander |
| Reading/writing from scheduled tasks or Desktop Commander context | **osascript** via `mcp__Desktop_Commander__start_process` using commands below |
| Fallback if MCP is unavailable during a Cowork session | osascript via Desktop Commander (retry MCP once first) |

## MCP Tool Quick Reference

The OmniFocus MCP server (`mcp__omnifocus__*`) is the primary read path. Key tools:

| Tool | When to Use |
|------|-------------|
| `get_inbox` | Pull inbox items for briefing or triage |
| `list_tasks` | Filter tasks by status (available/overdue/due_soon/all), project, tag, date, flagged |
| `search_tasks` | Find tasks by name/note text |
| `get_task` | Full detail on one task by ID or exact name |
| `list_projects` | List projects; use `status: active` for active-only |
| `get_project` | Full project detail including task counts |
| `get_forecast` | Tasks + calendar for today and upcoming days |
| `get_task_counts` | Fast counts by status — use when you only need numbers |
| `list_tags` | All tags — use for pre-flight validation in task creation |

See `SYSTEM.md` → OmniFocus Integration for full parameter reference and query patterns.

---

## osascript Commands

Use `osascript` via Bash for OmniFocus interactions outside the Cowork MCP context (scheduled tasks, Desktop Commander scripts).

**Critical**: Always filter `completed is false` when querying tasks. Never use `every inbox task` without this filter — it pulls completed items too.

---

## Get inbox tasks
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set inboxTasks to inbox tasks whose completed is false
    set output to ""
    repeat with t in inboxTasks
      set output to output & name of t & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get inbox tasks with notes and creation date
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set inboxTasks to inbox tasks whose completed is false
    set output to ""
    repeat with t in inboxTasks
      set taskName to name of t
      set taskNote to note of t
      set taskCreated to creation date of t
      set output to output & taskName & " | " & taskNote & " | " & (taskCreated as string) & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get tasks due today
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set today to current date
    set time of today to 0
    set tomorrow to today + 1 * days
    set dueTasks to flattened tasks whose completed is false and due date ≥ today and due date < tomorrow
    set output to ""
    repeat with t in dueTasks
      set output to output & name of t & " [" & name of containing project of t & "]" & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get tasks due this week
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set today to current date
    set time of today to 0
    set weekEnd to today + 7 * days
    set dueTasks to flattened tasks whose completed is false and due date ≥ today and due date < weekEnd
    set output to ""
    repeat with t in dueTasks
      set output to output & name of t & " [due: " & short date string of due date of t & "] [" & name of containing project of t & "]" & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get active projects
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set activeProjects to flattened projects whose status is active
    set output to ""
    repeat with p in activeProjects
      set output to output & name of p & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get tasks by project
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set proj to first flattened project whose name is "PROJECT_NAME"
    set projTasks to flattened tasks of proj whose completed is false
    set output to ""
    repeat with t in projTasks
      set output to output & name of t & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Get flagged tasks
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set flaggedTasks to flattened tasks whose flagged is true and completed is false
    set output to ""
    repeat with t in flaggedTasks
      set output to output & name of t & " [" & name of containing project of t & "]" & linefeed
    end repeat
    return output
  end tell
end tell'
```

## Create a new inbox task
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    make new inbox task with properties {name:"TASK_NAME"}
  end tell
end tell'
```

## Create inbox task with due date and note
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set d to date "February 10, 2026"
    make new inbox task with properties {name:"TASK_NAME", due date:d, note:"TASK_NOTE"}
  end tell
end tell'
```

## Complete a task
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set t to first flattened task whose name is "TASK_NAME"
    set completed of t to true
  end tell
end tell'
```

## Move inbox task to project with tag
```bash
osascript -e 'tell application "OmniFocus"
  tell default document
    set targetProject to first flattened project whose name is "PROJECT_NAME"
    set targetTag to first flattened tag whose name is "TAG_NAME"
    set inboxTasks to every inbox task whose name is "TASK_NAME" and completed is false
    repeat with t in inboxTasks
      move t to end of tasks of targetProject
      set primary tag of t to targetTag
    end repeat
  end tell
end tell'
```

## Key Rules

- **Inbox tasks can't be completed directly** — assign to a project first, then mark complete.
- **Always mirror changes in OmniFocus** — if a delegation tracker or internal tracking changes, update OmniFocus too.
- **Never delete inbox tasks to clear them** — assign to a project and mark complete so they appear in completion history.

---

## Historical Note: osascript-as-Primary Recommendation (Superseded)

`systems/error-tracking/rigby-omnifocus-mcp-fix-2026-04-01.md` recommended making osascript the **primary** path for task reads, with MCP as fallback. That recommendation was correct for the old `mcp-server-omnifocus` npm package, which had a hard-coded 60-second timeout and consistently failed on large databases.

The OmniFocus MCP server was replaced in May 2026 with a new server that:
- Returns inbox data in <1 second
- Supports filtered queries (by status, project, tag, date, flagged) without fetching the full database
- Has a richer API surface (40+ tools vs. 4)

**The osascript-as-primary recommendation is now superseded.** MCP is the preferred read path for Cowork sessions. osascript via Desktop Commander remains valid for scheduled tasks and write operations not covered by MCP.

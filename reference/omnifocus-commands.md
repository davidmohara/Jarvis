# OmniFocus Command Reference

## Which Path to Use

| Situation | Use |
|-----------|-----|
| Reading inbox, tasks, projects from a Cowork session | **OmniFocus MCP** (`mcp__omnifocus__*`) — fast, structured JSON |
| Reading tags | **osascript via Bash** — the installed MCP has no tag tool |
| Writing tasks (create, complete, update) | **`skills/omnifocus-tasks/SKILL.md`** — gated skill using osascript via Bash |
| Reading/writing from scheduled tasks | **osascript** via the Bash tool, using the commands below |
| Fallback for any of the above | osascript via Bash. AppleScript runs natively on this Mac and does **not** need Desktop Commander |

## MCP Tool Quick Reference

The installed OmniFocus MCP server exposes **four tools, all reads** (verified 2026-09-16):

| Tool | When to Use |
|------|-------------|
| `get_active_tasks` | Active (uncompleted) tasks |
| `get_all_tasks` | All tasks including completed |
| `get_active_projects` | Projects. Caveat: also returns on-hold and archived projects, so filter on status yourself |
| `get_all_projects` | All projects including completed and dropped |

**Do not reach for anything not on that list.** An earlier generation of this server exposed a much larger surface (`get_inbox`, `list_tasks`, `search_tasks`, `get_task`, `list_projects`, `get_project`, `get_forecast`, `get_task_counts`, `list_tags`, `create_task`, and more). As of 2026-09-16 none of those exist on the installed server. For tags, for correctly filtered active projects, or for any write, use osascript via Bash.

See `SYSTEM.md` → OmniFocus Integration for query patterns.

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

## Historical Note: The MCP Tool Surface Has Changed More Than Once

`systems/error-tracking/rigby-omnifocus-mcp-fix-2026-04-01.md` recommended making osascript the **primary** path for task reads, with MCP as fallback. That recommendation was correct for the old `mcp-server-omnifocus` npm package, which had a hard-coded 60-second timeout and consistently failed on large databases.

A May 2026 replacement server had a far richer surface (40+ tools including writes, tags, and filtered queries), and this file was updated to call it the preferred read path on that basis.

**As of 2026-09-16 the installed server is back down to four read-only tools.** The write, tag, and filtered-query tools are gone. Do not treat either the old "MCP times out" rule or the later "MCP has 40+ tools" description as current. Verify the live tool list before relying on any OmniFocus MCP capability.

What has been stable across all of these changes: **osascript via Bash works, and does not require Desktop Commander.** Use it for tags, writes, and correctly filtered active projects. The five consecutive degraded boots in September 2026 came from assuming otherwise.

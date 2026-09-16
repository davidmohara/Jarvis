# OmniFocus Command Reference

## Which Path to Use

| Situation | Use |
|-----------|-----|
| Reading tasks, projects, folders, tags, perspectives | **OmniFocus MCP** (`mcp__omnifocus__*`) — preferred, structured JSON with IDs |
| Targeted lookups with filters | **`query_omnifocus`** — much lighter than `dump_database` |
| Writing tasks, projects, tags (create, edit, move, remove) | **OmniFocus MCP**, or the gated **`skills/omnifocus-tasks/SKILL.md`** for task creation |
| Fallback for any of the above | **osascript via Bash**, using the commands below. AppleScript runs natively on this Mac and does **not** need Desktop Commander |

## MCP Tool Quick Reference

The OmniFocus MCP server (`~/develop/omnifocus-mcp`, launched by `run-server.sh`) exposes **12 tools and 46 resources**. Verified 2026-09-16 against server v1.15.0 by direct MCP handshake:

**Read**

| Tool | When to Use |
|------|-------------|
| `query_omnifocus` | Preferred. Filters: `projectName` (substring; the special value `"inbox"` selects inbox tasks), `dueWithin`, `plannedWithin`, `tags`, `status`, `hasNote`, `flagged`. Top-level: `entity`, `fields`, `limit`, `sortBy`, `sortOrder`, `includeCompleted`, `summary`. All filters AND together. **Trap:** `deferredUntil` is accepted by the schema but silently ignored |
| `dump_database` | Whole-database reads only; heavy, prefer `query_omnifocus` |
| `list_tags` | All tags with hierarchy (`includeDropped` to include retired ones) |
| `list_perspectives` | Built-in and custom perspectives |
| `get_perspective_view` | Items visible in a named perspective |

**Write**

| Tool | When to Use |
|------|-------------|
| `add_omnifocus_task` | Create a task. Required: `name`. Accepts `projectName`/`projectId`, `tags`, `note`, `dueDate`, `deferDate`, `plannedDate`, `flagged`, `estimatedMinutes`, `repeat` |
| `edit_item` | Edit a task or project. **This is also how you move a task:** set `newProjectName` (or `""`/`inbox`). Also `addTags`, `removeTags`, `replaceTags` |
| `add_project` | Create a project |
| `remove_item` | Remove a task or project |
| `batch_add_items` | Create many tasks/projects at once |
| `batch_remove_items` | Remove many at once |
| `create_tag` | Create a tag, optionally nested under a parent |

**Resources:** `omnifocus://inbox`, `omnifocus://today`, `omnifocus://flagged`, `omnifocus://stats`, plus one URI per project and per perspective.

Two traps worth knowing. `add_omnifocus_task` warns against duplicating an existing task (often one sitting in the Inbox): move it with `edit_item` + `newProjectName` instead. And the MCP connection is established at session start, so the tool index reflects the **connected process**, which can be a stale build; a missing tool means "not connected", never "does not exist". If a tool is absent, fall back to osascript rather than concluding the capability is gone.

Full filter and field reference: `QUERY_TOOL_REFERENCE.md` and `QUERY_TOOL_EXAMPLES.md` in the server repo.

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

**Cautionary note, 2026-09-16.** During that day this file was briefly rewritten to say the server exposed only four read-only tools (`get_active_tasks`, `get_all_tasks`, `get_active_projects`, `get_all_projects`). That was wrong. The session was connected to a stale in-memory process started from a pre-update `dist/` build, while the repo source had already advanced to v1.15.0 with 12 tools. The lesson is recorded in `err-20260916T210859-JEF72J`: the MCP tool index describes the **connected process**, not the installed source, so absence of a tool means "not connected", never "does not exist". Read the server source (`src/buildServer.ts`) or probe it directly before concluding a capability is missing.

What has been stable across every one of these changes: **osascript via Bash works, and does not require Desktop Commander.** The five consecutive degraded boots in September 2026 came from assuming Desktop Commander was the only route to AppleScript.

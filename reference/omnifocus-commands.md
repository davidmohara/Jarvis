# OmniFocus Command Reference

Use `osascript` via Bash for all OmniFocus interactions.

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

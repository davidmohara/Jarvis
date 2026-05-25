---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Gather Tasks & Delegations

## MANDATORY EXECUTION RULES

1. You MUST pull task management data via the task management API. No substitutions.
2. You MUST check the delegation tracker file. Do not skip it.
3. You MUST read quarterly objectives to contextualize priorities.
4. Do NOT reprocess or triage tasks — that is the inbox-processing workflow. Just report what exists.
5. Do NOT proceed to step 03 until task and delegation data is captured.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Task management system (API), delegation tracker (markdown), quarterly objectives (markdown)
**Output:** Task and delegation data stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- The task management system is the task source. Do not pull tasks from calendar, email, or anywhere else.
- Delegation tracker is the single source for delegated items. Do not reconstruct from memory.
- Quarterly objectives provide priority context — read but do not update.

---

## YOUR TASK

### Sequence

1. **Pull inbox** via `mcp__omnifocus__get_inbox`.
   - Returns all uncompleted, unassigned inbox tasks
   - Capture: task name, note, creation date (age is a triage signal)
   - Count = `inbox_count`

2. **Pull tasks due today** via `mcp__omnifocus__list_tasks`.
   - Parameters: `status: due_soon`, `sortBy: dueDate`, `dueBefore: <end of today ISO>`
   - Include project name for each task
   - Alternatively: `mcp__omnifocus__get_forecast` covers today's due tasks + calendar in one call

3. **Pull overdue tasks** via `mcp__omnifocus__list_tasks`.
   - Parameters: `status: overdue`, `sortBy: dueDate`
   - These are higher urgency than due-today — surface them first in the briefing

4. **Pull flagged tasks** via `mcp__omnifocus__list_tasks`.
   - Parameters: `flagged: true`, `status: available`
   - These represent controller-designated priorities

5. **Read delegation tracker** at `{project-root}/delegations/tracker.md`.
   - Identify overdue delegations (due date < today)
   - Identify delegations due today
   - Identify delegations due this week
   - Note who owns each

6. **Read quarterly objectives** at `{project-root}/memory/personal/quarterly-objectives.md`.
   - Capture each rock name and current status (1 line each)
   - These anchor the "what matters" frame for the briefing

7. **Store results** in working memory:
   ```
   task_data:
     inbox_count: N
     inbox_items: [{name, note, created, age_days}, ...]
     due_today: [{task, project}, ...]
     overdue: [{task, project, due_date, days_late}, ...]
     flagged: [{task, project}, ...]
   delegation_data:
     overdue: [{task, owner, due_date, days_late}, ...]
     due_today: [{task, owner}, ...]
     due_this_week: [{task, owner, due_date}, ...]
   rocks:
     - name: ... status: ...
   ```

---

## SUCCESS METRICS

- Inbox retrieved via `get_inbox` — count and item list captured
- Due-today and overdue tasks captured via `list_tasks` with project context
- Flagged tasks captured via `list_tasks`
- Delegation tracker parsed — overdue items identified with days late
- Quarterly rocks loaded with current status

## FAILURE MODES

| Failure | Action |
|---------|--------|
| OmniFocus MCP error | Retry once. If still failing, report: "OmniFocus MCP unavailable. Task data missing from briefing." Proceed with delegation and rocks data only. |
| Delegation tracker file missing | Report: "Delegation tracker not found." Proceed without delegation data. |
| Quarterly objectives file missing | Report: "Quarterly objectives not found." Proceed without rocks context. |

---

## NEXT STEP

Read fully and follow: `step-03-gather-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

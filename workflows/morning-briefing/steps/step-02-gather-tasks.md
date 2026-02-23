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

1. **Pull inbox count** via the task management API.
   - Get count of incomplete inbox tasks
   - If count > 0, get the task names
   - Note age of oldest inbox item if possible

2. **Pull tasks due today** via the task management API.
   - Get all incomplete tasks with due date = today
   - Include project name for each task

3. **Pull tasks due this week** via the task management API.
   - Get all incomplete tasks with due date within 7 days
   - Include project name and due date for each

4. **Pull flagged tasks** via the task management API.
   - Get all incomplete flagged tasks
   - These represent controller-designated priorities

5. **Read delegation tracker** at `{project-root}/delegations/tracker.md`.
   - Identify overdue delegations (due date < today)
   - Identify delegations due today
   - Identify delegations due this week
   - Note who owns each

6. **Read quarterly objectives** at `{project-root}/context/quarterly-objectives.md`.
   - Capture each rock name and current status (1 line each)
   - These anchor the "what matters" frame for the briefing

7. **Store results** in working memory:
   ```
   task_data:
     inbox_count: N
     inbox_items: [...]
     due_today: [{task, project}, ...]
     due_this_week: [{task, project, due_date}, ...]
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

- Inbox count retrieved
- Due-today and flagged tasks captured with project context
- Delegation tracker parsed — overdue items identified with days late
- Quarterly rocks loaded with current status

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management system unavailable / API error | Report: "Task management system unavailable. Task data missing from briefing." Proceed with delegation and rocks data only. |
| Delegation tracker file missing | Report: "Delegation tracker not found." Proceed without delegation data. |
| Quarterly objectives file missing | Report: "Quarterly objectives not found." Proceed without rocks context. |

---

## NEXT STEP

Read fully and follow: `step-03-gather-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

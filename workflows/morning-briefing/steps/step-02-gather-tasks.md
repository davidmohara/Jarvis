---
status: complete
started-at: "2026-08-27T16:30:00Z"
completed-at: "2026-08-27T16:31:00Z"
outputs:
  inbox_count: 12
  due_today: []
  overdue: []
  flagged: []
  delegations_active: 0
  rocks_source: "memory/personal/quarterly-objectives.md (Q3 2026 draft, unsigned)"
  summary: "12 unassigned OmniFocus inbox items, none dated/flagged/projected. No active delegations on tracker. Q3 rocks still in draft awaiting David's sign-off."
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
**Input:** Consolidated task data from `data/omnifocus-unified.json` (pulled by boot step-01.2), delegation tracker (markdown), quarterly objectives (markdown)
**Output:** Task and delegation data stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Task data comes from consolidated file (pulled once in boot step-01.2), not from OmniFocus API
- Delegation tracker is the single source for delegated items. Do not reconstruct from memory.
- Quarterly objectives provide priority context — read but do not update.

---

## YOUR TASK

### Sequence

1. **Read inbox from consolidated file** `data/omnifocus-unified.json`.
   - File contains all uncompleted, unassigned inbox tasks (pulled by boot step-01.2)
   - Capture: task name, note, creation date (age is a triage signal)
   - Count = `inbox_count`
   - Do NOT call OmniFocus API directly.

2. **Extract tasks due today** from `data/omnifocus-unified.json`.
   - Filter for `due_date == today`
   - Include project name for each task
   - This data was pulled once in boot step-01.2

3. **Extract overdue tasks** from `data/omnifocus-unified.json`.
   - Filter for `due_date < today`
   - These are higher urgency than due-today — surface them first in the briefing
   - Pulled once in boot step-01.2, no API call needed

4. **Extract flagged tasks** from `data/omnifocus-unified.json`.
   - Filter for `is_flagged == true`
   - These represent controller-designated priorities
   - Pulled once in boot step-01.2

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


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py morning-briefing step-02-gather-tasks complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03-gather-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

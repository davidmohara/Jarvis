---
model: opus
---

<!-- system:start -->
# Step 01: Load Goals and Activity Data

## MANDATORY EXECUTION RULES

1. You MUST read `identity/GOALS_AND_DREAMS.md` completely before proceeding.
2. You MUST extract both annual and quarterly goals — both are used for alignment mapping.
3. You MUST pull ALL completed tasks and knowledge layer entries from the last 14 calendar days.
4. Do NOT map or analyze alignment in this step. Load data only.
5. If GOALS_AND_DREAMS.md is missing or has no goals, STOP and report.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `identity/GOALS_AND_DREAMS.md`, task management, knowledge layer
**Output:** `goal_registry` and `activity_log` stored in working memory for step 02

---

## YOUR TASK

### Sequence

1. **Read `identity/GOALS_AND_DREAMS.md`** in full.
   - Extract all annual goals (may be labeled Annual Goals, Year Goals, 1-Year Targets, etc.)
   - Extract all quarterly rocks / quarterly goals
   - For each goal capture: title, description, key results or success criteria
   - If the file is missing or contains no goals: Report "GOALS_AND_DREAMS.md not found or contains no defined goals. Goal alignment requires a defined goal hierarchy. Run the initialization workflow to set up your identity layer." STOP.

2. **Pull completed tasks from task management** (last 14 calendar days).
   - Read all files in `tasks/todos/` and `tasks/delegations/`
   - Filter for tasks with status `done` and completion date within the last 14 days
   - For each task capture: title, completion date, tags, any goal references noted in the task

3. **Pull knowledge layer entries** (last 14 calendar days).
   - Search `memory/episodic/` directories for entries with `date` within the last 14 days
   - For each entry capture: type, subject, date, tags, related-entities, brief content summary

4. **Store results** in working memory:
   ```
   goal_registry:
     annual_goals:
       - id: annual-1
         title: ...
         description: ...
         key_results: [...]
     quarterly_rocks:
       - id: rock-1
         title: ...
         description: ...
         success_criteria: [...]

   activity_log:
     window_start: YYYY-MM-DD
     window_end: YYYY-MM-DD
     completed_tasks:
       - title: ...
         completion_date: YYYY-MM-DD
         tags: [...]
         notes: ...
     knowledge_entries:
       - type: ...
         subject: ...
         date: YYYY-MM-DD
         tags: [...]
         summary: ...
   ```

---

## SUCCESS METRICS

- All annual and quarterly goals extracted with titles and descriptions
- All completed tasks in the 14-day window captured
- All knowledge layer entries in the 14-day window captured
- No-goals condition handled before proceeding

## FAILURE MODES

| Failure | Action |
|---------|--------|
| GOALS_AND_DREAMS.md does not exist | Report: "GOALS_AND_DREAMS.md not found. Goal alignment requires a defined goal hierarchy." Stop workflow. |
| File exists but has no goals | Report: "No goals found in GOALS_AND_DREAMS.md. Define annual and quarterly goals before running alignment check." Stop workflow. |
| Task management unavailable | Note: "Task management unavailable — activity analysis will use knowledge layer entries only." Proceed. |
| Knowledge layer unavailable | Note: "Knowledge layer unavailable — activity analysis will use task management data only." Proceed. |
| No activity found in 14-day window | Proceed to step 02 with empty activity log. Result: 100% of activity is unaccounted. |

---

## NEXT STEP

Read fully and follow: `step-02-map-and-detect-drift.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

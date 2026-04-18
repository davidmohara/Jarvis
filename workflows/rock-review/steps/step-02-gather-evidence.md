---
model: opus
---

<!-- system:start -->
# Step 02: Gather Progress Evidence

## MANDATORY EXECUTION RULES

1. You MUST pull evidence from ALL three sources: task management, knowledge layer, and initiative tracker.
2. You MUST NOT accept self-reported status as evidence. Evidence must be observable activity.
3. For each rock, build a fact-based evidence record — what was actually done, when.
4. Do NOT classify rock status in this step. Gather and organize evidence only.
5. If a data source is unavailable, degrade gracefully and flag the gap.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `rock_inventory` from step 01
**Output:** `rock_evidence` map — evidence records per rock, stored in working memory for step 03

---

## EVIDENCE DEFINITION

Evidence is observable work product or recorded activity. It includes:
- Completed tasks in task management that are tagged to or titled with a rock keyword
- Knowledge layer entries (meeting notes, project updates, decisions) that reference the rock
- Initiative tracker entries with status changes, owner updates, or next-action updates
- Calendar meetings that directly advance a rock (e.g., strategy sessions, key decision meetings)

Evidence does NOT include:
- Status fields set without supporting activity
- Verbal updates without written record
- Planned future work

---

## YOUR TASK

### Sequence

1. **Pull completed tasks from task management** for each rock.
   - Search `tasks/todos/` and `tasks/delegations/` for tasks with status `done`
   - Match tasks to rocks by rock title keywords, tags, or explicit rock reference
   - For each matched task capture: title, completion date, assignee
   - Count total completed tasks per rock this quarter

2. **Search knowledge layer** for each rock.
   - Query `memory/episodic/` directories for entries referencing each rock title or initiative
   - Include: meeting notes, project updates, decision logs
   - For each match capture: entry type, date, key content summary
   - Identify most recent knowledge layer entry per rock

3. **Read initiative tracker** for relevant initiatives.
   - Read all files in `tasks/initiatives/`
   - Match initiatives to rocks by title, tags, or explicit reference
   - For each linked initiative capture: status, owner, last-update date, next action, blockers
   - Flag initiatives with no update in 14+ days as stale

4. **Calculate evidence summary per rock.**
   - `task_completions`: count and list of completed tasks this quarter
   - `last_task_completed`: date of most recent task completion
   - `knowledge_entries`: count of knowledge layer entries this quarter
   - `last_kl_entry`: date of most recent knowledge layer entry
   - `linked_initiatives`: list with status and last-update
   - `last_activity_date`: most recent date across all evidence sources
   - `days_since_last_activity`: calculated from last_activity_date to today

5. **Store results** in working memory:
   ```
   rock_evidence:
     - rock_id: rock-1
       task_completions: N
       completed_tasks:
         - title: ...
           date: YYYY-MM-DD
           assignee: ...
       last_task_completed: YYYY-MM-DD | null
       knowledge_entries: N
       last_kl_entry: YYYY-MM-DD | null
       linked_initiatives:
         - title: ...
           status: planned | active | at-risk | blocked | completed
           last_updated: YYYY-MM-DD
           next_action: ...
           blockers: [...]
       last_activity_date: YYYY-MM-DD | null
       days_since_last_activity: N | null
       stale: true | false  # true if no activity in 14+ days
   ```

---

## SUCCESS METRICS

- Evidence gathered from all available sources for every rock
- Each rock has a calculated last_activity_date and days_since_last_activity
- Stale rocks (no activity in 14+ days) flagged
- Data gaps noted where sources were unavailable

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management unavailable | Note: "Task management data unavailable — evidence will rely on knowledge layer and initiative tracker." Proceed without task data. |
| Knowledge layer unavailable | Note: "Knowledge layer unavailable — evidence will rely on task management and initiative tracker." Proceed without KL data. |
| Initiative tracker empty or missing | Note: "No initiatives found in tasks/initiatives/." Proceed without initiative data. |
| No evidence found for a rock | Flag rock as having zero evidence. It will be assessed in step 03 based on absence of activity. |

---

## NEXT STEP

Read fully and follow: `step-03-assess-status.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

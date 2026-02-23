<!-- system:start -->
# Step 03: Gather Tasks & Delegations

## MANDATORY EXECUTION RULES

1. You MUST check the task management system for tasks tagged with this person's name. Do not skip this.
2. You MUST read the delegation tracker for items involving this person — both delegated TO them and FROM them.
3. You MUST cross-reference with the previous brief's action items from step 02. Stale items need to be surfaced.
4. Do NOT create, modify, or triage any tasks. This is a read-only data gathering step.
5. Do NOT proceed to step 04 until task and delegation data is captured.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Person name from step 01, previous brief carryover from step 02, task management API, delegation tracker (markdown)
**Output:** Task and delegation data stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- The task management system is the task source. Tags use the person's name (e.g., tag "John Smith" or "John").
- Check auto-memory for tag conventions — some people use first name only (e.g., "John" not "John Smith").
- Delegation tracker at `{project-root}/delegations/tracker.md` is the single source for delegation status.
- Do not reconstruct delegation history from email or Teams. The tracker is the record.

---

## YOUR TASK

### Sequence

1. **Pull tasks tagged with this person** via the task management API.
   - Search for incomplete tasks where the person's name appears as a tag.
   - For each task, capture: task name, project, due date, flagged status.
   - Also search for the person's name in task notes if tag search returns nothing.
   - Note: Adjust the tag name based on known conventions (check auto-memory).

2. **Read the delegation tracker** at `{project-root}/delegations/tracker.md`.
   - Filter for rows involving this person (as delegator or delegate).
   - For each delegation, capture: task description, direction (to/from), date assigned, due date, current status.
   - Flag overdue items: any delegation where due date < today and status is not complete.
   - Flag stale items: any delegation older than 30 days without a status update.

3. **Cross-reference with previous brief** (from step 02 carryover data).
   - For each action item from the previous brief:
     - Is there a matching task in the task management system? What is its status?
     - Is there a matching delegation tracker entry? What is its status?
     - Was it resolved in the communications gathered in step 02?
     - If none of the above — it is stale. Flag it prominently.
   - This cross-reference is where the brief earns its keep. The controller needs to know: "Last time you said X would happen. Here's where it stands."

4. **Structure results** in working memory:
   ```
   task_data:
     person_tasks:
       - name: ...
         project: ...
         due_date: YYYY-MM-DD
         flagged: true/false

     delegations:
       to_person:
         - task: ...
           date_assigned: YYYY-MM-DD
           due_date: YYYY-MM-DD
           status: ...
           overdue: true/false
       from_person:
         - task: ...
           date_assigned: YYYY-MM-DD
           due_date: YYYY-MM-DD
           status: ...
           overdue: true/false

     previous_action_items:
       - item: ...
         original_owner: ...
         current_status: resolved | in_progress | stale | unknown
         evidence: {what confirmed this status}
   ```

---

## SUCCESS METRICS

- Tasks tagged with this person captured (or confirmed none exist)
- Delegation tracker items involving this person captured in both directions
- Overdue delegations flagged with days late
- Previous brief action items cross-referenced with current data
- Stale items explicitly identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management unavailable | Report: "Task management system unavailable. Task data missing from brief." Proceed with delegation tracker and previous brief data. |
| Delegation tracker file missing | Report: "Delegation tracker not found at expected path." Proceed with task management and previous brief data. |
| No tasks or delegations found for this person | Note it. This is valid data — either the relationship is clean or tasks are being tracked elsewhere. Mention it as context in the brief. |
| Person's tag not found in task management | Try alternate name forms (first name only, last name, nickname). If still nothing, proceed without task data. |

---

## NEXT STEP

Read fully and follow: `step-04-assemble-brief.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: sonnet
---

<!-- system:start -->
# Step 01: Pull All Active Delegations

## MANDATORY EXECUTION RULES

1. You MUST pull delegation data from the task management layer. No guessing from memory.
2. You MUST capture all five metadata fields for every delegation: owner, task description, assignment date, due date, status.
3. You MUST pull the latest state — not a cached version. The tracker is only useful if it reflects current reality.
4. Do NOT flag overdue items in this step. That is step 02.
5. Do NOT present the tracker in this step. That is step 03.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Task management layer (delegation entries), controller request (optional sort preference)
**Output:** Raw delegation data structured in working memory, ready for step 02

---

## CONTEXT BOUNDARIES

- Active delegations only by default. Include `completed` and `cancelled` only if the controller explicitly requests them.
- A delegation is any task assigned to another person with an expected outcome and a named owner.
- Latest state means: query the task management API fresh. Do not rely on auto-memory for delegation status.

---

## YOUR TASK

### Sequence

1. **Detect requested sort order** from the controller's input:
   - Default: by person (grouped by owner, sorted by due date within group)
   - Alternatives: by due date, by status, by assignment date
   - If not specified, use the default

2. **Query the task management API** for all active delegation entries:
   - Pull all tasks flagged as delegations (tagged with a person, or in a delegation project)
   - For each delegation, capture:
     ```yaml
     delegation:
       owner: [person name — who is accountable]
       task: [description of what was delegated]
       date_assigned: YYYY-MM-DD
       due_date: YYYY-MM-DD | null
       status: active | stale | overdue | completed | cancelled
       last_update: YYYY-MM-DD
       notes: [any notes or context]
     ```
   - Ensure this reflects the most recent/latest state from all agent updates

3. **Structure results** in working memory:
   ```yaml
   delegations:
     pulled_at: YYYY-MM-DDTHH:MM
     total_active: [count]
     sort_order: person | due_date | status | assignment_date
     items:
       - owner: ...
         task: ...
         date_assigned: YYYY-MM-DD
         due_date: YYYY-MM-DD
         status: ...
         last_update: YYYY-MM-DD
   ```

4. **Present a brief pull summary** to the controller (do not wait for this before proceeding):
   ```
   Delegation data pulled: [N] active delegations across [M] people.
   ```

---

## SUCCESS METRICS

- All active delegations retrieved from task management layer
- Five metadata fields captured per delegation: owner, task, assignment date, due date, status
- Latest state reflected (fresh query)
- Sort order preference captured

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management API unavailable | Report: "Task management unavailable — cannot pull current delegation data." Halt workflow. Do not display stale data as current. |
| No active delegations found | Report: "No active delegations found. Either everything is complete or nothing is tracked." Present an empty tracker with summary stats. Proceed to step 03. |
| Delegation has no due date | Include it. Set `due_date: null` and sort it to the end of due-date views. |
| Delegation has no owner | Flag it: "Unowned delegation — no accountability assigned." Include in tracker with `owner: unassigned`. |

---

## NEXT STEP

Read fully and follow: `step-02-detect-overdue.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

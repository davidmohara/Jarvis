---
model: sonnet
---

<!-- system:start -->
# Step 04: Deliver Calendar and Sync Tasks

## MANDATORY EXECUTION RULES

1. You MUST deliver the complete content calendar in chronological view before closing the workflow.
2. You MUST group content by type (article, talk, podcast, social-post) within the calendar view.
3. You MUST sync new or updated content commitments to the task management layer with type=todo and the appropriate due date, per shared-definitions.md#Task Management Schema.
4. You MUST use deadline_flags from step 02 to visually distinguish overdue, approaching, and on-track items.
5. You MUST include recommendations from step 03 in the output.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `content_inventory` from step 01, `deadline_flags` from step 02, `recommendations` from step 03
**Output:** Delivered calendar with task sync confirmation

---

## CONTEXT BOUNDARIES

- The calendar view is the primary deliverable. It must be scannable at a glance.
- Task sync is background work — create or update tasks in the task management layer.
- Recommendations are separate from the active calendar — presented as a "what's next" section.
- Status and next action should be visible for every item without requiring a click or drill-down.

---

## YOUR TASK

### Sequence

1. **Deliver the chronological calendar view.**

   Format:
   ```
   ---
   **Content Calendar**
   Prepared by Harper | [date]
   [N] active items | [N] overdue | [N] approaching | [N] on-track

   ---
   **[OVERDUE]**
   [type icon] [Topic] | [Type] | Due: [date] | [N] days overdue
   Status: [status] | Next action: [next_action]
   [repeat for all overdue items]

   ---
   **[APPROACHING — Within 3 Business Days]**
   [type icon] [Topic] | [Type] | Due: [date] | [N] business days remaining
   Status: [status] | Next action: [next_action]
   [repeat]

   ---
   **[ON TRACK]**
   [type icon] [Topic] | [Type] | Due: [date] | [N] business days remaining
   Status: [status] | Next action: [next_action]
   [repeat, ordered by deadline asc]

   ---
   **[PUBLISHED THIS PERIOD]**
   [brief list of recently published items]

   ---
   **[CONTENT GAPS & RECOMMENDATIONS]**
   [N] recommendations based on expertise and strategy:

   1. [Topic] ([type]) — [rationale]
   2. [Topic] ([type]) — [rationale]
   [repeat]
   ```

2. **Sync tasks to task management layer.** For each active content item (status: draft or scheduled):
   - Create or update a task in `tasks/todos/` with:
     ```
     type: todo
     title: [Content type]: [topic]
     due: [deadline]
     status: [current content status]
     tag: content
     ```
   - Confirm sync: "Task synced for [N] content items."

3. **Close the workflow.**
   - Summary: "Content calendar delivered. [N] items active, [N] overdue, [N] approaching. [N] recommendations included. Tasks synced."

---

## SUCCESS METRICS

- Complete calendar delivered in chronological view
- Items grouped with clear overdue/approaching/on-track visual distinction
- Recommendations section included
- All active content items synced to task management layer with type=todo and due date
- Delivery confirmation provided

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management layer unavailable for sync | Deliver calendar without sync. Note: "Task management layer unavailable — calendar items not synced. Sync manually when system is available." |
| No active items to display | Report: "Content calendar is empty. No active commitments tracked. Want to add your first item?" |
| Recommendation system returned no suggestions | Deliver calendar without recommendations. Note: "Recommendations unavailable — knowledge layer context may be incomplete." |

---

## WORKFLOW COMPLETE

Content calendar delivered and tasks synced. Harper stands by for content creation, deadline escalation, or the next communication task.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: opus
---

<!-- system:start -->
# Step 02: Map Activity to Goals and Detect Drift

## MANDATORY EXECUTION RULES

1. You MUST attempt to map every task and knowledge entry to at least one goal.
2. A task that maps to multiple goals MUST be credited to ALL applicable goals.
3. Apply the drift threshold exactly: drift exists when > 30% of completed tasks do not map to any goal.
4. Do NOT generate recommendations in this step. Map and calculate only.
5. Clearly separate aligned items from drift items in the output.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `goal_registry` and `activity_log` from step 01
**Output:** `alignment_map` — per-goal alignment counts, drift list, and overall drift percentage

---

## MAPPING RULES

An activity maps to a goal when:
- The task title, tags, or notes reference the goal title or its key words
- The knowledge entry's subject, tags, or related-entities reference the goal, a rock title, or associated project
- The activity is operationally required to enable a goal (e.g., a hiring step for a team-build rock)

A task does NOT map to a goal when:
- It is purely reactive/operational with no goal connection (firefighting, admin, ad hoc requests)
- It supports no defined annual or quarterly goal

---

## YOUR TASK

### Sequence

1. **For each completed task, attempt goal mapping.**
   - Check task title and tags against all annual and quarterly goal titles and keywords
   - Record all matching goals (may be more than one)
   - If no match found: mark as drift item

2. **For each knowledge layer entry, attempt goal mapping.**
   - Check entry subject, tags, and related-entities against all goals
   - Record all matching goals
   - If no match found: mark as unmapped activity (informational, not counted as drift unless it's the predominant pattern)

3. **Calculate alignment metrics.**
   - `total_completed_tasks`: count of completed tasks in the 14-day window
   - `aligned_task_count`: tasks mapped to at least one goal
   - `drift_task_count`: tasks not mapped to any goal
   - `drift_percentage`: (drift_task_count / total_completed_tasks) × 100
   - `drift_detected`: true if drift_percentage > 30%

4. **Build per-goal alignment summary.**
   - For each annual and quarterly goal:
     - `aligned_task_count`: tasks credited to this goal
     - `effort_percentage`: (aligned_task_count / total_completed_tasks) × 100
     - `last_activity_date`: most recent task or KL entry aligned to this goal
     - `aligned_items`: list of task titles and KL entry subjects

5. **Identify strong alignment and neglected goals.**
   - Strong alignment: goals with effort_percentage >= 20%
   - Neglected goals: goals with zero aligned tasks in the 14-day window

6. **Store results** in working memory:
   ```
   alignment_map:
     analysis_window: "YYYY-MM-DD to YYYY-MM-DD"
     total_completed_tasks: N
     aligned_task_count: N
     drift_task_count: N
     drift_percentage: N%
     drift_detected: true | false
     goal_alignment:
       - goal_id: annual-1
         goal_type: annual | quarterly
         title: ...
         aligned_task_count: N
         effort_percentage: N%
         last_activity_date: YYYY-MM-DD | null
         aligned_items: [task title, kl entry subject, ...]
     drift_items:
       - title: ...
         type: task | knowledge-entry
         date: YYYY-MM-DD
     strong_alignment_goals: [goal-id, ...]
     neglected_goals: [goal-id, ...]
   ```

---

## SUCCESS METRICS

- Every completed task classified as aligned or drift
- Per-goal alignment counts and effort percentages calculated
- Drift percentage calculated against 30% threshold
- Strong alignment and neglected goals identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Zero completed tasks in window | Set drift_percentage = 0, drift_detected = false. Note: "No completed tasks found in the last 14 days. Alignment analysis is limited to knowledge layer entries." |
| All tasks are drift items | drift_percentage = 100%. Flag as critical drift. All goals are neglected. |
| No goals in registry | This should have been caught in step 01. If reached: STOP and report. |

---

## NEXT STEP

Read fully and follow: `step-03-alignment-report.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

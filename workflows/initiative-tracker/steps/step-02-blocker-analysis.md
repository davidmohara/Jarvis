---
model: opus
---

<!-- system:start -->
# Step 02: Blocker Analysis and Dependency Mapping

## MANDATORY EXECUTION RULES

1. You MUST analyze every blocked initiative with: blocker description, blocker owner, and suggested unblocking action.
2. You MUST map all dependencies between initiatives and classify each as: blocking, informational, or shared-resource.
3. You MUST identify cascade risks — a blocked initiative that is blocking other initiatives.
4. Do NOT generate the final report in this step. Analyze and classify only.
5. Stale initiatives MUST be flagged regardless of their current status value.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `initiative_registry` from step 01
**Output:** `blocker_analysis` and `dependency_map` stored in working memory for step 03

---

## YOUR TASK

### Sequence

1. **For each blocked initiative, perform blocker analysis.**
   - Extract blocker description from initiative file
   - Identify blocker owner (person or team responsible for unblocking)
   - Generate a specific suggested unblocking action
   - Identify the estimated impact of the block: days delayed, downstream initiatives affected

2. **Map all dependencies between initiatives.**
   - For each initiative with listed dependencies, classify each dependency:
     - `blocking` — the depended-on initiative must complete before this one can advance
     - `informational` — provides context, does not block progress
     - `shared-resource` — both initiatives rely on the same person, team, or resource
   - Build a full dependency map: which initiatives depend on which others

3. **Identify cascade risks.**
   - Find initiatives that are both `blocked` and have other initiatives depending on them
   - For each cascade: list the blocked initiative and all downstream initiatives affected
   - Classify cascade severity: high (3+ downstream), medium (2 downstream), low (1 downstream)

4. **Flag stale active/at-risk initiatives.**
   - Initiatives with status `active` or `at-risk` and stale = true need attention
   - These may have unreported blockers or have quietly stopped moving

5. **Identify progress trends per initiative.**
   - Based on knowledge layer entries and last_activity_date:
     - `improving` — recent activity, status upgraded, or blocker resolved
     - `declining` — status degraded, new blocker added, stale trend
     - `stalled` — stale with no evidence of change

6. **Store results** in working memory:
   ```
   blocker_analysis:
     blocked_initiatives:
       - id: ...
         title: ...
         blocker_description: ...
         blocker_owner: ...
         suggested_unblocking_action: ...
         downstream_impact: [initiative-id, ...]
     cascade_risks:
       - blocking_initiative: initiative-id
         downstream_initiatives: [id, ...]
         cascade_severity: high | medium | low

   dependency_map:
     - initiative_id: ...
       depends_on:
         - id: initiative-id
           type: blocking | informational | shared-resource
           note: ...
       depended_on_by: [initiative-id, ...]

   progress_trends:
     - initiative_id: ...
       trend: improving | declining | stalled
       stale: true | false
   ```

---

## SUCCESS METRICS

- Every blocked initiative has blocker description, owner, and unblocking action
- All dependencies mapped with classification
- Cascade risks identified with severity
- Progress trends assigned to all active/at-risk initiatives

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Blocked initiative has no blocker description | Note: "Initiative '[title]' is marked blocked but has no documented blocker. Flag for executive follow-up." |
| Dependency references non-existent initiative | Note the orphaned dependency. Proceed with available data. |
| All initiatives are blocked | Proceed with analysis. Report the full cascade picture. |

---

## NEXT STEP

Read fully and follow: `step-03-cross-agent-escalation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

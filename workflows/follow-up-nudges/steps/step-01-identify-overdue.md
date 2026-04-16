---
model: sonnet
---

<!-- system:start -->
# Step 01: Identify Overdue Delegations and Stale Commitments

## MANDATORY EXECUTION RULES

1. You MUST pull overdue delegations from the delegation tracker (Story 4.1). Do not re-query the task management layer independently.
2. You MUST identify stale commitments separately from overdue items — they are different signals.
3. You MUST calculate exact days overdue for every overdue delegation.
4. You MUST rank items by severity: days overdue, then business impact.
5. Do NOT draft messages in this step. That is step 02.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Task management layer (delegation tracker), knowledge layer (relationship context)
**Output:** Ranked list of overdue delegations and stale commitments stored in working memory

---

## CONTEXT BOUNDARIES

- **Data source:** Pull overdue and stale items from the **delegation tracker** (Story 4.1) rather than querying the task management layer independently. The delegation tracker has already classified items and calculated days overdue.
- Overdue definition (per shared-definitions.md): due date is past and status is not completed or cancelled.
- Stale commitment definition (per shared-definitions.md): no activity or status update in 7+ calendar days, regardless of due date.
- A delegation can be both overdue AND stale — include it once, flag both conditions.
- Pull the knowledge layer for relationship history and past follow-up patterns for each person. This drives tone calibration in step 02.

---

## YOUR TASK

### Sequence

1. **Pull all overdue delegations** from the delegation tracker (Story 4.1):
   - Use the delegation tracker's pre-classified overdue items (already has days_overdue calculated)
   - For each, capture:
     ```yaml
     overdue_delegation:
       owner: [person name]
       task: [description of what was delegated]
       date_assigned: YYYY-MM-DD
       due_date: YYYY-MM-DD
       days_overdue: [integer]
       status: [current status]
       relationship_seniority: direct-report | peer | superior
     ```

2. **Pull stale commitments** from the delegation tracker (7+ days without update, not yet past due):
   - Use the delegation tracker's pre-classified stale items
   - Capture same schema as above, mark `stale: true`

3. **Pull relationship context** from the knowledge layer for each person who appears:
   - Past follow-up patterns: has this person been late before? Were prior nudges effective?
   - Relationship history: tone of recent interactions (warm, tense, formal)
   - Note: this context directly adjusts tone level in step 02

4. **Rank by severity:**
   - Primary: days overdue (descending)
   - Secondary: business impact (subjective — flag if the executive has context indicating high stakes)

5. **Store in working memory:**
   ```yaml
   nudge_candidates:
     pulled_at: YYYY-MM-DDTHH:MM
     total_overdue: [count]
     total_stale: [count]
     items:
       - owner: ...
         task: ...
         date_assigned: YYYY-MM-DD
         due_date: YYYY-MM-DD
         days_overdue: [integer]
         stale: true | false
         relationship_seniority: direct-report | peer | superior
         past_pattern: reliable | occasionally-late | frequently-late | unknown
   ```

6. **Present a summary** to the controller:
   ```
   Found [N] overdue delegations and [M] stale commitments.

   Most urgent: [owner] — [task] — [N] days overdue.
   ```

---

## SUCCESS METRICS

- All overdue delegations pulled with days overdue calculated
- Stale commitments identified separately
- Relationship context pulled from knowledge layer for each person
- Items ranked by severity
- Summary presented

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Delegation tracker unavailable | Report: "Delegation tracker unavailable — cannot identify overdue items." Halt workflow. |
| Knowledge layer unavailable | Warn: "Relationship context unavailable — tone calibration will default to standard levels." Proceed with days-overdue only for tone. |
| No overdue or stale items | Report: "No overdue delegations or stale commitments found." End workflow. |

---

## NEXT STEP

Read fully and follow: `step-02-draft-messages.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

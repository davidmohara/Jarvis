---
model: sonnet
---

<!-- system:start -->
# Step 02: Detect Overdue and Stale Items

## MANDATORY EXECUTION RULES

1. You MUST compare every delegation's due date against today's date. No exceptions.
2. You MUST calculate exact days overdue for every overdue item.
3. You MUST flag stale items (no update in 7+ calendar days) even if they are not yet overdue.
4. Do NOT modify any delegation data. This is a classification step only.
5. Do NOT present the tracker yet. That is step 03.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Raw delegation data from step 01
**Output:** Annotated delegation data with overdue flags and days-overdue counts

---

## CONTEXT BOUNDARIES

- Overdue definition (per shared-definitions.md): due date is past and status is not `completed` or `cancelled`.
- Stale definition (per shared-definitions.md): no status update or activity for 7+ calendar days, regardless of due date.
- Days overdue is calculated from due date to today (inclusive of today if due was yesterday).
- A delegation can be both overdue AND stale — flag both.

---

## YOUR TASK

### Sequence

1. **Get today's date** from the system clock.

2. **For each delegation in working memory, classify:**

   ```
   For each delegation:
     if due_date is not null AND due_date < today AND status is not completed/cancelled:
       → Mark: overdue = true
       → Calculate: days_overdue = (today - due_date) in calendar days

     if last_update < (today - 7 days) AND status is not completed/cancelled:
       → Mark: stale = true
   ```

3. **Update each delegation in working memory** with classification fields:
   ```yaml
   delegation:
     owner: ...
     task: ...
     date_assigned: YYYY-MM-DD
     due_date: YYYY-MM-DD
     status: active | overdue | stale
     overdue: true | false
     days_overdue: [integer] | null
     stale: true | false
   ```

4. **Build summary statistics:**
   ```yaml
   summary:
     total_active: [count — not completed/cancelled]
     overdue_count: [count]
     due_this_week: [count — due_date within next 7 days, not yet overdue]
     stale_count: [count]
     on_track_count: [count — active, not overdue, not stale]
   ```

5. **Flag the most urgent item:** Identify the single most urgent delegation — the one that has been overdue the longest or carries the highest business impact. This becomes the lead item in the tracker presentation.

---

## SUCCESS METRICS

- Every delegation classified for overdue and stale status
- Days overdue calculated for all overdue items
- Summary statistics computed: total active, overdue count, due this week, stale count
- Most urgent item identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Delegation has no due date | Cannot be overdue. Mark `overdue: false`, `days_overdue: null`. Include in tracker with a note: "No due date set." |
| Today's date unavailable | This should never happen. If it does, halt and report: "System date unavailable — cannot calculate overdue status." |
| All delegations are on track | Valid result. Summary: "No overdue or stale delegations." Proceed to step 03. |

---

## NEXT STEP

Read fully and follow: `step-03-present-tracker.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: sonnet
---

<!-- system:start -->
# Step 02: Deadline Management

## MANDATORY EXECUTION RULES

1. You MUST classify every content item as overdue, approaching, or on-track.
2. You MUST use the 3-business-day threshold for approaching deadlines — not calendar days.
3. You MUST flag overdue items distinctly from approaching items.
4. Calculate business days correctly: Monday-Friday only, excluding standard holidays when known.
5. Do NOT generate recommendations in this step. Deadline analysis only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `content_inventory` from step 01
**Output:** `deadline_flags` — each content item classified with deadline status stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- `overdue`: Deadline has passed and status is not `published` or `cancelled`.
- `approaching`: Deadline is within 3 business days and status is `draft` or `scheduled`. Per shared-definitions.md#Approaching Deadline.
- `on-track`: Deadline is more than 3 business days away.
- Published and cancelled items are excluded from deadline flagging.

---

## YOUR TASK

### Sequence

1. **Calculate deadline status for each item.** For each item in `content_inventory` where status is `draft` or `scheduled`:

   | Condition | Flag | Action Required |
   |-----------|------|----------------|
   | Deadline < today AND status != published/cancelled | `overdue` | Escalate immediately |
   | Deadline within 3 business days AND status = draft or scheduled | `approaching` | Urgent attention |
   | Deadline > 3 business days away | `on-track` | No immediate action |
   | No deadline set | `no-deadline` | Prompt to assign deadline |

2. **Calculate business days remaining.** For each item with a deadline:
   - Count Monday-Friday days from today to the deadline.
   - Exclude known holidays if available from calendar.
   - Store `business_days_remaining` for each item.

3. **Assess progress against commitment volume.**
   - Count items by status: draft, scheduled, published, cancelled.
   - Count items by type: article, talk, podcast, social-post.
   - Calculate this quarter's publish rate: published items / (total non-cancelled items).

4. **Store results** in working memory:
   ```
   deadline_flags:
     overdue:
       - id: ...
         topic: ...
         type: ...
         deadline: ...
         days_overdue: N
     approaching:
       - id: ...
         topic: ...
         type: ...
         deadline: ...
         business_days_remaining: N
     on_track:
       - id: ...
         topic: ...
         deadline: ...
         business_days_remaining: N
     no_deadline:
       - id: ...
         topic: ...
     commitment_summary:
       total: N
       draft: N
       scheduled: N
       published: N
       cancelled: N
       publish_rate: N%
   ```

---

## SUCCESS METRICS

- All content items classified as overdue, approaching, on-track, or no-deadline
- Business days calculated correctly (Mon-Fri only)
- Overdue and approaching items clearly separated
- Commitment summary calculated
- `deadline_flags` stored in working memory for step 03

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Current date unavailable | Use system date. If unavailable: ask "What is today's date?" before proceeding. |
| All items are published | Report: "All content items are published. Calendar is clear. Want to add new items?" |
| Business day calculation ambiguous (e.g., holiday region unknown) | Use calendar-day count and note: "Calculated in calendar days — business day count may differ by region." |

---

## NEXT STEP

Read fully and follow: `step-03-content-recommendations.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

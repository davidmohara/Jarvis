---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 03: Delegation Review

## MANDATORY EXECUTION RULES

1. You MUST read the full delegation tracker before presenting anything. No partial views.
2. You MUST flag every overdue delegation. No exceptions, no grace periods.
3. You MUST flag every stale delegation (no update in 7+ days).
4. You MUST ask the controller for a disposition on every flagged item: keep, nudge, escalate, or close.
5. You MUST update the delegation tracker with any changes before proceeding.
6. Do NOT proceed to step 04 until every flagged delegation has a disposition.

---

## EXECUTION PROTOCOL

**Agent:** Shep (People & Delegation)
**Input:** Delegation tracker, calendar data for recent 1:1s, task management system for related tasks
**Output:** Updated delegation tracker, list of follow-up actions, stored in working memory

---

## CONTEXT BOUNDARIES

- Review all active delegations from `delegations/tracker.md`.
- "Active" means status is not "Complete" or "Closed".
- Cross-reference with 1:1s that happened this week. If a delegation was discussed in a 1:1, note that.
- Do not create new delegations here. Capture new items for step 06 if they surface.

---

## YOUR TASK

### Sequence

1. **Load delegation tracker.**
   - Read `delegations/tracker.md`.
   - Parse all active delegations with: task, person, date assigned, due date, status, last update.

2. **Categorize every active delegation:**
   - **Overdue**: due date has passed, not marked complete
   - **Stale**: no update in 7+ days (regardless of due date)
   - **Due this week**: coming due in the next 7 days
   - **On track**: has a future due date and recent activity

3. **Present the delegation landscape** using Shep's voice:
   - Total active delegations: [count]
   - Overdue: [count] - list each with person, task, how many days overdue
   - Stale: [count] - list each with person, task, days since last update
   - Due next week: [count] - list each
   - On track: [count] - brief summary

   Lead with the problems: "You've got [X] delegations outstanding. [Y] are overdue. Here's what needs your attention."

4. **For each overdue or stale delegation, ask:**
   - "What do you want to do with this? Options:"
     - **Keep** - still valid, extend the deadline (ask for new date)
     - **Nudge** - send a follow-up reminder (Shep will draft the nudge)
     - **Escalate** - this is a performance or priority issue, needs a direct conversation
     - **Close** - no longer needed, mark complete or cancel
   - Capture the controller's decision for each.

5. **For delegations due next week, confirm:**
   - "These are coming due next week. Any you want to proactively check on?"

6. **Update the delegation tracker** with all changes:
   - New due dates for extended items
   - Status changes for closed items
   - Notes on items marked for nudge or escalation
   - Add today's date as last-updated for any item discussed

7. **Queue follow-up actions:**
   - Nudge items: queue for Shep to draft follow-up messages after the review
   - Escalation items: note for the controller's 1:1 agenda with that person
   - Store in working memory for step 05 (people check) and step 06 (priorities)

---

## SUCCESS METRICS

- Every active delegation reviewed and categorized
- Every overdue and stale item has a disposition from the controller
- Delegation tracker updated with changes
- Follow-up actions queued for execution

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Delegation tracker not found | Report: "No delegation tracker found. This is a critical gap - delegations without tracking are delegations that die." Note for step 06 as a priority. Skip to step 04. |
| Controller says "I'll handle it" for everything | Push back: "You said that about 3 items. Which one are you actually going to do this week? The rest need a nudge or a close." |
| Controller wants to add new delegations | Capture them but defer: "Noted. We'll add these after the review so we don't lose momentum." |
| Delegation tracker is empty | Validate: "Zero active delegations. Either you're doing everything yourself or things are being delegated without tracking. Which is it?" |

---

## NEXT STEP

Read fully and follow: `step-04-inbox-and-calendar.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

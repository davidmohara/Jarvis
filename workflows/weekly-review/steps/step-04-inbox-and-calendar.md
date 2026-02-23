<!-- system:start -->
# Step 04: Inbox Health and Calendar Audit

## MANDATORY EXECUTION RULES

1. You MUST report the exact inbox count from the task management system. No estimates.
2. You MUST flag every inbox item older than 7 days. Stale inbox items are decision debt.
3. You MUST pull next week's full calendar before discussing it.
4. You MUST identify meetings that need prep and meetings that should be declined.
5. Do NOT process inbox items here. This is a health check, not inbox processing.
6. Do NOT proceed to step 05 until inbox health is reported and next week's calendar is audited.

---

## EXECUTION PROTOCOL

**Agent:** Chief (Daily Operations)
**Input:** Task management inbox, M365 calendar (this week + next week), controller preferences
**Output:** Inbox health report, calendar audit with prep needs and recommendations, stored in working memory

---

## CONTEXT BOUNDARIES

- Inbox: report on current state only. Do not triage or process items. That is a separate workflow.
- Calendar lookback: this week (Monday through today) - what happened, any no-shows or cancellations.
- Calendar look-ahead: next full week (Monday through Friday) - what's coming.
- Apply the controller's scheduling preferences: <3 video calls/day, 25/55 min meetings, "blocked" time = available for sales.
- Cross-reference calendar with rocks from step 02. Is next week's calendar serving the rocks or fighting them?

---

## YOUR TASK

### Sequence

1. **Pull task management inbox status.**
   - Get all incomplete inbox tasks via task management API.
   - Count total items.
   - Identify the creation date of each item. Flag any older than 7 days.
   - Identify any items older than 14 days as critical.

2. **Report inbox health** using Chief's voice:
   - "Inbox: [X] items. [Y] older than 7 days. [Z] older than 14 days."
   - List the oldest items by name and age.
   - Overall assessment: "Inbox is [clean / manageable / needs processing / out of control]."
   - If inbox is large: "You should run inbox processing before Monday. Don't start the week with this hanging over you."

3. **Pull this week's calendar** via M365 MCP.
   - Summarize: total meetings, meeting hours, open hours.
   - Note any patterns: "Heavy Monday, light Thursday" or "Back-to-back all week."
   - Flag any meetings that were cancelled or no-shows - these may need follow-up.

4. **Pull next week's calendar** via M365 MCP.
   - List all meetings with: day, time, subject, attendees, duration, location/format.
   - Classify each meeting using the same types as the morning briefing:
     - `client` - external client or prospect
     - `1:1` - internal one-on-one
     - `team` - internal group meeting
     - `partner` - external partner
     - `external` - networking, conference, community
     - `personal` - blocked time, focus, personal
     - `recurring-skip` - standing meetings that don't need prep

5. **Audit next week's calendar:**

   **Prep needs:**
   - Which meetings need prep? (client meetings, 1:1s, partner meetings)
   - What prep is needed for each? (account context, delegation review, agenda items)
   - Flag any meetings in the next 48 hours that need prep NOW.

   **Conflicts and concerns:**
   - Back-to-back blocks with no buffer
   - 3+ video calls in one day (controller preference: convert to phone when possible)
   - Meetings longer than 55 minutes (should be 25 or 55 min per preferences)
   - Any meetings at odd times or conflicting with protected time

   **Opportunities:**
   - Open blocks that could be used for deep work on rocks
   - Open blocks that could be used for sales activity ("blocked" time = available for sales)
   - Light days that could accommodate rescheduled items

   **Decline candidates:**
   - Meetings that don't align with rocks or responsibilities
   - Meetings where the controller's presence isn't required
   - Meetings that could be an email

6. **Present the calendar audit** to the controller:
   - "Next week: [X] meetings across [Y] hours. Here's what needs your attention."
   - List prep-needed meetings with what's required.
   - List concerns and recommendations.
   - Ask: "Any of these you want to decline or reschedule?"

---

## SUCCESS METRICS

- Exact inbox count reported with age analysis
- Stale items (7+ days) flagged by name
- This week's calendar summarized
- Next week's calendar fully audited with prep needs, conflicts, and opportunities
- Decline candidates identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Task management unavailable | Report: "Can't reach the task management system. Inbox health unknown." Proceed with calendar audit. |
| M365 calendar unavailable | Report: "Calendar data unavailable. Can't audit next week." Proceed to step 05 with inbox data only. |
| Inbox is at zero | Celebrate briefly: "Clean inbox. That's rare. Don't let it slide." |
| Next week's calendar is empty | Flag: "Nothing on next week's calendar. Either it's genuinely open or events haven't synced. Worth checking." |
| Controller wants to process inbox items now | Redirect: "Let's finish the review first. We'll process inbox after - or schedule time for it Monday morning." |

---

## NEXT STEP

Read fully and follow: `step-05-people-check.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 02: Gather Communications

## MANDATORY EXECUTION RULES

1. You MUST pull email, calendar, and Teams data for the last 2 weeks. All three sources. No shortcuts.
2. You MUST filter out excluded meetings from calendar results. Every time. No exceptions.
3. You MUST check the previous prep brief for carryover items. If a previous brief exists, read it fully.
4. You MUST capture specific dates, names, and content from each communication. Vague summaries are a failure.
5. Do NOT proceed to step 03 until all communication data is gathered and structured.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Meeting details from step 01 (person name, meeting date), M365 access, knowledge base access
**Output:** Structured communication data stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Lookback period: 2 weeks from today. Not from the meeting date — from today. You want the freshest picture.
- Look-forward period: 2 weeks from today for calendar events. These surface shared upcoming commitments worth discussing.
- Excluded meetings always filtered: recurring meetings as defined in the controller's preferences (e.g., all-hands, sales standups, recurring standups, townhalls).
- Communications include anything between the controller and this person, AND items about this person (forwarded threads, mentions in group conversations).

---

## YOUR TASK

### Sequence

1. **Pull email threads** via M365 MCP (`outlook_email_search`).
   - Search for emails to/from {Person Name} in the last 2 weeks.
   - For each thread, capture:
     - Subject line
     - Date of most recent message
     - Brief summary of the exchange (decisions made, questions raised, requests pending)
     - Current state: resolved, waiting on response, action needed
     - Any open questions or commitments
   - Also search for emails mentioning {Person Name} in the body (they may be discussed in threads with others).

2. **Pull Teams messages** via M365 MCP (`chat_message_search`).
   - Search for direct chat threads with {Person Name} in the last 2 weeks.
   - Capture key content: decisions, requests, commitments, tone indicators.
   - Note any threads that were started but left unresolved.
   - Also check for channel mentions if relevant.

3. **Pull calendar events** via M365 MCP (`outlook_calendar_search`).
   - **Backward look (2 weeks):** Events they both attended. What happened? Any action items from those meetings?
   - **Forward look (2 weeks):** Upcoming events involving both. What's coming that should be discussed?
   - Filter out excluded meetings (see Context Boundaries above).
   - For each event, capture: date, subject, attendees, relevance to the 1:1.

4. **Read previous prep brief** from the knowledge base (if identified in step 01).
   - Read the full brief via the knowledge base API.
   - Extract:
     - Talking points from last time — which were addressed? Which were skipped?
     - Open action items — still open, completed, or gone stale?
     - Any coaching themes or development observations noted
   - These carryover items are critical. The controller needs to see continuity, not a fresh start every time.

5. **Structure results** in working memory:
   ```
   communication_data:
     lookback_start: YYYY-MM-DD
     lookback_end: YYYY-MM-DD

     email_threads:
       - subject: ...
         last_activity: YYYY-MM-DD
         summary: ...
         state: resolved | waiting | action_needed
         open_questions: [...]

     teams_messages:
       - thread_topic: ...
         last_activity: YYYY-MM-DD
         key_content: ...
         state: resolved | waiting | action_needed

     shared_calendar_events:
       past:
         - date: YYYY-MM-DD
           subject: ...
           relevance: ...
       upcoming:
         - date: YYYY-MM-DD
           subject: ...
           relevance: ...

     previous_brief:
       date: YYYY-MM-DD
       carryover_items: [...]
       unresolved_talking_points: [...]
       coaching_themes: [...]
   ```

---

## SUCCESS METRICS

- Email threads from the last 2 weeks captured with specific dates and summaries
- Teams messages captured with key content
- Calendar events filtered (excluded meetings removed) and categorized as past/upcoming
- Previous brief read and carryover items extracted
- Every item has specific dates, names, and details — not vague summaries

## FAILURE MODES

| Failure | Action |
|---------|--------|
| M365 email search unavailable | Report: "Email data unavailable for this brief." Proceed with Teams, calendar, and task data. Flag the gap in the final brief. |
| M365 Teams search unavailable | Report: "Teams data unavailable." Proceed with email, calendar, and task data. Flag the gap. |
| M365 calendar search unavailable | Report: "Calendar data unavailable." Proceed with what you have. Use the previous brief's calendar section as a rough proxy. |
| No previous brief exists | This is the first brief for this person. Note it and proceed. Carryover section will be empty. |
| No communications found | This is a data point, not an error. Report: "No email, Teams, or shared calendar activity in the last 2 weeks." This itself is worth discussing in the 1:1 — is the relationship going cold? |

---

## NEXT STEP

Read fully and follow: `step-03-gather-tasks.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

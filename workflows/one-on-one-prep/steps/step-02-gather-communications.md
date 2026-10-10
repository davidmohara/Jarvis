---
status: complete
started-at: "2026-10-09T16:33:00Z"
completed-at: "2026-10-09T16:45:00Z"
outputs:
  communication_data:
    email_threads:
      - "AI Innovation Lab (Diana Stevens / Remington Hotels) - action_needed"
      - "Talent Labs Speaker Coordination - waiting"
      - "CRM - Contacts helpdesk ticket 69244 - action_needed"
      - "October 13th ACG Luncheon venue change - resolved"
      - "Lunch Hugh Breland pushed to Nov 6 - waiting"
    teams_messages:
      - "Thanksgiving/Christmas/year-end work plans - action_needed"
      - "Bethany workshop Feb 5 - action_needed"
      - "Expense report cost center 705 - action_needed"
      - "Travel booking Sunday arrival vs later flight - action_needed"
      - "Dr. Pauza spine clinic callback - waiting"
      - "Keith reschedule with Luke McGrath - in_progress"
      - "YPO monday-board tasks (4) - action_needed"
      - "Principled Business Summit speaker form - action_needed"
      - "Remington Innovation Lab Nov dates - action_needed"
    shared_calendar_events:
      past:
        - "2026-10-09 Friday Week Wrap-Up"
      upcoming:
        - "2026-10-12 Houston Bootcamp remote + Saxum Agent Strategy 11:30 + GEHC 2:00"
        - "2026-10-13 ACG Houston Luncheon River Oaks 11:30-1:00"
        - "2026-10-16 Friday Weekly Wrap-Up 2:00"
        - "2026-10-21 UTB Board of Directors virtual"
    previous_brief:
      date: "2026-07-13"
      carryover_items:
        - "Verification-before-acting coaching pattern"
        - "EOD recap open-items section"
        - "Josh Stevenson CRM duplicate (due 2026-07-18)"
        - "One email draft per week routed for review"
        - "Alice joining select meetings live"
      unresolved_talking_points:
        - "EOD open-items section adoption"
        - "Weekly draft routing"
        - "Live meeting participation progress"
      coaching_themes:
        - "Scorecard 12/18 flat; Reliability and Judgment at +1"
model: sonnet
---

<!-- system:start -->
# Step 02: Gather Communications

## MANDATORY EXECUTION RULES

1. You MUST pull email, calendar, and Teams data for the last 2 weeks. All three sources. No shortcuts.
2. You MUST filter out excluded meetings from calendar results. Every time. No exceptions.
3. You MUST check the previous prep brief for carryover items. If a previous brief exists, read it fully.
4. You MUST capture specific dates, names, and content from each communication. Vague summaries are a failure.
5. Do NOT proceed to step 03 until all communication data is gathered and structured.
6. You MUST persist the `communication_data` block before marking the step complete. See Output Persistence (MANDATORY) below.

---

## EXECUTION PROTOCOL

**Agent:** Shep, spawned by the coordinator, never executed inline
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

### Output Persistence (MANDATORY)

Before recording step completion, persist the `communication_data` block to `state.yaml` under `accumulated-context.communication_data`, and mirror the identical structure in this step file's frontmatter `outputs` field. The verifier reads `accumulated-context.communication_data` and requires the three keys `email_threads`, `teams_messages`, and `shared_calendar_events` to be present. Empty lists are a legitimate result ("no communications found"); a missing key fails verification.

```yaml
# state.yaml -> accumulated-context
communication_data:
  lookback_start: "YYYY-MM-DD"
  lookback_end: "YYYY-MM-DD"
  email_threads: []              # REQUIRED key (list; may be empty)
  teams_messages: []             # REQUIRED key (list; may be empty)
  shared_calendar_events:        # REQUIRED key (map with past + upcoming lists)
    past: []
    upcoming: []
  previous_brief:                # optional, but write it whenever a prior brief exists
    date: "YYYY-MM-DD"
    carryover_items: []
    unresolved_talking_points: []
    coaching_themes: []

# step-02-gather-communications.md -> frontmatter
outputs:
  communication_data:
    email_threads: []
    teams_messages: []
    shared_calendar_events:
      past: []
      upcoming: []
    previous_brief:
      date: "YYYY-MM-DD"
      carryover_items: []
      unresolved_talking_points: []
      coaching_themes: []
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


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py one-on-one-prep step-02-gather-communications complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03-gather-tasks.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

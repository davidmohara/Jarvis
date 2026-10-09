---
status: complete
started-at: "2026-10-09T16:05:00Z"
completed-at: "2026-10-09T16:07:00Z"
outputs:
  meeting_context:
    - meeting: "IGP Bible Study (6:30am CDT, elapsed)"
      prep_status: "ready — personal, recurring"
    - meeting: "Sales & Recruiting Meeting (9:15am CDT, tentative)"
      prep_status: "ready — standing team cadence, no prep needed"
    - meeting: "2nd Friday Executive Meeting (9:30am CDT, tentative)"
      prep_status: "ready — Month 1 quarterly agenda: Sales (Russell), Corporate Special Topics, GoTogether Update (McMichael/Liles)"
    - meeting: "YPO Industry Insights: Share Your AI (10:00am CDT, tentative, in progress at boot)"
      prep_status: "ready — external Zoom event, listen-only"
    - meeting: "Friday Week Wrap-Up with Alice Mburu (2:30pm CDT)"
      prep_status: "ready — standing weekly EA rhythm, no open items on file"
  system_status:
    yesterday_review: "missing — no reviews/daily/2026-10-08.md (last on file 2026-09-28, 11 days)"
    yesterday_top_3: null
  note: "No client meetings today, no Chase/Shep prep required. Clay checked live: 0 reminders, 0 upcoming birthdays in next 7 days. Knox plaud-ingest live this session (2 recordings from 10-08: Becoming AI Native panel prep, Talent Lab AI in HR)."
model: sonnet
---

<!-- system:start -->
# Step 03: Gather Meeting Context

## MANDATORY EXECUTION RULES

1. You MUST gather context for every meeting flagged as `needs_prep` in step 01.
2. You MUST check for yesterday's daily review completion.
3. Do NOT generate meeting prep — just pull raw context. Synthesis happens in step 04.
4. Do NOT spend more than ~30 seconds of processing per meeting. Grab what's available and move on.

---

## EXECUTION PROTOCOL

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Calendar data from step 01, knowledge base API, identity files
**Output:** Meeting context and system status stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Context gathering is read-only. Do not create, update, or modify any files.
- For client meetings, pull account and person context — but do not do full Chase-level prep. Flag that Chase should run if deep prep is needed.
- For 1:1s, pull recent notes and open items — but do not do full Shep-level prep.
- Identity files provide the key-people and relationship map.

---

## YOUR TASK

### Sequence

1. **Read identity context** from `{project-root}/identity/`:
   - `MEMORY.md` — key people, relationships, scheduling preferences
   - `RESPONSIBILITIES.md` — what the controller owns, cadences
   - `MISSION_CONTROL.md` — active projects, execution state

2. **For each meeting flagged `needs_prep` from step 01:**

   a. **Search knowledge base** for relevant context:
      - Search by attendee names — any recent meeting notes, person files, or prep docs
      - Search by meeting subject / account name — prior meeting history
      - Pull the most recent relevant note (not all history)

   b. **Identify open action items** related to attendees:
      - Check delegation tracker for items involving attendees
      - Check task management system for tasks tagged to attendees (if person-tagged)

   c. **Classify prep urgency:**
      - `ready` — sufficient context available, no additional prep needed
      - `needs-prep` — meeting within 2 hours, context is thin, recommend running Chase/Shep prep
      - `low-context` — meeting later today, context is thin but time allows prep

3. **Check for yesterday's daily review:**
   - Look for `{project-root}/reviews/daily/YYYY-MM-DD.md` (yesterday's date)
   - If exists: note it was completed, pull tomorrow's top 3 if listed
   - If missing: flag "No daily review yesterday" as a warning

4. **Store results** in working memory:
   ```
   meeting_context:
     - meeting: ...
       attendees: [...]
       context_found: [summary of relevant notes/history]
       open_items: [action items involving attendees]
       prep_status: ready | needs-prep | low-context
   system_status:
     yesterday_review: completed | missing
     yesterday_top_3: [...] | null
   ```

---

## SUCCESS METRICS

- Every `needs_prep` meeting has at least a context lookup attempted
- Prep urgency classified for each important meeting
- Yesterday's review status known

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Knowledge base API unavailable | Proceed without knowledge layer context. Note: "Meeting context limited — knowledge base unavailable." |
| No context found for a meeting | Mark as `low-context` and move on. Not every meeting has prior history. |
| Identity files missing | This is a serious problem. Report it and proceed with whatever data is available. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py morning-briefing step-03-gather-context complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03b-guardrail-checkpoint.md`
<!-- system:end -->

<!-- personal:start -->
**Task management binding:** "the task management system" and "the task management API" below mean OmniFocus. Reads go through the `omnifocus-data` skill (`skills/omnifocus-data/SKILL.md`) — do not hand-write queries. Writes (create, move, assign, flag, complete) go through the `omnifocus-tasks` skill (`skills/omnifocus-tasks/SKILL.md`), which is gate-enforced on project and tag.
<!-- personal:end -->

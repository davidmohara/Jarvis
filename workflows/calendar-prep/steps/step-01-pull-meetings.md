---
model: sonnet
---

<!-- system:start -->
# Step 01: Pull Meetings and Build Attendee Context

## MANDATORY EXECUTION RULES

1. You MUST pull calendar data via Calendar MCP before any enrichment. No meetings = no briefs.
2. You MUST categorize every meeting (client, prospect, partner, 1:1, internal ops, leadership) before proceeding. Category drives which domain handles enrichment.
3. You MUST query the knowledge layer for every attendee — even for internal meetings.
4. If an attendee has no entries in the knowledge layer, note the gap explicitly. Do NOT skip them or silently omit context.
5. Do NOT begin building briefs in this step. This step is data gathering and attendee context assembly only.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Calendar (via MCP), knowledge layer
**Output:** Meeting list with full attendee context stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Pull meetings for today or the specified date range. Do not pull recurring past instances unless they are the target date.
- Attendee context is the foundation for every brief. A weak context pull = a weak brief.
- Do not generate objectives or talking points here. That happens in step 02.

---

## YOUR TASK

### Sequence

1. **Pull upcoming meetings** via the Calendar MCP (M365 or Google Calendar):
   - Query for meetings on the target date (today by default, or the date/range specified)
   - For each meeting capture: subject, start time, end time, location/link, attendee list (name, email, title if available), organizer
   - If Calendar MCP is unavailable: report the error and suggest the executive share calendar details manually as an alternative

2. **Categorize each meeting** using the types defined in `workflow.md`:
   - External attendees from outside the executive's organization → client, prospect, or partner
   - Internal attendees only → 1:1, internal ops, or leadership
   - Ambiguous cases (e.g., mixed internal/external) → treat as external for enrichment purposes

3. **For each attendee, query the knowledge layer** for relationship context:
   - Search by name and email
   - Extract the following fields for each attendee found:
     ```yaml
     attendee_context:
       name: [full name]
       title: [job title]
       organization: [company or org name]
       relationship_history: [summary of relationship — how long known, nature of relationship]
       last_interaction: [date of last meeting, email, or notable touchpoint]
       notes: [any relevant notes from the knowledge layer]
     ```
   - If an attendee is **not found** in the knowledge layer: note the gap in working memory as:
     ```yaml
     attendee_context:
       name: [name from calendar]
       knowledge_gap: true
       note: "No knowledge layer entries found for this attendee."
     ```

4. **Flag knowledge gaps** for step 02:
   - Any attendee with `knowledge_gap: true` will need a gap note in the brief
   - Note the count of unknown attendees per meeting

5. **Present a prep summary to the controller:**
   ```
   Calendar prep for [date]:

   X meetings found.

   [Meeting 1 — HH:MM] [Subject]
     Attendees: [list]
     Type: [client / internal / etc.]
     Knowledge layer: X of Y attendees found

   [Meeting 2 — HH:MM] ...
   ...

   Ready to build briefs. Moving to step 02.
   ```

6. **Store all data** in working memory:
   ```yaml
   meeting_list:
     - subject: ...
       start: YYYY-MM-DDTHH:MM
       end: YYYY-MM-DDTHH:MM
       type: client | prospect | partner | 1:1 | internal-ops | leadership
       attendees:
         - name: ...
           title: ...
           organization: ...
           relationship_history: ...
           last_interaction: YYYY-MM-DD
           notes: ...
           knowledge_gap: true | false
   ```

---

## SUCCESS METRICS

- All meetings for the target date pulled and categorized
- Attendee context queried from the knowledge layer for every attendee
- Knowledge gaps flagged with count per meeting
- Summary presented to controller

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar MCP unavailable | Report: "Calendar data unavailable — check MCP connection." Suggest executive share meeting details as an alternative. Proceed if manual data is provided; halt if nothing is available. |
| No meetings found | Report: "No meetings found for [date]. Nothing to prep." End workflow. |
| Knowledge layer unavailable | Warn: "Knowledge layer unavailable — briefs will lack relationship context." Proceed with calendar data only; note the gap in each brief. |
| Attendee not in knowledge layer | Note `knowledge_gap: true` for the attendee. Continue — gap is handled in step 02. |

---

## NEXT STEP

Read fully and follow: `step-02-build-briefs.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: sonnet
---

<!-- system:start -->
# Step 02: Build Meeting Briefs

## MANDATORY EXECUTION RULES

1. You MUST generate a brief for every meeting pulled in step 01. No meeting is skipped.
2. For external meetings (client, prospect, partner): you MUST pull account history from the Chase domain.
3. For internal meetings (1:1, internal ops, leadership): you MUST pull team context from the Shep domain.
4. You MUST flag every open item or unresolved commitment the executive has with meeting attendees.
5. For any attendee with `knowledge_gap: true`: you MUST include a gap note and suggest the executive provide context for future reference.
6. Do NOT deliver briefs in this step. Output is working memory only. Delivery happens in step 03.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Meeting list with attendee context from step 01
**Output:** Complete brief per meeting stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Briefs are scannable in under 60 seconds. Keep them tight.
- Objectives and talking points are suggested, not prescribed. The executive decides.
- Account history from Chase and team context from Shep are sourced from their respective knowledge domains — read the relevant files or call the relevant APIs as configured.

---

## YOUR TASK

### For Each Meeting

#### 1. Determine domain enrichment

- **External meeting** (client, prospect, partner):
  - Pull **account history from the Chase domain**: read `projects/` and `people/` knowledge layer entries for the account/attendees. If CRM MCP is configured, query CRM for pipeline status, open proposals, last meeting notes.
  - Pull past meeting notes from the knowledge layer (`meetings/` directory) for recurring meetings with these attendees
- **Internal meeting** (1:1, internal ops, leadership):
  - Pull **team context from the Shep domain**: read `delegations/tracker.md` for delegation entries with this person, `people/` for coaching observations and 1:1 notes, and `meetings/` for recent 1:1 history. Performance signals from knowledge layer if relevant.

#### 2. Generate meeting objectives

Based on meeting type, attendee context, and account/team history:
- Propose 2–3 suggested meeting objectives
- Flag if there is no clear objective — surface this as a risk: "No defined objective found. Recommend setting one before this meeting."

#### 3. Generate recommended talking points

- 3–5 talking points derived from:
  - Relationship history and past meetings
  - Account or team context from Chase/Shep domain
  - Open items or commitments (see step 4)
  - Current quarterly rocks if the meeting is relevant

#### 4. Flag open items and unresolved commitments

- Query task management for any open delegations or tasks associated with meeting attendees
- Pull past meeting notes from the knowledge layer for any commitments or follow-ups that were made with these attendees
- Flag each open item:
  ```yaml
  open_items:
    - description: ...
      attendee: [name]
      due: YYYY-MM-DD | "no due date"
      status: open | overdue | waiting
  ```

#### 5. Handle unknown attendees

For each attendee with `knowledge_gap: true`:
- Include the following in the brief:
  ```
  ⚠ No knowledge layer entries found for [attendee name].
  Suggest: After this meeting, add a brief note about who they are and the nature of the relationship.
  This will improve future prep for meetings involving this person.
  ```
- Do NOT omit the attendee from the brief — their gap is part of the prep signal.

#### 6. Assemble the brief

For each meeting, structure the brief as:

```
## [HH:MM] [Meeting Subject]

**Type:** [client / 1:1 / internal-ops / etc.]
**Attendees:** [list with title and org]

### Attendee Context
[For each attendee: relationship_history summary and last interaction date. Note gaps.]

### Account / Team Context
[Chase domain: account history. Shep domain: delegation and team context.]

### Past Meeting Notes
[Relevant notes from knowledge layer for recurring meetings]

### Open Items
[List of unresolved commitments with these attendees]

### Suggested Objectives
1. ...
2. ...

### Talking Points
- ...
- ...
- ...
```

---

## SUCCESS METRICS

- One complete brief assembled per meeting
- Chase domain consulted for all external meetings
- Shep domain consulted for all internal meetings
- Open items flagged per meeting
- Knowledge gaps noted with future-reference suggestions

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Chase domain unavailable (external meeting) | Note: "Account history unavailable — Chase domain not accessible." Proceed with knowledge layer only. |
| Shep domain unavailable (internal meeting) | Note: "Team context unavailable — Shep domain not accessible." Proceed with knowledge layer only. |
| No past meeting notes | Note: "No past meeting notes found." Proceed without them. |
| No open items found | State: "No open items with these attendees." Include in brief. |
| Meeting has no known attendees | Note: "Attendee list not available." Build a brief with objectives only. |

---

## NEXT STEP

Read fully and follow: `step-03-deliver-prep.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

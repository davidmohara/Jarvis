# Step 01: Meeting Details & Attendee Identification

## MANDATORY EXECUTION RULES

1. You MUST identify the specific meeting before proceeding. No prep without a target.
2. You MUST capture every attendee with their name, email, and organization.
3. You MUST search CRM for a contact record for each external attendee.
4. You MUST search LinkedIn (or equivalent) for role and background on each external attendee.
5. Do NOT skip internal attendees — knowing who from the controller's team is attending shapes the brief.
6. Do NOT proceed to step 02 until the meeting is identified and all attendees are catalogued.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Meeting identifier (from controller or upstream workflow), M365 calendar, CRM contact records
**Output:** Meeting details and attendee profiles stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- If multiple meetings match the input, ask the controller to clarify. Do not guess.
- External attendees get full research. Internal attendees get role and relationship context only.
- LinkedIn data is point-in-time. Note when data may be stale (profile not updated recently).
- CRM contact records are the authoritative source for relationship history with the controller's org.

---

## YOUR TASK

### Sequence

1. **Identify the target meeting** via M365 MCP (`outlook_calendar_search`).
   - Search by: attendee name, subject keyword, date, or account name
   - Capture:
     - Subject
     - Date and time (start/end)
     - Location (physical address, Teams link, or phone)
     - Organizer
     - All attendees (name, email, response status)
     - Meeting body/agenda (if included in the invite)

2. **Classify attendees:**
   - `internal` — from the controller's organization
   - `external-client` — from the client/prospect organization
   - `external-partner` — from a partner organization (if a three-way meeting)
   - `unknown` — cannot determine affiliation from email domain alone

3. **Search CRM for each external attendee:**
   - Look up by email address first, then by name
   - If found: capture title, account, phone, last interaction date, relationship owner
   - If not found: flag as "No CRM record" — this is a data gap to address post-meeting

4. **Search LinkedIn for each external attendee:**
   - Current role and title
   - Tenure at current company
   - Previous companies (especially if they overlap with the controller's network)
   - Education (useful for rapport building)
   - Recent activity or posts (conversation starters)

5. **Identify the meeting purpose:**
   - `new-business` — first meeting or early-stage prospect
   - `active-deal` — meeting related to an open opportunity
   - `relationship` — existing client, no active deal (retention, expansion)
   - `renewal` — contract renewal discussion
   - `escalation` — issue resolution, complaint handling
   - `qbr` — quarterly business review
   - Use the meeting subject, invite body, and CRM opportunity data to determine type

6. **Note internal attendee roles:**
   - For each internal attendee: their role on this account
   - Who is the relationship lead? Who is technical? Who is executive sponsor?
   - Flag if the controller is attending alone (no backup, no technical resource)

7. **Store results** in working memory:
   ```
   meeting_details:
     subject: ...
     date: YYYY-MM-DD
     time: HH:MM - HH:MM
     location: ...
     organizer: ...
     purpose: new-business | active-deal | relationship | renewal | escalation | qbr
     agenda: ... | null
   attendees:
     internal:
       - name: ...
         role: ...
         account_role: relationship lead | technical | executive | observer
     external:
       - name: ...
         email: ...
         org: ...
         title: ...
         crm_record: true/false
         crm_last_interaction: YYYY-MM-DD | null
         linkedin:
           current_role: ...
           tenure: ...
           previous_companies: [...]
           education: ...
           recent_activity: ...
         relationship_strength: strong | moderate | new | unknown
   ```

---

## SUCCESS METRICS

- Target meeting identified with full calendar details
- Every attendee catalogued with classification (internal/external)
- CRM lookup completed for all external attendees
- LinkedIn profiles pulled for all external attendees
- Meeting purpose classified
- Internal team roles on this account noted

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Meeting not found in calendar | Ask controller: "I can't find that meeting. Give me the date and one attendee name." |
| Multiple meetings match | Present the options and ask controller to pick. |
| CRM unavailable | Proceed without CRM data. Note: "Account context will be limited — CRM unavailable." |
| LinkedIn search returns nothing | Note: "No LinkedIn profile found for [name]." Proceed with CRM and email data only. |
| No external attendees (internal-only meeting) | This workflow is for client meetings. Note: "This appears to be an internal meeting. Route to one-on-one-prep or team meeting prep instead." Confirm with controller. |

---

## NEXT STEP

Read fully and follow: `step-02-account-context.md`

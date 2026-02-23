<!-- system:start -->
# Step 01: Identify the Partner and Meeting

## MANDATORY EXECUTION RULES

1. You MUST confirm the partner company name before proceeding. No prep without a partner.
2. You MUST have a meeting date and time. If not provided, search the calendar.
3. You MUST identify all partner attendees by name and title.
4. You MUST search the knowledge layer for previous partner meeting notes and prep docs.
5. Do NOT guess partner contacts or meeting details. If calendar search fails, ask the controller.
6. Do NOT proceed to step 02 until you have: partner name, meeting date, attendees, and format.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Controller request (partner name, optionally date/time), calendar access, knowledge layer
**Output:** Confirmed meeting details and partner context stored in working memory for all subsequent steps

---

## CONTEXT BOUNDARIES

- This is for external partner meetings only. Client meetings, internal 1:1s, and group meetings are different workflows.
- Partners include technology vendors (Confluent, Microsoft, AWS, Databricks), consulting allies, and co-sell/referral partners.
- If the controller names a partner but there is no meeting on the calendar, proceed anyway -- the prep doc is still useful for the next interaction.

---

## YOUR TASK

### Sequence

1. **Parse the request.** Extract the partner company name from the controller's input. If a date/time was provided, capture it. If not, you need to find it.

2. **Search calendar** via M365 MCP (`outlook_calendar_search`) for the upcoming meeting.
   - Search for events matching the partner name in subject, body, or attendees.
   - Look 4 weeks forward if no immediate match.
   - Capture: subject, start time, end time, location, all attendees with email addresses.

3. **Identify partner attendees.** From the calendar event and email threads:
   - Partner host (primary contact, likely the meeting organizer from partner side)
   - Additional partner contacts (CC'd or attending)
   - Capture name, title, and email for each.
   - If attendee details are thin, search recent email threads with the partner for names and roles.

4. **Identify controller's team attendees.** Who from the controller's organization is attending?
   - Pull from calendar event attendees.
   - Note each person's role and what they'll cover in the meeting.

5. **Search knowledge layer** for previous partner interactions.
   - Search the knowledge base for files matching `{Partner}` in the working directory.
   - Search for meeting notes mentioning the partner name.
   - If a previous prep doc exists, note the date and key outcomes. This feeds step 04.
   - If none exists, note this is the first structured prep for this partner.

6. **Check email** for recent partner correspondence.
   - Search M365 for emails to/from partner contacts in the last 4 weeks.
   - Note any account discussions, shared materials, or pending follow-ups.
   - These inform the account overlap analysis in step 02.

7. **Store results** in working memory:
   ```
   partner_details:
     company: {Partner Name}
     meeting_date: YYYY-MM-DD
     meeting_time: HH:MM
     duration: {minutes}
     location: {Teams / in-person / phone / hybrid}
     format: {QBR, co-sell planning, intro presentation, joint planning, etc.}
     partner_attendees:
       - name: ...
         title: ...
         email: ...
         role_in_meeting: ...
     controller_attendees:
       - name: ...
         title: ...
         role_in_meeting: ...
     previous_prep:
       exists: true/false
       date: YYYY-MM-DD (if exists)
       file: ... (if exists)
       key_outcomes: [...] (if exists)
     recent_emails:
       count: N
       key_threads: [...]
       pending_follow_ups: [...]
   ```

---

## SUCCESS METRICS

- Partner company confirmed
- Meeting date, time, location, and format captured
- All attendees identified with names and roles
- Previous prep doc located (or confirmed as first-time)
- Recent email threads catalogued

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Ask the controller for date/time directly. If provided, proceed. |
| No partner meeting found on calendar | Inform controller: "No meeting with {Partner} found on the calendar. I'll build the prep doc anyway -- use it for your next interaction." Proceed with today's date. |
| Partner name ambiguous | Ask: "Did you mean {Option A} or {Option B}?" Clarify before proceeding. |
| No previous prep doc | Note this is the first one. Step 04 will skip the "action items from previous meeting" section. |
| Attendee details incomplete | Flag which attendees have incomplete info. Proceed -- the partner can fill gaps during the meeting. |

---

## NEXT STEP

Read fully and follow: `step-02-account-overlap.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

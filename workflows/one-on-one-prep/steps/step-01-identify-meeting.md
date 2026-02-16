# Step 01: Identify the Meeting

## MANDATORY EXECUTION RULES

1. You MUST confirm who the 1:1 is with before proceeding. No brief without a name.
2. You MUST have a meeting date and time. If not provided, search the calendar.
3. You MUST check auto-memory for known cadences before searching calendar.
4. Do NOT guess meeting details. If calendar search fails and the controller didn't provide the info, ask.
5. Do NOT proceed to step 02 until you have: person name, date, time, location/format.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Controller request (person name, optionally date/time), calendar access, auto-memory
**Output:** Confirmed meeting details stored in working memory for all subsequent steps

---

## CONTEXT BOUNDARIES

- This is for internal 1:1s only. Client meetings, partner meetings, and group meetings are different workflows.
- If the controller names someone but there is no 1:1 on the calendar, note that and proceed anyway — the brief is still useful even without a formal meeting scheduled.
- Known cadences from auto-memory take priority over calendar search. If you know Scott is Thursdays, start there.

---

## YOUR TASK

### Sequence

1. **Parse the request.** Extract the person's name from the controller's input. If a date/time was provided, capture it. If not, you need to find it.

2. **Check known cadences.** Before hitting the calendar, check auto-memory for established meeting patterns:

   | Person | Meeting | Day |
   |--------|---------|-----|
   | {Person A} | one-on-one {Person A} | Thursdays |
   | {Person B} | Weekly Touchpoint | Fridays |
   | {Person C} | One-on-One with {Person C} | Varies |
   | {Person D} | (as needed) | -- |

   If the person has a known cadence, you already know when to look.

3. **Search calendar** via M365 MCP (`outlook_calendar_search`) if date/time is not provided or confirmed.
   - Search for the next upcoming event matching the person's name in the subject or attendees.
   - Capture: subject, start time, end time, location, format (Teams/in-person/phone).

4. **Confirm meeting details.** Store in working memory:
   ```
   meeting_details:
     person: {Full Name}
     date: YYYY-MM-DD
     day_of_week: {Monday-Friday}
     time: HH:MM
     duration: {minutes}
     location: {Teams / in-person / phone}
     meeting_name: {calendar event subject}
     known_cadence: true/false
   ```

5. **Check for previous prep brief** in the knowledge base working directory.
   - Search for the most recent file matching `{Person Name} - *.md`
   - If found, note the date and file path. This will be critical input for steps 02-04.
   - If none exists, note this is the first prep brief for this person.

---

## SUCCESS METRICS

- Person name confirmed
- Meeting date, time, and location captured
- Previous brief located (or confirmed as first-time)
- Known cadence status identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Ask the controller for date/time directly. If provided, proceed. If not, use next known cadence day. |
| No 1:1 found on calendar | Inform controller: "No 1:1 with {Person} found on the calendar. I'll build the brief anyway — you can use it for your next touchpoint." Proceed with today's date. |
| Person not recognized | Ask the controller to confirm the full name and their relationship (direct report, peer, leader). |

---

## NEXT STEP

Read fully and follow: `step-02-gather-communications.md`

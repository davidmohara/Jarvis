---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Identify the Meeting

## MANDATORY EXECUTION RULES

1. You MUST confirm the external attendee(s) and/or company before proceeding. No prep sheet without a name.
2. You MUST have a meeting date and time. If not provided, search the calendar via the connected email/calendar tool.
3. You MUST verify the meeting's local time and timezone against the Mac's actual local time before recording it anywhere. Never trust a raw calendar timestamp at face value.
4. You MUST record whether location/format (Teams link, phone, in-person, address) is present on the invite. If missing, this is an open question to carry into the final prep sheet — not something to guess.
5. You MUST record whether this is a first-time meeting with this person or there is prior 1:1 history (check knowledge layer / prior prep docs).
6. Do NOT proceed to step 02 until you have: attendee name(s), company (if known), date, time (verified), duration, and a location/format status (confirmed or flagged as missing).

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Controller request (name/company, optionally date/time), calendar access, knowledge layer
**Output:** Confirmed meeting logistics stored in accumulated-context for all subsequent steps

---

## CONTEXT BOUNDARIES

- This step gathers logistics only. Do NOT research why the meeting exists here — that is step 02's job, and it must be sourced from email, not guessed at this stage.
- Do NOT research the company or attendee's background here — that is step 03's job, and it happens after classification.
- If the controller names a person but there is no meeting on the calendar, note that and proceed anyway — the prep sheet is still useful for an upcoming or informally-scheduled conversation.

---

## YOUR TASK

### Sequence

1. **Parse the request.** Extract attendee name(s) and company (if given). If a date/time was provided, capture it as a starting point — it still requires verification in step 3 below.

2. **Search the calendar** via the connected email/calendar tool (per SYSTEM.md connector resolution — the active Superhuman-style connector's `query_email_and_calendar`, or M365 MCP `outlook_calendar_search` when authorized) if date/time is not already confirmed.
   - Search by attendee name, by company/organization, AND by date range if the first two return nothing — do not give up after one query shape.
   - Capture: subject, start time (as returned, likely UTC or ISO with offset), end time, location field, format (Teams/phone/in-person), organizer, full attendee list.

3. **Verify local time and timezone.** This step is non-negotiable — timezone mismatches are a documented recurring failure mode in this system.
   - Run `osascript -e 'tell application "System Events" to get time string of (current date)'` (or equivalent `date` command) via Desktop Commander or Control_your_Mac to get the Mac's actual current local time and timezone.
   - Convert the calendar's returned meeting time to that local timezone. Show your conversion math if there's any ambiguity (e.g., "14:00 UTC → 9:00 AM CDT").
   - Sanity-check the conversion: does the resulting local time make sense given the day and context? A meeting that "starts at 11 PM" for a same-day business call is a red flag — recheck the offset.
   - Only record the meeting time in the format: `HH:MM–HH:MM [Timezone abbreviation] (verified against Mac local time)`.

4. **Check location/format completeness.** If the invite has no Teams link, no phone number, and no physical address — record this explicitly as a gap. Do not assume a default format (e.g., do not assume "probably Teams" — state it's unconfirmed).

5. **Check relationship history.** Search the knowledge layer / Obsidian vault / prior prep docs for this person's name and/or company.
   - If a prior 1:1 history or prior prep sheet exists, note it and its date — this changes the calibration in later steps (an ongoing relationship reads differently than a first-time contact).
   - If nothing is found, record this explicitly as "new contact — no prior 1:1 history."

6. **Store in accumulated-context:**
   ```yaml
   meeting_details:
     attendees_external:
       - name: {Full Name}
         company: {Company or "unknown — confirm in step 02/03"}
     meeting_date: YYYY-MM-DD
     meeting_time_verified: "HH:MM–HH:MM {TZ} CDT/CST/etc — verified against Mac local time"
     duration_minutes: {N}
     format_confirmed: true/false
     format_notes: "{Teams link present / phone number present / not on invite — confirm before the call}"
     organizer: {email}
     prior_relationship: "new contact — no prior 1:1 history" | "ongoing — last met {date}, see {prior prep doc path}"
   ```

---

## SUCCESS METRICS

- Attendee name(s) and company (if known) confirmed
- Meeting date and time captured AND verified against Mac local time — no unverified timestamps carried forward
- Location/format status recorded as confirmed or explicitly flagged as missing
- Prior relationship status determined (new vs. ongoing)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable or connector not authorized | Ask the controller for date/time/attendees directly. If provided, proceed with local-time verification still mandatory. |
| No meeting found on calendar | Inform controller: "No meeting with {name} found on the calendar. I'll build the prep sheet from what you give me — confirm date/time so I can verify the timezone." |
| Timezone conversion is ambiguous or the calendar entry has no timezone marker | Do not guess. State the ambiguity explicitly in the prep sheet's Open Questions section rather than picking one silently. |
| Location/format genuinely absent from the invite | Do not invent one (no assuming "Teams" by default). Carry forward as an open question. |

---

## NEXT STEP

Read fully and follow: `step-02-source-of-truth-email.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

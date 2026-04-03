---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Gather Calendar

## MANDATORY EXECUTION RULES

1. You MUST pull today's full calendar before proceeding. No briefing without calendar data.
2. You MUST identify meeting type for each event (client, internal 1:1, team, external, personal).
3. You MUST flag back-to-back meetings with zero buffer.
4. Do NOT skip cancelled or tentative meetings — note them separately.
5. Do NOT proceed to step 02 until calendar data is captured and categorized.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** M365 calendar access, today's date
**Output:** Structured calendar data stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Pull today's calendar only. Do not look ahead to tomorrow unless today is empty.
- Include all events regardless of status (accepted, tentative, cancelled).
- Attendee names are required. Attendee count is required for meetings with 5+.

---

## YOUR TASK

### Sequence

1. **Pull today's calendar** via M365 MCP (`outlook_calendar_search`).
   - Query: all events for today
   - Capture: subject, start time, end time, location, attendees, response status

2. **Classify each meeting** by type:
   - `client` — external client or prospect meeting
   - `1:1` — internal one-on-one with a direct report, peer, or leader
   - `team` — internal group meeting (sales, ops, all-hands)
   - `partner` — external partner meeting (Microsoft, Confluent, etc.)
   - `external` — networking, conference, community
   - `personal` — blocked time, focus, personal appointment
   - `recurring-skip` — standing meetings that don't need prep (all-hands, recurring standups, etc.)

3. **Flag meetings that need attention:**
   - Client meetings → will need Chase for prep context
   - 1:1s with direct reports → will need Shep for prep context
   - Partner meetings → will need account overlap data
   - Back-to-back blocks with no buffer
   - Meetings starting in < 60 minutes with no prior prep

4. **Note scheduling patterns:**
   - Total meeting count
   - Total hours in meetings vs. open time
   - Any video call clusters (3+ video calls = flag per controller preferences)

5. **Store results** in working memory as structured data:
   ```
   calendar_data:
     date: YYYY-MM-DD
     meeting_count: N
     meetings:
       - time: HH:MM - HH:MM
         subject: ...
         type: client | 1:1 | team | partner | external | personal
         attendees: [...]
         location: ...
         needs_prep: true/false
         flags: [...]
     open_blocks: [HH:MM - HH:MM, ...]
     warnings: [...]
   ```

---

## SUCCESS METRICS

- All meetings for today captured with times and attendees
- Each meeting classified by type
- Prep-needed meetings identified
- Back-to-back and overload warnings flagged

## FAILURE MODES

| Failure | Action |
|---------|--------|
| M365 calendar unavailable | Report: "Calendar data unavailable. Proceeding with tasks and delegations only." Skip to step 02. |
| No meetings today | Note "Clear calendar" and proceed. This is a win, not an error. |
| Partial data (missing attendees) | Flag the meeting as "attendee data incomplete" and proceed. |

---

## NEXT STEP

Read fully and follow: `step-02-gather-tasks.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

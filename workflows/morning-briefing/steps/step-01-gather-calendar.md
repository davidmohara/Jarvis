---
status: complete
started-at: "2026-08-27T16:28:00Z"
completed-at: "2026-08-27T16:30:00Z"
outputs:
  date: "2026-08-27"
  meeting_count: 9
  summary: "Board retreat day (Lone Star Gold, Malakoff TX, lake house) overlapping 5 internal calls David is still booked into (Sales Scrum, Town Hall, Bday reveal event, 1:1 w/ Scott McMichael). DEXA scan 8:45am. Flag: heavy double-booking risk against the retreat block."
model: sonnet
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
**Input:** Unified calendar data from `data/calendar-unified.json` (pulled by boot step-01.5)
**Output:** Structured calendar data for today, stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Read today's events from the unified calendar file (already pulled in boot step-01.5).
- Do NOT call M365 directly — reuse the cached data.
- Include all events regardless of status (accepted, tentative, cancelled).
- Attendee names are required. Attendee count is required for meetings with 5+.

---

## YOUR TASK

### Sequence

1. **Load today's calendar from disk** via `data/calendar-unified.json`.
   - Parse: JSON file with 4-day calendar data
   - Filter: Extract events where date == today
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


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py morning-briefing step-01-gather-calendar complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-02-gather-tasks.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

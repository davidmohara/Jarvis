---
status: complete
started-at: '2026-10-09T15:49:14Z'
completed-at: '2026-10-09T15:52:00Z'
outputs:
  calendar_file: data/calendar-unified.json
  event_count: 18
  date_range: 2026-10-09 to 2026-10-12
  status: written
  m365_calls: 1
  highlights: Libby's Birthday all-day today; today 6 events incl 2nd Friday Executive Meeting 9:30am CT and Friday Week Wrap-Up 2:30pm CT; Sat Rimmer Wedding 6pm; Mon DLP Bootcamp (remote) all-day with Agent Strategy and GEHC check-in overlapping
---

<!-- system:start -->
# Step 01.5: Unified Calendar Pull (Before Phase 2)

## MANDATORY EXECUTION RULES

1. You MUST pull calendar data ONCE and write it to disk — no repeated calls.
2. You MUST pull 4 days (today + next 3) in a single M365 call to minimize API overhead.
3. You MUST write the raw response to disk for all downstream steps to consume.
4. Do NOT parse or filter yet — that happens in consuming steps.
5. You MUST NOT proceed to phase-02 until the file is written and verified.

---

## EXECUTION PROTOCOL

**Agent:** boot subagent (Master persona), spawned by the coordinator at boot start, never executed inline in the coordinator's session (see `workflow.md`).
**Input:** M365 MCP access, today's date + next 3 days
**Output:** Raw calendar response written to `data/calendar-unified.json`

---

## CONTEXT BOUNDARIES

- This step is "pull once, share many" — all calendar needs go to this data file.
- Morning briefing step-01 will read from this file instead of calling M365.
- Boot step-02 Task G (72-hour look-ahead) will read from this file.
- Morning briefing step-03 (meeting prep) will read from this file.
- One API call. One file. Multiple consumers.

---

## YOUR TASK

1. **Check if calendar file exists and is fresh:**
   ```
   File: data/calendar-unified.json
   If exists AND created within last 12 hours: reuse it (skip to step 2)
   If missing OR stale: proceed to pull
   ```

2. **Pull calendar via M365 MCP** (`outlook_calendar_search`):
   ```
   Query: all events from [today] to [today + 3 days]
   Date range: Today 00:00 to Day+3 23:59
   Return: Full event objects (subject, start, end, attendees, location, status, etc.)
   ```

3. **Write raw response to disk:**
   ```
   File: data/calendar-unified.json
   
   {
     "pulled_at": "ISO-8601 timestamp",
     "date_range": {
       "start": "YYYY-MM-DD",
       "end": "YYYY-MM-DD"
     },
     "event_count": N,
     "events": [
       { full event objects from M365 }
     ]
   }
   ```

4. **Verify file was written:**
   - Check file exists
   - Check size > 100 bytes (not empty)
   - Check valid JSON

5. **Log to outputs:**
   ```yaml
   outputs:
     calendar_file: "data/calendar-unified.json"
     event_count: N
     date_range: "YYYY-MM-DD to YYYY-MM-DD"
     file_size_kb: N
     status: "written"
   ```

6. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

7. **Update state.yaml:** Set `current-step: step-02-gather-data.md`.

---

## SUCCESS METRICS

- Single M365 calendar API call made (not multiple)
- Raw response written to data/calendar-unified.json
- File contains all events for 4-day window
- All downstream steps will read from this file (no additional calls)
- Estimated context savings: 70-80% by eliminating duplicate API responses

## FAILURE MODES

| Failure | Action |
|---------|--------|
| M365 calendar unavailable | Record: "Calendar pull failed — M365 unavailable". Write empty file `{"events": []}`. Continue. |
| File write fails | Log error. Continue. Steps will handle missing file gracefully. |
| Partial data returned | Write what was returned. Steps will process it. |

---

## NEXT STEP

Read fully and follow: `step-02-gather-data.md`

Note: All consolidated data files (calendar, email, tasks, reminders, inbox) are now available on disk for consuming steps to read from.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

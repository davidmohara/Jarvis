---
status: complete
started-at: '2026-11-02T16:08:13Z'
completed-at: '2026-11-02T16:10:36Z'
---

<!-- system:start -->
# Step 01.5: Unified Calendar Pull (Before Phase 2)

## MANDATORY EXECUTION RULES

1. You MUST pull calendar data ONCE and write it to disk — no repeated calls.
2. You MUST pull 4 days (today + next 3) in a single M365 call to minimize API overhead.
3. You MUST write the raw response to disk for all downstream steps to consume.
4. Do NOT parse or filter yet — that happens in consuming steps.
5. When the file is written and verified, your mandate is DONE. Exit and return to the coordinator. Do NOT read, follow, or execute any other step file: this step is one bounded pull, and walking the broader workflow from here multiplies cost with no added output.

---

## EXECUTION PROTOCOL

**Agent:** dedicated calendar subagent, spawned by the coordinator (Master) with a tight single-purpose brief. This step is a plain data pull: it never loads the master persona (`agents/master.md`) or `SYSTEM.md`, never runs STATE CHECK, and never walks other steps.
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
   If exists AND pulled_at within last 12 hours: reuse it (skip to step 4)
   If missing OR stale: proceed to pull
   ```

2. **Pull calendar via M365 MCP** (`outlook_calendar_search`) — this is the ONLY calendar call you make:
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

5. **Log to `state.yaml` `accumulated-context`** (use the Edit tool, never Bash):
   ```yaml
   # state.yaml -> accumulated-context
   calendar_file: "data/calendar-unified.json"
   event_count: N
   date_range: "YYYY-MM-DD to YYYY-MM-DD"
   file_size_kb: N
   status: "written"
   ```

6. **Update step frontmatter:** Set `status: complete` and `completed-at` to the real UTC clock time from `date -u +%Y-%m-%dT%H:%M:%SZ` (paste the exact output; never estimate or round) — Edit tool.

7. **Set `current-step: step-01.2-unified-data-pull.md`** in state.yaml — the coordinator dispatches the main boot subagent for steps 01.2 through 08 next.

---

## TOOL DISCIPLINE

- M365 MCP is the only authorized calendar source. Never substitute AppleScript or Outlook, and never declare the calendar unavailable without first attempting the connector.
- If the M365 connector is unreachable (ToolSearch returns no calendar tool after one retry), report that failure explicitly in your final message and write the empty-file fallback per Failure Modes. A silent "calendar unavailable" is the recorded failure mode, not an acceptable shortcut.
- Use the file tools (Read/Edit/Write) for the output file, the state.yaml update, and the step frontmatter update — never Bash redirection or heredocs. The eval harness's per-step attribution keys on Edit/Write tool calls; a Bash-written state update is invisible to it, which silently loses the run's per-step records.

## SUCCESS METRICS

- Single M365 calendar API call made (not multiple)
- Raw response written to data/calendar-unified.json
- File contains all events for 4-day window
- Subagent exited immediately after the file was verified — zero other step files read
- All downstream steps will read from this file (no additional calls)
- Estimated context savings: 70-80% by eliminating duplicate API responses

## FAILURE MODES

| Failure | Action |
|---------|--------|
| M365 calendar unavailable | Record: "Calendar pull failed — M365 unavailable". Write empty file `{"events": []}`. Report the failure in your final message. Continue to exit. |
| File write fails | Log error. Report in final message. Steps will handle missing file gracefully. |
| Partial data returned | Write what was returned. Steps will process it. |

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read `step-02-gather-data.md` or any other step file — the coordinator spawns the main boot subagent for steps 01.2 through 08 after you return. Your final message is a short status report: reused-or-pulled, event_count, date_range, and any failure. Then stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

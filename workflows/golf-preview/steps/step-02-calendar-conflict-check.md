---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 02: Calendar Conflict Check

## MANDATORY EXECUTION RULES

1. Treat calendar conflicts as hard blocks. Treat weather as a soft block (handled in step-03).
2. **⚠️ UTC→CT conversion is mandatory and applies everywhere.** Never compare raw UTC event
   times against CT window boundaries.
3. Do not proceed to step-03 until **QUALITY GATE 2** below is logged, even if it only logs a
   pass.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** `target_friday`, `target_saturday`, `target_sunday` from step-01's output
**Output:** Per-day availability status + CT time windows, stored in `accumulated-context`

---

## YOUR TASK

### Pull Calendar

```
mcp__b8c41a14__outlook_calendar_search
query: ""
start_datetime: [target_friday]T00:00:00
end_datetime: [target_sunday]T23:59:59
```

### Convert UTC → CT

All event times returned by the calendar API are in UTC. David is in CT (CDT = UTC-5 in
summer, CST = UTC-6 in winter). Convert every `start` and `end` timestamp to CT before:
- Assigning an event to a calendar day
- Calculating when a busy block starts and ends
- Identifying free windows between events
- Checking whether a 3-hour gap exists within a target time range

**Conversion rule:** Subtract 5 hours from UTC timestamps (CDT, roughly April–October). If the
resulting time crosses midnight backward, the event belongs to the previous calendar day.

Example: `2026-05-22T23:30:00.000Z` → subtract 5h → 6:30 PM CT on May 22 (not May 23).

**Build a CT timeline for each day before analysis.** For each of Friday, Saturday, and Sunday:
1. Collect all events whose CT start or end falls within that calendar day (midnight–11:59 PM CT)
2. Sort by CT start time
3. Map out busy blocks as CT time ranges: e.g., `[13:00–14:30, 16:00–17:00]`
4. Identify free gaps between busy blocks within the target golf window (see per-day rules below)

### Per-Day Rules

**Hard blocks (mark day as unavailable regardless of timing):**
- Travel / flights / out of town
- Evening dinners with family (parents dinner etc.) — check Saturday and Sunday
- All-day events

**Sunday-specific rules:**
- Church volunteering blocks 8:30 AM – 1:30 PM CT every Sunday. Hard-coded — no golf before
  2:30 PM CT on Sundays.
- If Sunday has a dinner with parents on the calendar → prefer Saturday that week. If Saturday
  also has an event, Sunday is still viable after 2:30 PM CT.

**Friday-specific rules:**
- Susie works from home Fridays — her schedule mirrors David's calendar.
- Using the CT timeline built above, check for a continuous 3-hour free gap between 1:00 PM
  and 6:00 PM CT. If no such gap exists, mark Friday unavailable.
- If a clear 3-hour window exists, Friday is viable. Record the exact window start and end.

**Saturday rules:**
- No standing constraints. Identify the earliest available start at or after 1:00 PM CT with
  at least 4.5 hours free before any hard block or end of day (6:30 PM CT latest start for 18
  holes).

**Already booked:**
- Search calendar for any existing golf block on the target weekend. If found, mark that day
  unavailable.

Store per-day status: `available` | `unavailable` | `conditional`. Store reason for any
unavailable day. Store the available CT window (earliest_start, latest_start) for each
available day.

---

## QUALITY GATE 2 — CT Timeline Integrity (SOFT, LOGGED)

This gate does not block the workflow — it exists to catch the specific failure mode this
step was designed against: analyzing raw UTC times as if they were CT, which silently shifts
every window by 5-6 hours and can misclassify a hard-blocked evening as a free afternoon.

Self-check before moving to step-03:

| Check | How to verify | If it fails |
|-------|---------------|-------------|
| Every event used in day-status reasoning has a CT-converted timestamp, not raw UTC | Spot-check the busy-block ranges you recorded — do they look like plausible CT daytime hours, or do they look shifted (e.g., a "dinner" busy block starting at 1am)? | Re-run the conversion, log `[Gate 2] CT conversion re-run — suspected UTC leak`, and flag `ct_conversion_flag: true` in output |
| All three days have a recorded status (`available`/`unavailable`/`conditional`) | Check your own notes | Fill in the missing day before proceeding — do not leave a day unassessed |
| Already-booked check was run against the full target weekend, not just the day being scored | Confirm the search covered target_friday through target_sunday | Re-run the already-booked search |

Log the result:
```
[Gate 2] Friday: [status] — [reason if unavailable]
[Gate 2] Saturday: [status] — [reason if unavailable]
[Gate 2] Sunday: [status] — [reason if unavailable]
[Gate 2] CT conversion integrity: confirmed | flagged
```

If `ct_conversion_flag: true`, carry that flag into `preview-output.json` in step-04 and
mention it in the Slack summary in step-05 — this soft gate's job is to make sure a suspected
timezone bug is visible to David, not to silently self-correct and hide it.

Update `state.yaml`'s `accumulated-context` with day-status and CT windows. Set
`current-step: step-03`.

---

## SUCCESS METRICS

- All three days have a recorded status with a documented reason for any unavailable day
- No raw UTC comparison anywhere in the reasoning trail

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Proceed with weather only in step-03. Flag in Slack (step-05): "⚠️ Calendar unavailable — verify no conflicts." Record `calendar_unavailable: true`. |
| CT conversion looks suspect (Gate 2 flags it) | Re-run conversion once. If still suspect, proceed but flag prominently in output and Slack — do not block the workflow on a soft gate. |

## NEXT STEP

Read fully and follow: `step-03-drought-and-weather.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

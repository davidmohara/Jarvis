---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Create and Verify Calendar Block

## MANDATORY EXECUTION RULES

1. **CALENDAR EVENT CREATION MUST BE VERIFIED.** After executing the AppleScript to create a
   calendar event on the Family calendar, ALWAYS verify the event actually exists before
   proceeding. If verification fails, invoke the fallback protocol immediately — send Slack
   notification to David with manual add instructions. Do NOT proceed to step-07 assuming the
   calendar event was created if verification fails.
2. Only execute this step after step-05 (Gate 4) confirms the booking is visible on the
   Bookings page.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Confirmed, visually-verified booking from step-05
**Output:** Calendar event on the Family calendar (or a documented fallback) —
**QUALITY GATE 5**

---

## YOUR TASK

### 6a — Create Event via AppleScript

Do NOT use Outlook or the MS365 MCP — they do not support event creation.

```applescript
tell application "Calendar"
  tell calendar "Family"
    set startDate to date "[booked_date_words] [booked_time - 30min]"
    set endDate to date "[booked_date_words] [booked_time + 4.5hrs for 18 holes | + 2.5hrs for 9 holes]"
    set newEvent to make new event with properties {summary:"⛳ Golf — Frisco Lakes", start date:startDate, end date:endDate, location:"Frisco Lakes Golf Club, 7170 Anthem Drive, Frisco TX 75034", description:"Tee time: [booked_time] · [booked_holes] holes · $[booked_cost] due at course · 2 players (David + Susie O'Hara) · Booking #[booking_number] · Arrive by [booked_time - 30min] for range warm-up."}
  end tell
end tell
```

Run via `mcp__Desktop_Commander__start_process` with `osascript << 'EOF' ... EOF`.

**Range time:** Calendar block starts 30 minutes BEFORE the tee time to cover warm-up.

---

## QUALITY GATE 5 — Calendar Event Verification (SOFT, FALLBACK-NOTIFIED)

### 6b — Verify

```applescript
tell application "Calendar"
  tell calendar "Family"
    set eventCount to count of events
    set lastEvent to the last event
    set lastEventSummary to summary of lastEvent
    set lastEventDate to start date of lastEvent
    if lastEventSummary contains "⛳" and lastEventSummary contains "Frisco Lakes" then
      "calendar-event-verified"
    else
      "calendar-event-not-found"
    end if
  end tell
end tell
```

Run this immediately after 6a.

**If `"calendar-event-verified"`:** Log `[Gate 5] PASS`. Proceed to step-07.

**If `"calendar-event-not-found"` OR AppleScript execution errors/times out:** Proceed to 6c.
Do NOT assume success on an AppleScript timeout — that is not the same as a confirmed pass.

### 6c — Fallback

This is a soft gate: the booking itself is already confirmed (Gate 4 passed), so a calendar
failure does not undo that. But it must never be silently swallowed.

1. Log the failure — record the osascript error details.
2. Send Slack notification to David:
   ```
   *⛳ Golf Booking Confirmed — Calendar Event Failed*

   Booking #[booking_number] confirmed on ChronoGolf
   But calendar event creation failed (AppleScript or Family calendar not available)

   Please add manually:
   📅 [Day, Month D] at [booked_time - 30min]–[end_time]
   📍 Frisco Lakes Golf Club, 7170 Anthem Drive, Frisco TX 75034
   🏌️ Tee time: [booked_time] · [booked_holes] holes · $[booked_cost]
   👥 David + Susie O'Hara · Booking #[booking_number]
   ```
3. Continue to step-07 — booking is still confirmed; just missing the calendar block.
4. Note in `state.yaml`'s `accumulated-context`: `calendar_event_failed: true`.

---

## SUCCESS METRICS

- Either Gate 5 passes with a verified calendar event, or the fallback notification was sent
  and `calendar_event_failed: true` is recorded — never a silent gap

## FAILURE MODES

| Failure | Action |
|---------|--------|
| AppleScript osascript timeout | Do NOT assume success. Proceed immediately to the 6b verification query. If verification still fails, invoke 6c fallback. |
| Family calendar not available | Log error. Invoke 6c fallback. Do not try Outlook/MS365 — they do not support event creation. |

## NEXT STEP

Read fully and follow: `step-07-slack-confirmation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

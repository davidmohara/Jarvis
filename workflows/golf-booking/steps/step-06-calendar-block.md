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

1. **CALENDAR EVENT CREATION MUST BE VERIFIED.** This step now goes through the
   `calendar-handler` skill's `event-create` operation, which creates the event and verifies
   it before returning. If the skill reports the event as unverified or failed, invoke the
   fallback protocol immediately — send Slack notification to David with manual add
   instructions. Do NOT proceed to step-07 assuming the calendar event was created if
   verification failed.
2. Only execute this step after step-05 (Gate 4) confirms the booking is visible on the
   Bookings page.
3. This step uses `calendar_backend: Calendar.app` (AppleScript against macOS Calendar.app),
   not M365. As of 2026-09-02, live testing showed
   `mcp__claude_ai_Microsoft_365__outlook_create_event` returns a `permission_error` ("This
   tool is not available") in this environment, so the M365 write path in `calendar-handler` is
   currently unverified here. Do not switch this step's `calendar_backend` to `M365` without
   re-testing that the create tool is actually reachable first.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Confirmed, visually-verified booking from step-05
**Output:** Calendar event on the Family calendar (or a documented fallback) —
**QUALITY GATE 5**

---

## YOUR TASK

### 6a — Create Event via calendar-handler

Call `skills/calendar-handler/SKILL.md`:

```yaml
operation: event-create
calendar_backend: Calendar.app   # explicit — known-working AppleScript path against macOS
                                 # Calendar.app. The M365 write path exists in calendar-handler
                                 # for future use, but as of 2026-09-02 the M365 create tool
                                 # (mcp__claude_ai_Microsoft_365__outlook_create_event) returned
                                 # a permission_error ("This tool is not available") in testing,
                                 # so this step stays on Calendar.app until that's resolved.
calendar_name: "Family"
title: "⛳ Golf — Frisco Lakes"
time:
  start: "[booked_date_words] [booked_time - 30min]"
  end: "[booked_date_words] [booked_time + 4.5hrs for 18 holes | + 2.5hrs for 9 holes]"
participants: ["David O'Hara", "Susie O'Hara"]
description: >
  Tee time: [booked_time] · [booked_holes] holes · $[booked_cost] due at course ·
  2 players (David + Susie O'Hara) · Booking #[booking_number] · Arrive by
  [booked_time - 30min] for range warm-up.
```

Location (`Frisco Lakes Golf Club, 7170 Anthem Drive, Frisco TX 75034`) is fixed for this
workflow — pass it as part of `description`/`time` context if the skill's `event-create` input
doesn't carry a separate `location` field by the time this runs, so it isn't dropped from the
calendar entry.

**Range time:** Calendar block starts 30 minutes BEFORE the tee time to cover warm-up — this is
encoded in the `time.start` value above, not left to the skill to infer.

With `calendar_backend: Calendar.app`, the skill creates the event via AppleScript against
macOS Calendar.app and re-queries that calendar to verify it before returning `confirmation`.
This path does not send M365 invites to `participants` — they're folded into the description
text only (see calendar-handler's `event-create` process notes). If M365 write access is
confirmed working later, switch this step to `calendar_backend: M365` to get real Outlook
invites and re-test before changing the default.

---

## QUALITY GATE 5 — Calendar Event Verification (SOFT, FALLBACK-NOTIFIED)

### 6b — Check the skill's result

**If `confirmation: "created-and-verified"`:** Log `[Gate 5] PASS`. Proceed to step-07.

**If `confirmation: "created-unverified"` or `"failed"`:** Proceed to 6c. Do NOT assume success
on an AppleScript timeout inside the skill — that is not the same as a confirmed pass, and the
skill itself does not treat it as one (`fallback_notified` will be `true` if the skill already
attempted its own fallback notice — see 6c).

### 6c — Fallback

This is a soft gate: the booking itself is already confirmed (Gate 4 passed), so a calendar
failure does not undo that. But it must never be silently swallowed.

1. Log the failure — record the error detail the skill returned.
2. If the skill's `fallback_notified` came back `false` (it expects the caller to supply and
   run the fallback path — see calendar-handler's error handling table), send Slack
   notification to David directly:
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
   If `fallback_notified` is already `true`, confirm the notice went out rather than sending a
   duplicate.
3. Continue to step-07 — booking is still confirmed; just missing the calendar block.
4. Note in `state.yaml`'s `accumulated-context`: `calendar_event_failed: true`.

---

## SUCCESS METRICS

- Either Gate 5 passes with `confirmation: "created-and-verified"` from `calendar-handler`, or
  the fallback notification was sent and `calendar_event_failed: true` is recorded — never a
  silent gap

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `calendar-handler` returns `confirmation: "created-unverified"` or times out internally | Do NOT assume success. Treat as 6b failure and proceed to 6c fallback. |
| `calendar-handler` returns `confirmation: "failed"` (e.g. Family calendar not available in Calendar.app) | Log error. Invoke 6c fallback. Do not silently retry with `calendar_backend: M365` mid-run without a human decision — M365 create is currently unverified in this environment (see MANDATORY EXECUTION RULES note above) and a backend switch changes where the event lands and whether invites go out, so treat it as a deliberate choice, not an automatic retry. |

## NEXT STEP

Read fully and follow: `step-07-slack-confirmation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

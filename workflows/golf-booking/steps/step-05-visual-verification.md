---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Mandatory Visual Verification on Bookings Page

## MANDATORY EXECUTION RULES

1. **This step is non-negotiable.** Do not claim success until you navigate to the Bookings
   page and visually confirm the booking is listed. Confirmation page appearance (Gate 3) is
   not enough — the booking must be visible in the Bookings list.
2. If verification fails, abort and send a critical alert to David. Do not proceed to
   step-06 or step-07.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** `BOOKING-SUCCESS` result from step-04 (Gate 3)
**Output:** Independently confirmed booking on the Bookings page — this is **QUALITY GATE 4**

---

## YOUR TASK

Navigate to the Bookings page:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
window.location.href = \"https://www.chronogolf.com/dashboard/#/bookings\";
\"navigating-to-bookings\"
"'
```

Wait 3 seconds for the page to load.

**Visually inspect the Bookings list** on screen. Look for:
- The booked date (e.g., "Saturday, June 13")
- The booked time (e.g., "1:00 PM")
- Frisco Lakes Golf Club listed
- 2 players shown (David + Susie O'Hara)

Read the DOM to confirm the booking is present:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var hasBooking = body.includes(\"Frisco Lakes\") && (body.includes(\"[booked_date]\") || body.includes(\"[booked_month]\"));
hasBooking ? \"BOOKING-VISIBLE-ON-PAGE\" : \"BOOKING-NOT-FOUND-ON-PAGE: \" + body.substring(0,500).replace(/\\n+/g,\" | \")
"'
```

(Substitute `[booked_date]` / `[booked_month]` with the actual values captured in step-04.)

---

## QUALITY GATE 4 — Visual Verification (HARD, BLOCKING, CRITICAL ESCALATION)

**If result is `BOOKING-VISIBLE-ON-PAGE`:**
→ Log `[Gate 4] PASS`. Booking confirmed. Proceed to step-06.

**If result is `BOOKING-NOT-FOUND-ON-PAGE`:**
→ **CRITICAL FAILURE.** The booking confirmation page appeared (Gate 3 passed), but the
booking is NOT in the Bookings list. This indicates a UI state inconsistency, a session/network
issue, or a ChronoGolf platform error.

**Action:** Send Slack alert to David immediately:
```
*⛳ BOOKING VERIFICATION FAILED*

Confirmation screen appeared and was accepted, but the booking does NOT appear in your Bookings list on ChronoGolf.

Date/Time attempted: [booked_date] at [booked_time]
Course: Frisco Lakes Golf Club
Players: David + Susie O'Hara

This may be a platform error. Please:
1. Refresh your Bookings page manually
2. Contact ChronoGolf support if the booking is still missing
3. Check your email for a confirmation receipt

Do NOT assume the booking succeeded.
```

Abort. Do not proceed to step-06 or step-07. Set `state.yaml` `status: verification-failed`.
This is why Gate 3 and Gate 4 are separate gates rather than one: ChronoGolf's own UI can lie
at the confirmation step, and only a second, independent check on the Bookings page catches
that.

---

## SUCCESS METRICS

- Gate 4 passes with an explicit `BOOKING-VISIBLE-ON-PAGE` result — never inferred from Gate 3
  alone

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `BOOKING-NOT-FOUND-ON-PAGE` | Critical Slack alert (above). Abort. `status: verification-failed`. Do not send a success notification anywhere else in the workflow. |

## NEXT STEP

Read fully and follow: `step-06-calendar-block.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

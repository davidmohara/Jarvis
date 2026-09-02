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
   page and get an explicit, recorded approval or escalation decision through the
   `visual-verification` skill. Confirmation page appearance (Gate 3) is not enough — the
   booking must be visible in the Bookings list AND that visibility must go through the
   skill's HARD gate, not an inline "looks fine" judgment.
2. If verification fails or is escalated, abort and send a critical alert to David. Do not
   proceed to step-06 or step-07.

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

Capture a screenshot of the Bookings list (Peekaboo skill or
`mcp__Control_your_Mac__osascript`) and also read the DOM as a machine-checkable cross-signal
before handing off to the verification skill:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var hasBooking = body.includes(\"Frisco Lakes\") && (body.includes(\"[booked_date]\") || body.includes(\"[booked_month]\"));
hasBooking ? \"BOOKING-VISIBLE-ON-PAGE\" : \"BOOKING-NOT-FOUND-ON-PAGE: \" + body.substring(0,500).replace(/\\n+/g,\" | \")
"'
```

(Substitute `[booked_date]` / `[booked_month]` with the actual values captured in step-04.)

### Call the visual-verification skill

This is the HARD gate. Call `skills/visual-verification/SKILL.md` with:

```yaml
screenshot_path: "{{path to the Bookings-page screenshot just captured}}"
reference_context: >
  Confirm this booking matches: {{booked_date}} at {{booked_time}}, Frisco Lakes Golf Club,
  2 players (David + Susie O'Hara). DOM cross-check returned: {{BOOKING-VISIBLE-ON-PAGE or
  BOOKING-NOT-FOUND-ON-PAGE result from above}}.
escalation_option: |
  Send the "BOOKING VERIFICATION FAILED" Slack alert below via master-slack, then abort —
  do not proceed to step-06 or step-07.
caller: "golf-booking / step-05-visual-verification"
```

Do not substitute your own visual read of the screenshot for the skill's approval/escalation
decision — the DOM check above is a supporting signal you feed into `reference_context`, not a
replacement for running the skill.

---

## QUALITY GATE 4 — Visual Verification (HARD, BLOCKING, CRITICAL ESCALATION)

**If the skill returns `approval: true`:**
→ Log `[Gate 4] PASS`. Booking confirmed. Proceed to step-06.

**If the skill returns `approval: false`:**
→ **CRITICAL FAILURE.** Either the DOM cross-check came back `BOOKING-NOT-FOUND-ON-PAGE`, or
the human reviewer rejected the screenshot, or no one was available to answer and the skill
escalated by default (it never silently approves on a timeout). This indicates a UI state
inconsistency, a session/network issue, or a ChronoGolf platform error.

**Action:** The skill's `escalation_option` already ran the Slack alert below as part of its
own process — confirm it went out, then treat this as a hard stop regardless. Do not send a
second, different alert; if for some reason the skill's escalation path didn't fire (e.g. the
skill itself failed rather than returning a decision), send it directly:
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
at the confirmation step, and only a second, independent check — now enforced as a HARD gate
by the `visual-verification` skill rather than an inline DOM check alone — catches that.

---

## SUCCESS METRICS

- Gate 4 passes with an explicit `approval: true` decision from `visual-verification` — never
  inferred from Gate 3 or the DOM check alone

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `visual-verification` returns `approval: false` (rejected or escalated) | Critical Slack alert (above, or confirm the skill's own escalation already sent it). Abort. `status: verification-failed`. Do not send a success notification anywhere else in the workflow. |

## NEXT STEP

Read fully and follow: `step-06-calendar-block.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- system:start -->
# Step 03: Open Booking Widget, Select Date/Course/Holes/Players

## MANDATORY EXECUTION RULES

1. **Always book 2 players (David + Susie O'Hara)**, both as "41 - Frisco Lakes Total Member",
   unless `preview-output.json` explicitly specifies a different party size via a `party_size`
   field.
2. **Always book 18 holes** on Frisco Lakes Golf Club unless falling back due to drought/late
   time.
3. Before clicking any date cell, confirm this is the exact date validated by Gate 1 in
   step-01. If the calendar UI shows this date as unselectable, disabled, or throws an
   "out of your booking range" error, do NOT click a different date. Treat this as a failure
   (see FAILURE MODES) — never fall back to the nearest bookable date.

---

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline
**Input:** Authenticated session from step-02, validated date/time from step-01
**Output:** Booking widget open on the tee-time selection screen with players selected

---

## YOUR TASK

### Open Booking Widget

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href = \"https://www.chronogolf.com/dashboard/#/memberships\"; \"navigating\""'
```

Wait 2 seconds for dashboard to load.

Click the "Book on Calendar" button for the "41 - Frisco Lakes Total Member" membership (the
second Book on Calendar button on the page):

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var bookBtns = btns.filter(b => b.innerText.includes(\"Book on Calendar\"));
if (bookBtns.length > 1) {
  bookBtns[1].click();
  \"clicked-frisco-booking-button\"
} else if (bookBtns.length === 1) {
  bookBtns[0].click();
  \"clicked-only-booking-button\"
} else {
  \"no-booking-buttons-found\"
}
"'
```

Wait 2 seconds for widget to open.

### Select Date (validated by Gate 1)

Run the Select Date script from `references/step-03-widget-scripts.md` (read it in this step), with `[DATE]` as the target date validated in step-01, in YYYY-MM-DD format. If the result is anything other than `clicked-date-N` (e.g., the date cell doesn't exist, is disabled, or an "out of range" message appears), stop — this is a Gate 1 contradiction (the pre-check said the date was in range but the live UI disagrees) and must be treated as a failure, not an invitation to click a nearby date.

Wait 1 second for course/holes selection to appear.

### Select Course and Holes

Run the course visibility check script from `references/step-03-widget-scripts.md`.

**If both course and holes are already selected:** Click "Continue" to proceed to player selection.

**If not yet visible:** wait 1 more second, then run the course select script, then the 18-holes select script (same file).

**Fallback — 9 holes:** If `drought: true` and time is after 6:00 PM, select
"PLP / Total - 9 Hole" and "9 holes" instead.

Wait 1 second, then click "Continue" using the course-level Continue script in `references/step-03-widget-scripts.md`.

### Select 2 Players + Member Rate

Run the 2-players select script from `references/step-03-widget-scripts.md`.

Wait 1 second for player type dropdowns to appear, then set both to "41 - Frisco Lakes Total Member" using the member rate selects script (same file).

Wait 1 second, then click "Continue" using the players-level Continue script (same file).

---

## SUCCESS METRICS

- Date clicked matches the Gate 1-validated date exactly — no substitution
- Both players set to "41 - Frisco Lakes Total Member" (or `party_size` override honored)
- Course/holes selection matches preview-output.json's option (18 holes unless drought fallback)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Date cell not found / disabled / out-of-range despite Gate 1 passing | Do not click a different date. Send Slack alert flagging the Gate 1 / live-UI contradiction. Abort. This should be rare — investigate the discrepancy afterward. |
| Widget won't open after login | Try once more. If it still fails, Slack + abort. |
| "2" players label or member-rate option not found | Retry the selector once. If still not found, Slack + abort — do not guess at a different party configuration. |

## NEXT STEP

Read fully and follow: `step-04-select-time-and-confirm.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

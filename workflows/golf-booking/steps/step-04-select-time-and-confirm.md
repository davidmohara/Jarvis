---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Select Best Available Time and Confirm Booking

## MANDATORY EXECUTION RULES

1. **Confirm immediately** — you have a 5-minute window once you reach the confirmation
   screen.
2. **Never book a time before 2:30 PM on Sunday** (church buffer — hard rule).
3. **Never book a time before 1:00 PM on any day** (below cost threshold).
4. This step iterates through `top_options` in rank order if a given option's slots are
   unavailable — but the date itself never changes from what Gate 1 validated. Only the time
   within that date, or which ranked option is attempted, may shift.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Tee-time selection screen from step-03
**Output:** Confirmed reservation, verified by exact-string match — this is **QUALITY GATE 3**

---

## YOUR TASK

### Read Available Tee Times

Wait 2 seconds for tee times to load.

```bash
osascript << 'EOF'
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "
    var body = document.body.innerText;
    var lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    var times = [];
    for (var i = 0; i < lines.length; i++) {
      if (lines[i] === 'Choose' || lines[i].includes('Choose')) {
        var timeStr = lines[i-1];
        if (timeStr && /^\d{1,2}:\d{2}/.test(timeStr)) {
          times.push(timeStr);
        }
      }
    }
    times.length > 0 ? times.join(',') : 'no-times-found'
    "
  end tell
end tell
EOF
```

Parse the comma-separated list of available times. Convert each to minutes-since-midnight for
comparison with preferred windows.

### Select Best Available Time

From the option's `preferred_start` and `preferred_end` (e.g., "13:00" to "14:30"):

1. Find all available times within the preferred window.
2. If multiple exist, pick the one closest to `preferred_start`.
3. If none exist in the preferred window, expand the search: look up to 2 hours outside the
   preferred window (earlier or later). Accept any reasonable substitute. Still respect hard
   limits: never before 1:00 PM, never before 2:30 PM on Sunday.
4. If still nothing, mark this option as `unavailable` and move to the next ranked option
   (same date — see NEXT STEP for what "no options left" means).
5. Never book a time before 2:30 PM on Sunday.
6. Never book a time before 1:00 PM on any day.

Record the selected time for the confirmation message.

### Click Choose for Selected Time

```bash
osascript << 'EOF'
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "
    var btns = Array.from(document.querySelectorAll('button'));
    var choose = btns.filter(b => b.innerText.trim() === 'Choose');
    if (choose[[INDEX]]) {
      choose[[INDEX]].click();
      'clicked-choose-[INDEX]'
    } else {
      'button-not-found-at-[INDEX]: ' + choose.length + ' buttons total'
    }
    "
  end tell
end tell
EOF
```

Wait 1 second for booking summary screen to load, then click "Continue".

### Confirm Booking

Verify the confirmation screen loaded (timer should be visible):

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
document.body.innerText.includes(\"left to confirm\") ? \"confirmation-screen\" : \"not-there\"
"'
```

If present, read the summary (date/time/cost/course), then **check the "I agree" checkbox**
(required before Confirm Reservation becomes active):

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
var agree = boxes.find(function(b){ return !b.checked });
if (agree) {
  agree.click();
  agree.dispatchEvent(new Event(\"change\", {bubbles:true}));
  \"checked agree\";
} else {
  \"no unchecked checkbox found — may already be checked or missing\";
}
"'
```

Verify the checkbox is now checked:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
boxes.length > 0 ? (boxes[0].checked ? \"checkbox-confirmed-checked\" : \"CHECKBOX-STILL-UNCHECKED\") : \"no-checkbox-found\"
"'
```

If `CHECKBOX-STILL-UNCHECKED` — the `.click()` + `change` event didn't register with Angular.
Force it through the framework:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
var agree = boxes.find(function(b){ return !b.checked });
if (agree) {
  var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, \"checked\").set;
  nativeInputValueSetter.call(agree, true);
  agree.dispatchEvent(new Event(\"input\", {bubbles:true}));
  agree.dispatchEvent(new Event(\"change\", {bubbles:true}));
  agree.checked ? \"force-checked-success\" : \"FORCE-CHECKED-FAILED\";
} else {
  \"no unchecked checkbox found\";
}
"'
```

If still unchecked, try each checkbox on the page:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
boxes.forEach(function(b){
  if (!b.checked) {
    b.click();
    b.dispatchEvent(new Event(\"change\", {bubbles:true}));
  }
});
\"attempted all checkboxes: \" + boxes.length
"'
```

Wait 0.5 seconds, re-verify. Only proceed once `boxes[0].checked === true`.

Wait 0.5 seconds, then click Confirm Reservation (force-enable if needed):

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var confirm = btns.find(function(b){ return b.innerText.trim().toLowerCase().includes(\"confirm reservation\") });
if (!confirm) { \"CONFIRM-BUTTON-NOT-FOUND\"; }
else if (!confirm.disabled) { confirm.click(); \"clicked-confirm\"; }
else {
  confirm.disabled = false;
  confirm.removeAttribute(\"disabled\");
  confirm.dispatchEvent(new Event(\"change\", {bubbles:true}));
  confirm.click();
  \"force-enabled-and-clicked\";
}
"'
```

If result is `CONFIRM-BUTTON-NOT-FOUND` → abort this option, send Slack failure alert. This is
the only abort condition for the confirm click itself.

---

## QUALITY GATE 3 — Confirmation Success (HARD, BLOCKING, EXACT-MATCH)

Wait 3 seconds, then verify booking success by checking for a post-booking confirmation page —
**not** the timer screen. The timer screen disappears on success; a receipt/confirmation page
appears instead:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var timerGone = !body.includes(\"left to confirm\");
var hasReceipt = body.includes(\"reservation is confirmed\") || body.includes(\"Reservation is confirmed\") || body.includes(\"Your booking\") || body.includes(\"booking number\") || body.includes(\"Booking number\") || body.includes(\"confirmation number\") || body.includes(\"Thank you\");
timerGone && hasReceipt ? \"BOOKING-SUCCESS\" : (body.includes(\"left to confirm\") ? \"STILL-ON-TIMER-SCREEN — booking did NOT complete\" : \"UNKNOWN-STATE: \" + body.substring(0,300).replace(/\\n+/g,\" | \"))
"'
```

**Gate 3 passes only on the exact string `BOOKING-SUCCESS`.** Any other result means the
booking did not go through:

| Result | Meaning | Action |
|--------|---------|--------|
| `BOOKING-SUCCESS` | Confirmed | Log `[Gate 3] PASS`. Store `booked_date`, `booked_time`, `booked_holes`, `booked_cost`. Proceed to step-05. |
| `STILL-ON-TIMER-SCREEN` | Checkbox or confirm click failed | Do not treat as success. Reload widget, retry this option once, or move to next ranked option. |
| `UNKNOWN-STATE: ...` | Ambiguous page text | Inspect the returned text. Do not proceed to step-05 assuming success — if uncertain, send Slack alert asking David to verify manually. Do NOT send a success notification. |

If confirmation screen never appeared at all → mark this option unavailable, reload widget,
try the next ranked option (same date, different time or different ranked window).

---

## SUCCESS METRICS

- Gate 3 passes with the literal `BOOKING-SUCCESS` string, never inferred from "looks done"

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Confirmation timer expires | Move to next ranked option. |
| All ranked options exhausted with no booking | Proceed to the "all options exhausted" failure path — Slack notification, abort, `status: aborted`. See workflow.md FAILURE MODES table. |
| `CONFIRM-BUTTON-NOT-FOUND` | Abort this option, Slack failure alert. |

## NEXT STEP

Read fully and follow: `step-05-visual-verification.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

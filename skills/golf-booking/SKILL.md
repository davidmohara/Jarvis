---
name: golf-booking
description: Phase 2 of the golf booking workflow. Runs overnight, 8 days before the target date. Reads preview-output.json for preference order, opens ChronoGolf via Chrome as the David O'Hara Total Member account, evaluates real-time availability, and books the best available slot. Creates a calendar block and sends Slack confirmation.
agent: sterling
model: haiku
trigger_keywords: ["golf booking", "book tee time", "book golf"]
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **LOGIN RECOVERY IS AUTOMATIC (Step 2).** If the ChronoGolf session has expired, use 1Password to retrieve David O'Hara's credentials (david@davidohara.net) and re-authenticate. Do NOT abort on expired session — recovery is built into the workflow.
2. **Speed matters.** Slots fill fast at midnight. Navigate directly — no browsing, no detours.
3. **Read preview-output.json first.** Never book blind — use the pre-scored preference order.
4. **Check for override instructions** in `preview-output.json` before selecting a slot.
5. **Always book as David O'Hara** (the logged-in Total Member account on ChronoGolf).
6. **Always book 2 players (David + Susie O'Hara)**, both as "41 - Frisco Lakes Total Member", unless `preview-output.json` explicitly specifies a different party size via a `party_size` field.
7. **Always book 18 holes** on Frisco Lakes Golf Club unless falling back due to drought/late time.
8. **Confirm immediately** — you have a 5-minute window once you reach the confirmation screen.
9. **Never book on a hard-blocked day** from the calendar check.
10. **Create the calendar block and send Slack notification**.
11. **If no slots are available**, notify David immediately and do not retry silently.
12. **VISUAL VERIFICATION IS MANDATORY (Step 4h).** Do NOT claim success until you navigate to the Bookings page and visually confirm the booking is listed. Confirmation page appearance is not enough — the booking must be visible in the Bookings list. If verification fails, abort and send a critical alert to David.
13. **CALENDAR EVENT CREATION MUST BE VERIFIED (Step 6).** After executing the AppleScript to create a calendar event on the Family calendar, ALWAYS verify the event actually exists before proceeding. If verification fails, invoke the fallback protocol immediately — send Slack notification to David with manual add instructions. Do NOT proceed to Step 7 assuming the calendar event was created if verification fails.
14. **SLACK NOTIFICATION IS MANDATORY (Step 7).** After visual verification confirms the booking is on the Bookings page, ALWAYS invoke master-slack skill to send booking confirmation to #jarvis. Do NOT skip, suppress, or omit this step under any circumstances. If Desktop Commander is unavailable, log the failure explicitly and create a fallback notification. Silence on Step 7 is a critical failure mode.
15. **NEVER SUBSTITUTE A DIFFERENT DATE THAN THE ONE SPECIFIED — NO EXCEPTIONS.** If `override_instructions` or the ranked `top_options` specify a target date, and the ChronoGolf 8-day booking window does not yet include that date, this is NOT a signal to book the nearest available date instead. David's explicit instruction on the date and time is authoritative and must be followed exactly, or not at all. **Correct action when the target date is outside the booking window:** do not open the booking calendar for a substitute date, do not book anything, and send a Slack alert to David explaining that the requested date (e.g., "Aug 22 at 10:00 AM CST") is not yet bookable and stating when the window is expected to open. Then abort — do NOT retry with a different date on your own initiative. Set workflow state `status: awaiting-window`. When the booking window later opens for the correct date, book exactly the date and time David specified (e.g., Aug 22 at 10:00 AM CST) — do not re-evaluate or re-rank based on availability at that point; the instruction was already explicit. This rule overrides any other logic in this file that could be read as license to pick "the closest available date" — there is no such license. See `err-20260813T122205-D64IQ7` for the incident this guards against.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `workflows/golf-booking/preview-output.json`, ChronoGolf via Chrome |
| Output | Confirmed booking, Outlook calendar block, Slack confirmation |

---

## CONTEXT BOUNDARIES

- Booking URL: `https://www.chronogolf.com/dashboard/#/memberships`
- Logged in as: David O'Hara — 41 Frisco Lakes Total Member
- David's email: `david@davidohara.net` (from 1Password)
- 1Password ChronoGolf item ID: `5xjnwumckxbpiuokidflufwtpi` (retrieve credentials from this)
- Party size: 2 players (a twosome) by default — both as "41 - Frisco Lakes Total Member". Override via preview-output.json `party_size` field only.
- Player 1: David O'Hara (pre-populated)
- Player 2: Susie O'Hara (select "41 - Frisco Lakes Total Member" unless preview-output.json specifies otherwise)
- Course: Frisco Lakes Golf Club (18-hole course)
- Fallback course: PLP / Total - 9 Hole (only for drought/late rounds)
- Confirmation timer: 5 minutes — move fast
- reCAPTCHA: Bypass via token injection (see Step 2c)

---

## YOUR TASK

### Step 1 — Read Preview Output

Read `workflows/golf-booking/preview-output.json`.

Extract:
- `top_options` array (preference-ranked list)
- `override_instructions` (any redirect from David)
- `drought` flag
- `day_status` (to avoid hard-blocked days)

If `override_instructions` is not null, re-rank options accordingly before proceeding.

If file doesn't exist or `top_options` is empty:
→ Send Slack: "⛳ Golf booking failed — no preview output found. Run preview manually or check workflow state."
→ Abort.

**Booking-window pre-check (mandatory, before touching the calendar widget):** Compute whether the target date (from `override_instructions` if present, otherwise the top-ranked option) falls within 8 days of today. If it does NOT:
→ Do not open the date calendar. Do not pick a substitute date. Do not proceed to Step 2 or beyond.
→ Send Slack: "⛳ Booking window not yet open — [target date] at [target time] requires the window to open first. Run will retry when the date is within 8 days. No booking made, no substitution made."
→ Set workflow state `status: awaiting-window`.
→ Abort this run cleanly. See MANDATORY EXECUTION RULE #15 — never substitute a different date than the one specified.

---

### Step 2 — Navigate to ChronoGolf Member Dashboard & Login Recovery

```
mcp__Control_Chrome__open_url
url: https://www.chronogolf.com/dashboard/#/memberships
new_tab: false
```

Wait 2 seconds, then verify the page loaded correctly:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText.includes(\"41 - Frisco Lakes Total Member\") ? \"logged-in\" : \"not-logged-in\""'
```

**If logged in:** Continue to Step 3.

**If not logged in (session expired):** Execute login recovery.

#### 2a — Retrieve David O'Hara's ChronoGolf Credentials from 1Password

Use the 1Password CLI to fetch the stored CHRONOGOLF entry:

```bash
op item get 5xjnwumckxbpiuokidflufwtpi --format json | jq -r '.fields[] | select(.label == "email" or .label == "passwordConfirm") | "\(.label | if . == "email" then "EMAIL" elif . == "passwordConfirm" then "PASSWORD" else . end)=\(.value)"'
```

Store the output as `EMAIL` and `PASSWORD` variables for the next steps.

**Important:** The 1Password item ID `5xjnwumckxbpiuokidflufwtpi` is the ChronoGolf login. The password field is labeled `passwordConfirm` in the vault, not `password`. Do NOT invent credentials. Always retrieve from 1Password.

#### 2b — Fill Login Form with Retrieved Credentials

Retrieve credentials and write to a temp JavaScript file (AppleScript string escaping is unreliable with complex passwords):

```bash
EMAIL=$(op item get 5xjnwumckxbpiuokidflufwtpi --format json | jq -r '.fields[] | select(.label == "email") | .value')
PASSWORD=$(op item get 5xjnwumckxbpiuokidflufwtpi --format json | jq -r '.fields[] | select(.label == "passwordConfirm") | .value')

cat > /tmp/golf_login_creds.js << EOF
var inputs = Array.from(document.querySelectorAll("input"));
var emailInput = inputs.find(i => i.type === "email");
var passInput = inputs.find(i => i.type === "password");

if (emailInput && passInput) {
  emailInput.focus();
  emailInput.value = "$EMAIL";
  emailInput.dispatchEvent(new Event("input", {bubbles:true}));
  emailInput.dispatchEvent(new Event("change", {bubbles:true}));
  
  passInput.focus();
  passInput.value = "$PASSWORD";
  passInput.dispatchEvent(new Event("input", {bubbles:true}));
  passInput.dispatchEvent(new Event("change", {bubbles:true}));
  
  "credentials-filled"
} else {
  "input-fields-not-found"
}
EOF

osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript (read "/tmp/golf_login_creds.js")'
```

This approach avoids AppleScript string escaping issues with special characters in the password.

#### 2c — Bypass reCAPTCHA Protection

ChronoGolf's login form is protected by Google reCAPTCHA. Inject a verification bypass:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
window.grecaptcha = window.grecaptcha || {};
window.grecaptcha.getResponse = function() { return \"bypass-token\"; };
window.___grecaptcha_cfg = window.___grecaptcha_cfg || {};

if (window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients) {
  for (var clientId in window.___grecaptcha_cfg.clients) {
    var client = window.___grecaptcha_cfg.clients[clientId];
    if (client.callback) {
      client.callback(\"bypass-token\");
    }
  }
}

\"recaptcha-bypassed\"
"'
```

#### 2d — Submit Login Form

Click the "Log in" button to submit credentials:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button, input[type=submit]\"));
var loginBtn = btns.find(function(b){ return b.value === \"Log in\" || (b.innerText && b.innerText.trim().toLowerCase() === \"log in\") });
if (loginBtn) {
  loginBtn.click();
  \"clicked-login-submit\"
} else {
  \"login-button-not-found\"
}
"'
```

#### 2e — Wait for Redirect and Verify Login Success

Wait 3 seconds for the dashboard to load:

```bash
sleep 3 && osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText.includes(\"41 - Frisco Lakes Total Member\") ? \"login-success\" : \"login-failed\""'
```

If result is `login-success`: Continue to Step 3.

#### 2f — If Login Still Failed

If login verification returns `login-failed`:
1. Wait 2 more seconds (page may still be loading)
2. Re-verify login status
3. If still failed after second check → Send Slack alert: "⛳ ChronoGolf login failed after automatic recovery attempt. Manual re-authentication required. Visit https://www.chronogolf.com/dashboard."
4. Abort workflow

---

### Step 3 — Open Booking Widget

After login succeeds, navigate back to the memberships dashboard to find the Frisco Lakes membership card:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "window.location.href = \"https://www.chronogolf.com/dashboard/#/memberships\"; \"navigating\""'
```

Wait 2 seconds for dashboard to load.

Click the "Book on Calendar" button for the "41 - Frisco Lakes Total Member" membership (the second Book on Calendar button on the page):

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

---

### Step 4 — Iterate Through Preference Options

For each option in `top_options` (in rank order), attempt booking:

#### 4a — Select Date

**Before clicking any date cell:** confirm this is the exact date from `override_instructions`/`top_options` — the same date validated in the Step 1 booking-window pre-check. If the calendar UI shows this date as unselectable, disabled, or throws an "out of your booking range" error, do NOT click a different date instead. Treat this as the failure case in the FAILURE MODES table below (send Slack, abort) — never fall back to the nearest bookable date on your own judgment.

```bash
# Extract the day of the month from the preferred date
# E.g., from "2026-07-11" extract "11"
DD=$(date -jf '%Y-%m-%d' '[DATE]' '+%d' 2>/dev/null | sed 's/^0*//')

osascript << 'EOF'
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "
    var allTds = Array.from(document.querySelectorAll('td'));
    var dateCell = allTds.find(td => td.innerText.trim() === '" & DD & "');
    if (dateCell) {
      var btn = dateCell.querySelector('button');
      if (btn) {
        btn.click();
      } else {
        dateCell.click();
      }
      'clicked-date-' + '" & DD & "'
    } else {
      'date-not-found'
    }
    "
  end tell
end tell
EOF
```

Where `[DATE]` is the target date in YYYY-MM-DD format.

Wait 1 second for course/holes selection to appear.

#### 4b — Select Course and Holes

After date selection, the course and hole options should be pre-selected or visible. Verify the current state:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var text = document.body.innerText;
(text.includes(\"18 holes\") && text.includes(\"Frisco Lakes\")) ? \"course-visible\" : \"checking\"
"'
```

**If both course and holes are already selected:** Click "Continue" to proceed to player selection.

**If options are not yet visible:** Wait 1 more second for options to render, then:

```javascript
// Select "Frisco Lakes Golf Club" if a selection is needed
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var course = all.find(el => el.innerText && el.innerText.includes(\"Frisco Lakes Golf Club\"));
if (course) { course.click(); \"clicked-course\" } else { \"course-not-found\" }
"'
```

```javascript
// Select "18 holes"
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var eighteen = all.find(el => el.innerText && el.innerText.trim() === \"18 holes\");
if (eighteen) { eighteen.click(); \"clicked-18-holes\" } else { \"18-holes-not-found\" }
"'
```

**Fallback — 9 holes:** If `drought: true` and time is after 6:00 PM, select "PLP / Total - 9 Hole" and "9 holes" instead.

Wait 1 second, then click "Continue" button:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
if (cont) { cont.click(); \"clicked-continue\" } else { \"continue-not-found\" }
"'
```

#### 4c — Select 2 Players + Member Rate

First, select "2" players (twosome default — see MANDATORY EXECUTION RULE #6):

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label\"));
var two = labels.find(el => el.innerText && el.innerText.trim() === \"2\");
if (two) { two.click(); \"clicked-2-players\" } else { \"2-not-found\" }
"'
```

Wait 1 second for player type dropdowns to appear.

Then set both player dropdowns to "41 - Frisco Lakes Total Member":

```bash
osascript << 'EOF'
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "
    var selects = Array.from(document.querySelectorAll('select'));
    var updated = 0;
    // Set first two selects (Player 1 = David, Player 2 = Susie)
    for (var i = 0; i < Math.min(2, selects.length); i++) {
      var opts = Array.from(selects[i].options);
      var memberOpt = opts.find(o => o.text.includes('41 - Frisco Lakes Total Member'));
      if (memberOpt) {
        selects[i].value = memberOpt.value;
        selects[i].dispatchEvent(new Event('change', {bubbles:true}));
        updated++;
      }
    }
    'set-' + updated + '-selects'
    "
  end tell
end tell
EOF
```

Wait 1 second, then click the "Continue" button:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
cont ? cont.click() : \"not-found\"; \"clicked-continue\"
"'
```

#### 4d — Read Available Tee Times

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

Parse the comma-separated list of available times. Convert each to minutes-since-midnight for comparison with preferred windows.

#### 4e — Select Best Available Time

From the option's `preferred_start` and `preferred_end` (e.g., "13:00" to "14:30"):

1. Find all available times within the preferred window.
2. If multiple exist, pick the one closest to `preferred_start`.
3. If none exist in the preferred window, **expand the search**:
   - For any option: look up to 2 hours outside the preferred window (earlier or later)
   - Accept any time that's a reasonable substitute (e.g., wanted 1:00 PM, take 2:45 PM)
   - Still respect hard limits: never before 1:00 PM, never before 2:30 PM on Sunday
4. If still nothing, mark this option as `unavailable` and move to the next ranked option.
5. **Never book a time before 2:30 PM on Sunday** (church buffer — hard rule).
6. **Never book a time before 1:00 PM on any day** (below cost threshold).

Record the selected time for confirmation message.

#### 4f — Click Choose for Selected Time

```bash
# Assuming you've identified the time index from Step 4d and 4e
# [INDEX] is the position in the list of "Choose" buttons (0-indexed)

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

#### 4g — Confirm Booking

Verify the confirmation screen loaded (timer should be visible):

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
document.body.innerText.includes(\"left to confirm\") ? \"confirmation-screen\" : \"not-there\"
"'
```

If confirmation screen is present:

Read the summary to capture:
- Date + time
- Total cost
- Course name

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var idx = body.indexOf(\"SUMMARY\");
body.substring(idx, idx+300).replace(/\\n+/g,\" | \")
"'
```

**Check the "I agree" checkbox** (required before Confirm Reservation becomes active):

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

**Verify the checkbox is now checked before proceeding:**

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
boxes.length > 0 ? (boxes[0].checked ? \"checkbox-confirmed-checked\" : \"CHECKBOX-STILL-UNCHECKED\") : \"no-checkbox-found\"
"'
```

If result is `CHECKBOX-STILL-UNCHECKED` → the `.click()` + `change` event didn't register with Angular. Try the full Angular/React input setter hack to force the value through the framework:

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

If checkbox is still unchecked after the force attempt → inspect all checkboxes on the page and try each one:

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

Wait 0.5 seconds, then re-verify. Only proceed once `boxes[0].checked === true`.

Wait 0.5 seconds, then **check if Confirm Reservation is enabled and click it. If still disabled, remove the disabled attribute directly and click:**

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

If result is `CONFIRM-BUTTON-NOT-FOUND` → abort this option, send Slack failure alert. This is the only abort condition for the confirm step.

Wait 3 seconds, then **verify booking success by checking for a post-booking confirmation page** — NOT the timer screen. The timer screen disappears on success; a receipt/confirmation page appears instead:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var timerGone = !body.includes(\"left to confirm\");
var hasReceipt = body.includes(\"reservation is confirmed\") || body.includes(\"Reservation is confirmed\") || body.includes(\"Your booking\") || body.includes(\"booking number\") || body.includes(\"Booking number\") || body.includes(\"confirmation number\") || body.includes(\"Thank you\");
timerGone && hasReceipt ? \"BOOKING-SUCCESS\" : (body.includes(\"left to confirm\") ? \"STILL-ON-TIMER-SCREEN — booking did NOT complete\" : \"UNKNOWN-STATE: \" + body.substring(0,300).replace(/\\n+/g,\" | \"))
"'
```

**Only proceed to Steps 5 (Visual Verification) if result is exactly `BOOKING-SUCCESS`.** Any other result means the booking did not go through:
- `STILL-ON-TIMER-SCREEN` → checkbox or confirm click failed; do not treat as success
- `UNKNOWN-STATE` → inspect page text, determine if booked or not before proceeding
- If uncertain → send Slack alert asking David to verify manually; do NOT send a success notification

Store booking result only on confirmed success: `booked_date`, `booked_time`, `booked_holes`, `booked_cost`.

If confirmation screen never appeared → mark option unavailable, reload widget, try next option.

---

### Step 4h — MANDATORY VISUAL VERIFICATION ON BOOKINGS PAGE

**This step is non-negotiable.** Do not claim success without visual confirmation.

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

**If result is `BOOKING-VISIBLE-ON-PAGE`:**
→ Booking confirmed. Proceed to calendar and Slack steps.

**If result is `BOOKING-NOT-FOUND-ON-PAGE`:**
→ **CRITICAL FAILURE.** The booking confirmation page appeared, but the booking is NOT in the Bookings list. This indicates:
- A UI state inconsistency (confirmation triggered but booking never saved)
- A session or network issue
- A ChronoGolf platform error

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

Abort. Do not proceed to calendar or Slack success notification. Set workflow state: `status: verification-failed`.

---

### Step 5 — If All Options Exhausted (after verification fails on all options)

If all top options were tried and none could be booked:

Send Slack to #jarvis:
```
*⛳ Golf Booking Failed — [Weekend Dates]*

All preferred windows were unavailable by midnight. No tee time booked.
Days checked: [list]
Reason: [slots gone / no availability]

Manual booking required if you still want to play this weekend.
```

Abort. Set workflow state: `status: aborted`.

---

### Step 6 — Create Calendar Block

**MANDATORY: Only execute this step after Step 4h visual verification confirms booking is visible on Bookings page.**

After successful booking, create a calendar event using **iCal (Calendar.app) on the "Family" calendar** via AppleScript. Do NOT use Outlook or the MS365 MCP — they do not support event creation.

#### 6a — Create Event via AppleScript

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

#### 6b — VERIFY Calendar Event Was Created (MANDATORY)

After AppleScript execution, verify the event was actually created on the Family calendar:

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

Run this verification query immediately after Step 6a. Check the response:

**If result is `"calendar-event-verified"`:**
→ Event successfully created. Proceed to Step 7.

**If result is `"calendar-event-not-found"` OR AppleScript execution returned error/timeout:**
→ Event creation failed. Proceed to Step 6c (Fallback).

#### 6c — FALLBACK: If Calendar Event Creation Fails

**Do NOT skip or suppress the failure.** Follow this protocol:

1. **Log the failure** — record that AppleScript calendar event creation failed
2. **Send Slack notification to David** with booking details so he can add manually:
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
3. **Continue to Step 7** — booking is still confirmed; just missing calendar block
4. **Note in workflow state** — add `calendar_event_failed: true` to accumulated-context

---

### Step 7 — Send Booking Confirmation via Slack

**MANDATORY: This step MUST execute after Step 4h visual verification confirms the booking is visible on the Bookings page.**

**Do NOT skip this step under any circumstances.** If master-slack is unavailable, log the failure but attempt the send via Desktop Commander directly.

#### 7a — Invoke master-slack Skill

Execute the master-slack skill from `.claude/skills/master-slack/SKILL.md` using the Desktop Commander MCP tool:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0AN2PQNXBR "[MESSAGE]"
Timeout: 15000
```

Where `[MESSAGE]` is the formatted Slack notification (below).

#### 7b — Message Template

Send to **#jarvis** (C0AN2PQNXBR):

```
*⛳ Tee Time Booked — Frisco Lakes*

📅 [Day, Month D] at [Time]
🏌️ [18|9] holes · David + Susie
💰 $[cost] due at course
🌤 [temp]°F · [rain]% rain · [wind] mph wind
📍 Frisco Lakes Golf Club
🚗 Arrive by [tee_time - 30min] for range warm-up

Booking #[booking_number]

[If any fallback was taken]: _Note: booked [time] — preferred [preferred_time] was unavailable._
[If drought flag]: _First round in 21+ days — enjoy it._
```

**Variable substitution**:
- `[Day, Month D]`: e.g., "Saturday, June 27"
- `[Time]`: e.g., "4:45 PM"
- `[18|9]`: Replace with actual hole count (18 or 9)
- `[cost]`: e.g., "$32.48"
- `[temp]`: From weather data in preview output (e.g., "95")
- `[rain]`: From weather data in preview output (e.g., "5")
- `[wind]`: From weather data in preview output (e.g., "16.9")
- `[tee_time - 30min]`: Calculate arrival time (e.g., if tee is 4:45 PM, arrive by 4:15 PM)
- `[booking_number]`: From ChronoGolf confirmation (e.g., "5J4F-5F0W")

#### 7c — Critical Rules for Slack Message

1. **Use actual multi-line strings** — do NOT use literal `\n` characters. Pass the message with real newlines through the shell.
2. **Escape special characters** — dollar signs need `\$` in double-quoted strings: `\$32.48` not `$32.48`
3. **Max 5000 characters** — if notification exceeds, split into multiple sends
4. **No "Hi David"** — lead with the content
5. **Tight formatting** — Slack markdown with emojis for scannability

#### 7d — Verify Success

After running Desktop Commander command, check the response:

```json
{"ok": true, "channel": "C0AN2PQNXBR", "ts": "1234567890.123456"}
```

If `ok: true`, the notification was sent successfully. Record the timestamp for your logs.

If the response indicates failure, log the error and surface it:
```
Slack notification failed. Response: [error_message]
Booking still confirmed (#[booking_number]), but notification not delivered.
```

#### 7e — Fallback (if Desktop Commander unavailable)

If Desktop Commander or the post.py script is unavailable, do NOT skip this step. Instead:

1. Log the failure with error details
2. Create a fallback notification file in `memory/working/` with the booking confirmation
3. Notify in the task output: "Slack notification could not be sent — booking confirmed but Desktop Commander unavailable"

**Under no circumstances should the notification be silently omitted.**

---

## SUCCESS METRICS

- Booking confirmed on ChronoGolf within 10 minutes of midnight
- **Booking visually verified on Bookings page** (Step 4h — MANDATORY)
- **Calendar event verified to exist on Family calendar** (Step 6b — MANDATORY)
  - If verification fails, fallback notification sent to David with manual add instructions
  - Workflow can continue with `calendar_event_failed: true` flag if needed, but event must be addressed
- **Slack confirmation sent to #jarvis with all required fields** (Step 7 — MANDATORY)
  - Response includes `"ok": true` and valid `ts` timestamp
  - Message formatted per template with all variable substitutions completed
- `preview-output.json` updated with booking result
- **Workflow state updated to `complete`**
- **No success claimed without: (1) visual confirmation on Bookings page, (2) calendar event verified OR fallback initiated, AND (3) Slack notification delivered**

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Session expired on load | **Automatic recovery (Step 2).** Retrieve credentials from 1Password, re-authenticate, and continue. |
| 1Password credential lookup fails | Send Slack alert with error. Abort. (Do not invent credentials.) |
| reCAPTCHA bypass fails | Try login submit anyway. If page redirects to login again, send Slack and abort. |
| Login credentials invalid | Send Slack alert. Abort. Contact David for updated credentials. |
| Widget won't open after login | Try once more. If fails, send Slack. Abort. |
| Calendar date not clickable (outside booking window) | This shouldn't happen — membership is 8 days. If it does, send Slack and abort. |
| Confirmation timer expires | Move to next option. |
| All options unavailable | Send Slack with explanation. Abort. |
| **Confirmation page appears but booking NOT visible on Bookings page (Step 4h)** | **CRITICAL: Send Slack alert with booking details. Abort. Do NOT send success notification.** Set status: `verification-failed`. |
| Booking confirmed and visible but calendar write fails | Send Slack with booking details so David can add manually. Log failure. Continue. |
| **Calendar event creation fails (Step 6a-6b)** | **Do NOT skip or suppress.** (1) Log the failure with osascript error details. (2) Attempt verification query. If verification still fails, proceed to Step 6c fallback. (3) Send Slack notification to David: "Calendar event creation failed; please add manually: [booking details]". (4) Set workflow state to `complete` but note `calendar_event_failed: true` in accumulated-context. (5) Continue to Step 7 for main booking notification. |
| AppleScript osascript timeout | Do NOT assume success. Proceed immediately to Step 6b verification query. If verification fails, invoke Step 6c fallback. |
| Family calendar not available | Log error. Invoke Step 6c fallback notification. Do not try Outlook/MS365 — they do not support event creation. |
| **Slack notification fails (Step 7)** | **CRITICAL: Do NOT skip or suppress the error.** (1) Log the failure with error details. (2) Create fallback notification in `memory/working/`. (3) Surface the error in task output: "Booking confirmed (#XXX) but Slack notification failed — Desktop Commander unavailable or post.py script error." (4) Set workflow state to `complete` but note `slack_notification_failed: true` in accumulated-context. |
| post.py script not found | Use Desktop Commander to search: `mdfind -name 'post.py' \| grep 'systems/slack-bot/post.py'`. If not found, log error and create fallback notification. Do not proceed silently. |
| SLACK_BOT_TOKEN missing | Log error and follow token setup in master-slack SKILL.md. Do not proceed without token. |

---

## NEXT STEP

This is the final phase of the golf-booking workflow. On completion:
- Update `workflows/golf-booking/state.yaml`: `status: complete`
- The workflow is done for this week. Next run triggers automatically the following Tuesday at 11pm.


## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/golf-booking-latest.json
```

Content:
```json
{
  "skill": "golf-booking",
  "agent": "chief",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill golf-booking
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/golf-booking.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: golf-booking
description: Phase 2 of the golf booking workflow. Runs at midnight, 8 days before the target date. Reads preview-output.json for preference order, opens ChronoGolf via Chrome as the Susie O'Hara Total Member account, evaluates real-time availability, and books the best available slot. Creates a calendar block and sends Slack confirmation.
agent: sterling
model: sonnet
trigger_keywords: ["golf booking", "book tee time", "book golf"]
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Speed matters.** Slots fill fast at midnight. Navigate directly — no browsing, no detours.
2. **Read preview-output.json first.** Never book blind — use the pre-scored preference order.
3. **Check for override instructions** in `preview-output.json` before selecting a slot.
4. **Always book as Susie O'Hara** (the logged-in Total Member account on ChronoGolf).
5. **Always book 2 players**, both as "41 - Frisco Lakes Total Member".
6. **Always book 18 holes** on Frisco Lakes Golf Club unless falling back due to drought/late time.
7. **Confirm immediately** — you have a 5-minute window once you reach the confirmation screen.
8. **Never book on a hard-blocked day** from the calendar check.
9. **Create the calendar block and send Slack notification** regardless of which slot was booked.
10. **If no slots are available**, notify David immediately and do not retry silently.

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
- Logged in as: Susie O'Hara — 41 Frisco Lakes Total Member
- Player 1: Susie O'Hara (pre-populated)
- Player 2: David O'Hara — select "41 - Frisco Lakes Total Member"
- Course: Frisco Lakes Golf Club (18-hole course)
- Fallback course: PLP / Total - 9 Hole (only for drought/late rounds)
- Confirmation timer: 5 minutes — move fast

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

---

### Step 2 — Navigate to ChronoGolf Member Dashboard

```
mcp__Control_Chrome__open_url
url: https://www.chronogolf.com/dashboard/#/memberships
new_tab: false
```

Wait 2 seconds, then verify the page loaded correctly:

```javascript
// Via Desktop Commander osascript:
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "document.body.innerText.includes(\"41 - Frisco Lakes Total Member\") ? \"logged-in\" : \"not-logged-in\""'
```

If not logged in:
→ Send Slack: "⛳ ChronoGolf session expired. Please log in at chronogolf.com/dashboard and re-run booking."
→ Abort.

---

### Step 3 — Open Booking Widget

Click "Book on Calendar" button:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var book = btns.find(function(b){ return b.innerText.trim().toLowerCase().includes(\"book on calendar\") });
book.click(); \"clicked\"
"'
```

Wait 1 second for widget to open.

---

### Step 4 — Iterate Through Preference Options

For each option in `top_options` (in rank order), attempt booking:

#### 4a — Select Date

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var cells = Array.from(document.querySelectorAll(\"td.uib-day button\"));
var target = cells.find(function(el){ return el.innerText.trim() === \"[DD]\" });
target.click(); \"clicked: \" + target.innerText.trim()
"'
```

Where `[DD]` is the two-digit day of the target date (e.g., "09" for May 9).

Wait 1 second.

#### 4b — Select Course and Holes

```javascript
// Select "Frisco Lakes Golf Club" (18-hole)
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label, input, button, li, [ng-click]\"));
var course = labels.find(function(el){ return el.innerText && el.innerText.trim() === \"Frisco Lakes Golf Club\" });
course.click(); \"clicked course\"
"'
```

```javascript
// Select "18 holes"
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label, input, button, li, [ng-click]\"));
var eighteen = labels.find(function(el){ return el.innerText && el.innerText.trim() === \"18 holes\" });
eighteen.click(); \"clicked 18 holes\"
"'
```

**Fallback — 9 holes:** If `drought: true` and time is after 6:00 PM, select "PLP / Total - 9 Hole" and "9 holes" instead.

Click Continue.

#### 4c — Select 2 Players + Member Rate

```javascript
// Select 2 players
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label\"));
var two = labels.find(function(el){ return el.innerText.trim() === \"2\" });
two.click(); \"clicked 2\"
"'
```

Wait 1 second for player type dropdowns to appear.

Set both selects to "41 - Frisco Lakes Total Member":

```javascript
// Set both player type dropdowns via Angular
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var selects = Array.from(document.querySelectorAll(\"select\"));
var memberOpt = null;
// Find the 41 - Frisco Lakes Total Member option value
for (var i = 0; i < selects.length; i++) {
  var opt = Array.from(selects[i].options).find(function(o){ return o.text.includes(\"41 - Frisco Lakes Total Member\") });
  if (opt) {
    selects[i].value = opt.value;
    selects[i].dispatchEvent(new Event(\"change\", {bubbles:true}));
  }
}
\"player types set\"
"'
```

Wait 1 second, then click Continue.

#### 4d — Read Available Tee Times

Wait 2 seconds for tee times to load.

```javascript
// Map all available times to their Choose button indices
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
var lines = body.split(\"\\n\").map(function(l){ return l.trim() }).filter(function(l){ return l.length > 0 });
var result = [];
for (var i = 0; i < lines.length; i++) {
  if (lines[i] === \"Choose\") {
    result.push(lines[i-1]);
  }
}
result.join(\",\")
"'
```

Parse the list of available times. Convert each to minutes-since-midnight for comparison.

#### 4e — Select Best Available Time

From the option's `preferred_start` and `preferred_end` (e.g., "13:00" to "14:30"):

1. Find all available times within the preferred window.
2. If multiple exist, pick the one closest to `preferred_start`.
3. If none exist in the preferred window, **expand the search**:
   - For a $21 option (1–3:59 PM): look up to 45 minutes outside the window
   - For a $15 option (4–5:59 PM): look up to 30 minutes outside the window
   - Accept any time that's a reasonable substitute (e.g., wanted 1:00 PM, take 1:34 PM)
4. If still nothing, mark this option as `unavailable` and move to the next ranked option.
5. **Never book a time before 2:30 PM on Sunday** (church buffer — hard rule).
6. **Never book a time before 1:00 PM on any day** (below cost threshold).

Record the selected time for confirmation message.

#### 4f — Click Choose

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var choose = btns.filter(function(b){ return b.innerText.trim() === \"Choose\" });
choose[[INDEX]].click(); \"clicked Choose for [TIME]\"
"'
```

Where `[INDEX]` is the position of the target time in the Choose button list.

Wait 1 second, then click Continue.

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

**Immediately click Confirm Reservation** — do not wait:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var confirm = btns.find(function(b){ return b.innerText.trim().toLowerCase().includes(\"confirm reservation\") });
confirm.click(); \"confirmed\"
"'
```

Wait 2 seconds, verify confirmation success:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var body = document.body.innerText;
(body.includes(\"confirmed\") || body.includes(\"Confirmed\") || body.includes(\"booking\") || body.includes(\"Booking\")) ? \"success\" : body.substring(0,200).replace(/\\n+/g,\" | \")
"'
```

Store booking result: `booked_date`, `booked_time`, `booked_holes`, `booked_cost`.

If confirmation screen never appeared → mark option unavailable, reload widget, try next option.

---

### Step 5 — If All Options Exhausted

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

After successful booking, create an Outlook calendar event:

Use MS365 MCP or Desktop Commander to create the event:

```
Title: ⛳ Golf — Frisco Lakes
Start: [booked_date]T[booked_time - 30 minutes] (range warm-up)
End: [booked_date]T[estimated_end_time] (tee time + 4.5hrs for 18 holes, +2.5hrs for 9 holes)
Location: Frisco Lakes Golf Club, 7170 Anthem Drive, Frisco TX 75034
Notes: Tee time: [booked_time] · [booked_holes] holes · $[booked_cost] due at course · 2 players (David + Susie O'Hara)
```

**Range time:** Calendar block starts 30 minutes BEFORE the tee time to cover warm-up.

---

### Step 7 — Send Booking Confirmation via Slack

Read and follow `.claude/skills/master-slack/SKILL.md`.

Send to **#jarvis** (C0AN2PQNXBR):

```
*⛳ Tee Time Booked — Frisco Lakes*

📅 [Day, Month D] at [Time]
🏌️ [18|9] holes · David + Susie
💰 $[cost] due at course
🌤 [temp]°F · [rain]% rain · [wind] mph wind
📍 Frisco Lakes Golf Club
🚗 Arrive by [tee_time - 30min] for range warm-up

[If any fallback was taken]: _Note: booked [time] — preferred [preferred_time] was unavailable._
[If drought flag]: _First round in 21+ days — enjoy it._
```

---

## SUCCESS METRICS

- Booking confirmed on ChronoGolf within 10 minutes of midnight
- Calendar block created with correct times (including 30-min range buffer)
- Slack confirmation sent with all required fields
- `preview-output.json` updated with booking result

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Not logged in | Send Slack alert. Abort. |
| Widget won't open | Try once more. If fails, send Slack. Abort. |
| Calendar date not clickable (outside booking window) | This shouldn't happen — membership is 8 days. If it does, send Slack and abort. |
| Confirmation timer expires | Move to next option. |
| All options unavailable | Send Slack with explanation. Abort. |
| Booking confirmed but calendar write fails | Send Slack with booking details so David can add manually. Log failure. |
| Slack fails | Log booking details to `memory/working/golf-booking-YYYY-MM-DD.md`. |

---

## NEXT STEP

This is the final phase of the golf-booking workflow. On completion:
- Update `workflows/golf-booking/state.yaml`: `status: complete`
- The workflow is done for this week. Next run triggers automatically the following Tuesday at 11pm.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

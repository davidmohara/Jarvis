---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

**Agent:** Sterling
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

```bash
# Extract the day of the month from the preferred date, e.g. from "2026-07-11" extract "11"
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

Where `[DATE]` is the target date validated in step-01, in YYYY-MM-DD format. If the result is
anything other than `clicked-date-N` (e.g., the date cell doesn't exist, is disabled, or an
"out of range" message appears), stop — this is a Gate 1 contradiction (the pre-check said the
date was in range but the live UI disagrees) and must be treated as a failure, not an
invitation to click a nearby date.

Wait 1 second for course/holes selection to appear.

### Select Course and Holes

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var text = document.body.innerText;
(text.includes(\"18 holes\") && text.includes(\"Frisco Lakes\")) ? \"course-visible\" : \"checking\"
"'
```

**If both course and holes are already selected:** Click "Continue" to proceed to player
selection.

**If not yet visible:** wait 1 more second, then:

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var course = all.find(el => el.innerText && el.innerText.includes(\"Frisco Lakes Golf Club\"));
if (course) { course.click(); \"clicked-course\" } else { \"course-not-found\" }
"'
```

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var eighteen = all.find(el => el.innerText && el.innerText.trim() === \"18 holes\");
if (eighteen) { eighteen.click(); \"clicked-18-holes\" } else { \"18-holes-not-found\" }
"'
```

**Fallback — 9 holes:** If `drought: true` and time is after 6:00 PM, select
"PLP / Total - 9 Hole" and "9 holes" instead.

Wait 1 second, then click "Continue":

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
if (cont) { cont.click(); \"clicked-continue\" } else { \"continue-not-found\" }
"'
```

### Select 2 Players + Member Rate

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label\"));
var two = labels.find(el => el.innerText && el.innerText.trim() === \"2\");
if (two) { two.click(); \"clicked-2-players\" } else { \"2-not-found\" }
"'
```

Wait 1 second for player type dropdowns to appear, then set both to "41 - Frisco Lakes Total
Member":

```bash
osascript << 'EOF'
tell application "Google Chrome"
  tell active tab of front window
    execute javascript "
    var selects = Array.from(document.querySelectorAll('select'));
    var updated = 0;
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

Wait 1 second, then click "Continue":

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
cont ? cont.click() : \"not-found\"; \"clicked-continue\"
"'
```

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

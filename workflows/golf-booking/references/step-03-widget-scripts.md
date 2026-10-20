<!-- system:start -->
# Step-03 Widget Scripts (golf-booking)

Exact osascript/JavaScript blocks for step-03. Run them as written; the step file holds the stop conditions and fallback rules.

## Select Date script

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

## Course visibility check script

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var text = document.body.innerText;
(text.includes(\"18 holes\") && text.includes(\"Frisco Lakes\")) ? \"course-visible\" : \"checking\"
"'
```

## Course select script

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var course = all.find(el => el.innerText && el.innerText.includes(\"Frisco Lakes Golf Club\"));
if (course) { course.click(); \"clicked-course\" } else { \"course-not-found\" }
"'
```

## 18-holes select script

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var all = Array.from(document.querySelectorAll(\"button, label, li, div[ng-click]\"));
var eighteen = all.find(el => el.innerText && el.innerText.trim() === \"18 holes\");
if (eighteen) { eighteen.click(); \"clicked-18-holes\" } else { \"18-holes-not-found\" }
"'
```

## Continue click script (course)

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
if (cont) { cont.click(); \"clicked-continue\" } else { \"continue-not-found\" }
"'
```

## 2-players select script

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var labels = Array.from(document.querySelectorAll(\"label\"));
var two = labels.find(el => el.innerText && el.innerText.trim() === \"2\");
if (two) { two.click(); \"clicked-2-players\" } else { \"2-not-found\" }
"'
```

## Member rate selects script

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

## Continue click script (players)

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var btns = Array.from(document.querySelectorAll(\"button\"));
var cont = btns.find(b => b.innerText.trim().toLowerCase() === \"continue\");
cont ? cont.click() : \"not-found\"; \"clicked-continue\"
"'
```

<!-- system:end -->

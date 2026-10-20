<!-- system:start -->
# Step-04 Confirm Scripts (golf-booking)

Exact osascript/JavaScript blocks for step-04. Run as written; the step file holds the selection logic and stop conditions.

## Read tee times script

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

## Choose click script

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

## Confirmation screen check script

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
document.body.innerText.includes(\"left to confirm\") ? \"confirmation-screen\" : \"not-there\"
"'
```

## Agree checkbox script

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

## Checkbox verify script

```javascript
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var boxes = Array.from(document.querySelectorAll(\"input[type=checkbox]\"));
boxes.length > 0 ? (boxes[0].checked ? \"checkbox-confirmed-checked\" : \"CHECKBOX-STILL-UNCHECKED\") : \"no-checkbox-found\"
"'
```

## Force-check script (Angular)

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

## Try-all-checkboxes script

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

## Confirm Reservation click script

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

<!-- system:end -->

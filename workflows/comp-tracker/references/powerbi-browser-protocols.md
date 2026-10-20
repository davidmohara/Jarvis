<!-- system:start -->
# PowerBI Browser Protocols (comp-tracker)

## Click Protocol (replaces browser_batch for all steps)

**Coordinate formula:**
```
screen_x = page_x  (no offset — window starts at x=0)
screen_y = window_y + chrome_ui_height + page_y
         = 33 + 121 + page_y
         = 154 + page_y
```

Chrome UI height = outerHeight(949) - innerHeight(828) = 121px. Window y = 33. These are confirmed values — store in state.yaml as `cliclick_offset_y: 154`.

**Finding element coordinates (always do this — never guess):**
```javascript
// Via execute_javascript:
var el = document.querySelector('[aria-label="Element Name"]');
// OR search by text:
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length; i++) {
  if (all[i].innerText && all[i].innerText.trim() === 'Target Text') {
    var rect = all[i].getBoundingClientRect();
    // screen_x = rect.left + rect.width/2
    // screen_y = 154 + rect.top + rect.height/2
  }
}
```

**Executing a click:**
```applescript
-- via mcp__Control_your_Mac__osascript:
tell application "Google Chrome" to activate
delay 0.5
do shell script "/opt/homebrew/bin/cliclick c:[screen_x],[screen_y]"
delay 1
```

**Verifying the click worked:** Call `mcp__Control_Chrome__get_page_content` immediately after. Check the expected UI change appears in the text output.

---

## "Show visuals as tables" Protocol (do once per session — Step 0)

This is the critical unlock. Without it, all pages show chart-only text with no numeric data.

1. Use `execute_javascript` to find the View button:
```javascript
var buttons = document.querySelectorAll('button');
for (var i = 0; i < buttons.length; i++) {
  if ((buttons[i].getAttribute('aria-label') || buttons[i].innerText || '').trim() === 'View') {
    var rect = buttons[i].getBoundingClientRect();
    // Returns: top:48, left:1339, centerX:1365, centerY:68
  }
}
```

2. Click View button: `cliclick c:1365,[154+68=222]`

3. Use `execute_javascript` to find "Show visuals as tables (preview)" in the dropdown:
```javascript
var all = document.querySelectorAll('*');
for (var i = 0; i < all.length; i++) {
  if (all[i].innerText && all[i].innerText.indexOf('Show visuals as tables') !== -1) {
    var rect = all[i].getBoundingClientRect();
    // Returns approx: top:271, left:1178
  }
}
```

4. Click it: `cliclick c:[154+271=425],[1178]` (note: x=page_x, y=154+page_y)

5. Verify: `get_page_content` should show "Now showing visuals as tables" at the bottom.

Set `show_visuals_as_tables_enabled: true` in state.yaml.

---
<!-- system:end -->

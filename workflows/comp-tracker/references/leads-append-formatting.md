<!-- system:start -->
# Leads Append — Formatting Protocol (comp-tracker)

Used by step-05 task 5 when appending new rows to the Leads sheet.

**IMPORTANT — Copy row formatting from the last data row:**

New rows must match the formatting of existing data rows (font, borders, fill color, number format). The Excel MCP does not copy formatting automatically when writing cell values — you must explicitly copy it.

**Protocol:**

1. Before writing new rows, identify the last existing data row (the row just above where you will insert). Call it `last_row`.
2. Use `mcp__Excel__By_Anthropic___get_range_values` to read `A{last_row}:D{last_row}` and confirm it is a data row (not a header or summary).
3. After writing each new row's values via `set_cell_value`, copy the formatting from `last_row` to the new row using `osascript` to run an Excel macro:

```applescript
-- Copy formatting from last_row to new_row via AppleScript
tell application "Microsoft Excel"
  set ws to active sheet of active workbook
  set src_range to range ("A" & last_row & ":D" & last_row) of ws
  set dst_range to range ("A" & new_row & ":D" & new_row) of ws
  copy src_range
  paste special destination dst_range with paste paste formats
end tell
```

4. Repeat for each new row appended.
5. Press Escape after the paste operations to clear the clipboard marquee:

```applescript
tell application "Microsoft Excel"
  key code 53  -- Escape
end tell
```
<!-- system:end -->

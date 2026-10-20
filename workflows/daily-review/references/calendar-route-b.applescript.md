<!-- system:start -->
# Calendar Route B (daily-review step-auto)

Fallback when the M365 MCP calendar route fails: pull yesterday's events via AppleScript.

```applescript
   tell application "Calendar"
     set theDate to (current date) - 1 * days
     set startOfDay to theDate - (time of theDate)
     set endOfDay to startOfDay + (23 * hours) + (59 * minutes)
     set output to ""
     repeat with cal in calendars
       repeat with ev in (every event of cal whose start date >= startOfDay and start date <= endOfDay)
         set output to output & (summary of ev) & " | " & (start date of ev as string) & linefeed
       end repeat
     end repeat
     return output
   end tell
   ```
<!-- system:end -->

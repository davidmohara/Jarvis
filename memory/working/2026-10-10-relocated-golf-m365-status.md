# Relocated content: golf-booking M365 calendar backend status

- Origin: workflows/golf-booking/steps/step-06-calendar-block.md (MANDATORY EXECUTION RULES rule 3 and the `calendar_backend` state comment, ~lines 22-27 and 48-53)
- Date: 2026-10-10
- Reason: Phase A cleanup. The dated 2026-09-02 M365 permission_error narrative was stated three times in the step. The workflow file now keeps a single one-line rule ("M365 create is unverified in this environment; stay on the Calendar.app backend"); the detail is preserved here.

## Original text

Rule 3: "This step uses `calendar_backend: Calendar.app` (AppleScript against macOS Calendar.app), not M365. As of 2026-09-02, live testing showed `mcp__claude_ai_Microsoft_365__outlook_create_event` returns a `permission_error` ("This tool is not available") in this environment, so the M365 write path in `calendar-handler` is currently unverified here. Do not switch this step's `calendar_backend` to `M365` without re-testing that the create tool is actually reachable first."

State comment: "calendar_backend: Calendar.app   # explicit, known-working AppleScript path against macOS Calendar.app. The M365 write path exists in calendar-handler for future use, but as of 2026-09-02 the M365 create tool (mcp__claude_ai_Microsoft_365__outlook_create_event) returned a permission_error ("This tool is not available") in testing, so this step stays on Calendar.app until that's resolved."

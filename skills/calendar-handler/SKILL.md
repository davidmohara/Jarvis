---
id: calendar-handler
name: Calendar Handler
owning_agent: rigby
model: sonnet
context: inline
fairness: {applicable: false, reason: "Infrastructure skill for scheduling/calendar operations against one user's own calendar. No differential treatment of people, no eligibility or scoring decision."}
trigger_keywords:
  - conflict check
  - calendar conflict
  - date calculate
  - next weekend
  - calendar block
  - create event
  - book calendar
  - calendar handler
---

<!-- system:start -->
# Calendar Handler

**Callable by:** Any agent or workflow needing calendar-based conflict checks, date math, or
event creation. Currently consumed by `workflows/golf-preview` (conflict-check,
date-calculate) and `workflows/golf-booking` (event-create). Flagged as reusable for any other
scheduling/planning workflow — do not build a second calendar skill; extend this one with a
new `operation` if a workflow needs calendar behavior this skill doesn't yet cover.

## Purpose

Centralizes the three calendar operations that kept getting re-implemented inline in
individual workflow steps: checking a date range for conflicts, calculating a target date from
an offset rule, and creating a calendar event with verification. One skill, one set of
UTC/CT-conversion and verification rules, selected via an `operation` parameter — instead of
each workflow re-deriving its own timezone math or verification logic (and re-introducing the
bugs that math already produced once).

**Backend is caller-selectable, not hardcoded.** Every operation takes a `calendar_backend`
parameter — `"M365"` or `"Calendar.app"` — defaulting to `"M365"` since this org standardizes on
Microsoft 365 for calendar. A caller only needs to pass `calendar_backend` explicitly when it
wants the non-default backend, or when it wants that choice visible in the workflow step file
rather than left implicit; the golf workflows pass it explicitly on every call for that
visibility. Do not silently substitute Google Calendar or any other provider — the only two
supported backends are the two named above.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

All calls take `operation` plus the fields for that operation.

| Field | Required | Applies to | Description |
|-------|----------|-----------|--------------|
| `operation` | Yes | all | One of `conflict-check`, `date-calculate`, `event-create` |
| `calendar_backend` | No | all | `"M365"` or `"Calendar.app"`. Default: `"M365"`. Selects which system the operation reads from or writes to — see the Backends section under each operation below. |
| `date` / `date_range` | Yes for `conflict-check` | conflict-check | A single date or a `{start, end}` range to check |
| `base_date` | Yes for `date-calculate` | date-calculate | The anchor date to calculate from (usually today) |
| `offset_type` | Yes for `date-calculate` | date-calculate | One of `next-weekend`, `current-weekend`, `specific-day` |
| `specific_day` | Yes if `offset_type: specific-day` | date-calculate | Target weekday name, e.g. `"Friday"` |
| `min_days_out` | No | date-calculate | Minimum days from `base_date` the result must satisfy (e.g. a booking-window constraint). Default: none. |
| `title` | Yes for `event-create` | event-create | Event title/summary |
| `time` | Yes for `event-create` | event-create | Start time (and duration, or an explicit end time) |
| `participants` | No | event-create | Attendee names — used as M365 invite attendees on that backend, or folded into the description/body on the Calendar.app backend (AppleScript does not send invites) |
| `description` | No | event-create | Event body/notes |
| `calendar_name` | No | event-create | Which named calendar to create the event on (Calendar.app backend) or which M365 calendar to target (M365 backend). Default: `"Family"` unless the caller specifies otherwise. |

## Output

**conflict-check:**
```yaml
conflicts_found: true | false
events: [{title, start_ct, end_ct}, ...]   # empty list if none
backend_used: "M365" | "Calendar.app"
```

**date-calculate:**
```yaml
target_date: "YYYY-MM-DD"
day_of_week: "<Weekday name>"
days_from_base: <int>
backend_used: "M365" | "Calendar.app"   # accepted for interface consistency — see note in Process below; this operation does no calendar lookup today, so the value is echoed back but does not change behavior
```

**event-create:**
```yaml
event_id: "<identifier or 'unverified' if verification below failed>"
confirmation: "created-and-verified" | "created-unverified" | "failed"
fallback_notified: true | false
backend_used: "M365" | "Calendar.app"
```

## Process

### Operation: conflict-check

**Backends:**

- **`M365` (default):** Pull the calendar for the requested `date` / `date_range` via
  `mcp__claude_ai_Microsoft_365__outlook_calendar_search` (query `""`, `start_datetime` /
  `end_datetime` spanning the full range, start of day to end of day). Events come back in UTC —
  step 2's conversion is mandatory on this backend.
- **`Calendar.app`:** Pull events for the requested `date` / `date_range` via AppleScript
  (`mcp__Desktop_Commander__start_process` running `osascript`) against the named calendar(s)
  in Calendar.app, e.g. `tell application "Calendar" to get events of calendar "{{calendar_name}}"
  whose start date ≥ {{range start}} and start date ≤ {{range end}}`. Calendar.app reports event
  times in the Mac's local timezone already — **skip the UTC→CT conversion (step 2 below)
  entirely on this backend**; converting an already-local time again is the same class of bug
  as skipping the conversion on M365, just inverted. Go straight to step 3 with the times as
  returned.

1. Pull events using the backend above.
2. **On the `M365` backend only: convert every returned event's UTC timestamp to CT before
   doing anything else with it.** This is the single most error-prone step in this skill — a
   raw UTC comparison silently shifts every window by 5-6 hours and can misclassify a
   hard-blocked evening as free, or a free morning as blocked. Subtract 5 hours for CDT
   (roughly April–October) or 6 hours for CST (roughly November–March); if the result crosses
   midnight backward, the event belongs to the previous calendar day.
3. Build a per-day CT timeline: collect events whose CT start or end falls within the day,
   sort by CT start, and map busy blocks as CT ranges.
4. Apply whatever day-specific rules the caller supplied (e.g. "no events before 2:30 PM on
   Sunday," "need a continuous 3-hour gap between 1-6 PM," "flag if a same-day event already
   exists with this title") against the CT timeline, not the raw UTC data.
5. Return `conflicts_found`, the CT-normalized `events` list, and `backend_used`. If the caller
   asked for a gap check rather than a yes/no conflict flag, also return the identified free
   windows in the caller-specified output shape — the return shape above is the minimum, not a
   ceiling.

**Self-check before returning:** do the busy-block times you're about to report look like
plausible daytime hours, or do they look shifted (e.g., a "dinner" block starting at 1 AM)? If
shifted, the UTC→CT conversion was skipped or applied twice — redo it before returning.

### Operation: date-calculate

**Backends:** `date-calculate` is pure weekday arithmetic on `base_date` — it does not query
any calendar system today, on either backend. `calendar_backend` is still accepted as an input
(and echoed back as `backend_used`) purely for interface consistency with the other two
operations, so a caller wiring in `calendar_backend: "Calendar.app"` for a whole workflow
doesn't have to special-case this one operation. If a future version of this skill adds
blackout-date or holiday-calendar awareness to `date-calculate`, that lookup would honor
`calendar_backend` for real; until then, both values produce identical behavior.

1. Get `base_date`. If the caller didn't supply one, use `currentDate` from system context —
   never guess or hardcode a date.
2. Apply `offset_type`:
   - **`next-weekend`**: find the next occurrence of the caller's target day(s) that is at
     least `min_days_out` days from `base_date` (if `min_days_out` given). Compute
     `days_until_target = (target_weekday_index - base_weekday_index) % 7`; if that lands
     before `min_days_out`, add 7 and recompute until the constraint is satisfied.
   - **`current-weekend`**: same math without the forward-skip — return the nearest occurrence
     even if it's fewer than `min_days_out` out, but flag `days_from_base` clearly so the
     caller can decide if it's still viable.
   - **`specific-day`**: find the next occurrence of `specific_day` from `base_date`, applying
     `min_days_out` the same way as `next-weekend` if supplied.
3. Validate before returning: confirm `target_date`'s actual weekday matches what was asked
   for, and confirm `days_from_base` satisfies `min_days_out` if one was given. If either check
   fails, recalculate — do not return an unvalidated date. This validation exists because a
   wrong date here is silent and expensive: it propagates into every downstream conflict check
   and, if this is feeding a booking workflow, into a real irreversible booking attempt against
   the wrong day.
4. Return `target_date`, `day_of_week`, `days_from_base`, `backend_used`.

### Operation: event-create

**Backends:**

- **`M365` (default):** Create the event via `mcp__claude_ai_Microsoft_365__outlook_create_event`
  — pass `title`, start/end from `time`, `description`, `participants` as invite attendees, and
  `calendar_name` if the connector supports targeting a non-default calendar. This writes a real
  M365/Outlook event, which is the org standard and (unlike the Calendar.app path) actually
  sends invites to `participants` rather than just naming them in the body.
- **`Calendar.app`:** Go through AppleScript against macOS Calendar.app, as documented in steps
  2-3 below. Use this backend when the caller specifically needs a local-machine calendar block
  instead of an M365 event — e.g. no Outlook calendar exists for the target use case, or the
  workflow was built before reliable M365 create was available and hasn't been migrated yet.

1. Resolve `calendar_backend` (default `"M365"`) before doing anything else, and route to the
   matching backend below. Do not mix backends mid-operation.

   **M365 path:**
   a. Call `mcp__claude_ai_Microsoft_365__outlook_create_event` with the mapped fields.
   b. **Verify immediately — do not report success on the create call alone.** Re-query the
      event via `mcp__claude_ai_Microsoft_365__outlook_calendar_search` for the same time window
      and confirm an event with matching `title` and start time comes back. A create call
      returning without error is not the same as a confirmed event.
   c. **If verified:** return `confirmation: "created-and-verified"`, `event_id` set to the
      M365 event id from the create/search response, `fallback_notified: false`,
      `backend_used: "M365"`.
   d. **If verification fails or the call errors:** do not assume success — go to step 2 below
      (fallback), with `backend_used: "M365"`.

   **Calendar.app path:**
   a. Build the AppleScript:
      ```applescript
      tell application "Calendar"
        tell calendar "{{calendar_name}}"
          set newEvent to make new event with properties {summary:"{{title}}", start date:date "{{start}}", end date:date "{{end}}", location:"{{location if given}}", description:"{{description}} · {{participants joined}}"}
        end tell
      end tell
      ```
      Run via `mcp__Desktop_Commander__start_process` with `osascript`. This path does not send
      M365 invites — `participants` is folded into the description text only.
   b. **Verify immediately — do not report success on the create call alone.** Query the target
      calendar for the newly created event (e.g. `count of events` / `last event` on
      `calendar_name`, checking `summary` matches `title`). An AppleScript call returning
      without error is not the same as a confirmed event; timeouts and silent no-ops both look
      like success from the create call's return value alone.
   c. **If verified:** return `confirmation: "created-and-verified"`, `event_id` set to whatever
      identifier is available (Calendar.app event id if retrievable, otherwise the title+start
      time as a human-readable identifier), `fallback_notified: false`, `backend_used:
      "Calendar.app"`.
   d. **If verification fails or the AppleScript errors/times out:** go to step 2 below
      (fallback), with `backend_used: "Calendar.app"`.

2. **Fallback (either backend):** do not assume success. Run the caller's fallback notification
   (e.g. a Slack message with manual add-it-yourself instructions) — this skill does not invent
   a fallback path if the caller didn't specify one; ask the caller for one at build time rather
   than silently skipping notification. Return `confirmation: "created-unverified"` or
   `"failed"`, `fallback_notified: true`, `backend_used` set to whichever backend was attempted.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`, do not run any
side-effect tools for the `event-create` operation (no `outlook_create_event` call on the M365
backend, no AppleScript execution against Calendar.app on that backend). Instead, produce a
markdown plan describing the create call(s) you would issue for the resolved `calendar_backend`,
in order, with rationale and the inputs you would pass to each. Save the plan to the requested
output path and stop. Do not call either backend's create mechanism under any circumstances in
this mode. `conflict-check` and `date-calculate` are read-only and are not gated by this mode —
they may still execute normally, against whichever `calendar_backend` was specified, to support
planning.

## Error Handling

| Situation | Response |
|-----------|----------|
| Calendar API/AppleScript unreachable for `conflict-check` (either backend) | Do not silently return `conflicts_found: false`. Return an explicit `calendar_unavailable: true` flag alongside an empty `events` list and `backend_used` so the caller can decide whether to proceed cautiously or block. |
| `date-calculate` produces a date that fails its own validation 3+ times | Abort. Do not guess. Report to the caller that date calculation needs a human look. (`calendar_backend` is irrelevant to this failure mode — see backend note under that operation.) |
| `event-create` targets a calendar that doesn't exist (M365 calendar name invalid, or Calendar.app calendar missing) | Treat as a verification failure — run the fallback notification path, do not attempt to auto-create the calendar, on either backend. |
| Caller passes `calendar_backend` value other than `"M365"` or `"Calendar.app"` | Ask the caller to clarify rather than guessing or silently defaulting — an unrecognized backend is treated the same as an ambiguous `offset_type`, below. |
| Ambiguous `offset_type` value not in the documented set | Ask the caller to clarify rather than guessing which of the three operations was meant. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/calendar-handler-latest.json
```

Content:
```json
{
  "skill": "calendar-handler",
  "agent": "<caller's agent, e.g. sterling>",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output (e.g. `event-create` fell back to notification instead of a verified event), `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill calendar-handler
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/calendar-handler.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

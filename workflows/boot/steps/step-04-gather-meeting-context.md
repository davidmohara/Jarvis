---
status: complete
started-at: "2026-09-03T15:14:00Z"
completed-at: "2026-09-03T15:17:00Z"
outputs:
  meetings_found: "24 events (Sep 2-7) with full context — calendar-unified.json provides all attendees, locations, times; cross-checked against live Clay getEvents this run"
  meeting-context: "Today (Thu Sep 3): Sales & Recruiting Meeting 9:15-9:30am CDT (recurring, tentative) and Sales Scrum 9:30-10am (recurring, tentative) — recurring-skip, no prep needed; David/Robyn 1:1 10:00-10:30am — standing 1:1, no client/deal-specific prep beyond usual cadence, delegation tracker clean (no open items tied to Robyn); Drive To 12:30-1:00pm; Podcast Filming (MarketScale) 1:00-3:00pm with guest Michael Slater, Janine Jeanson and Kristin Johnson producing — guest-episode prep may be useful given no prior notes found; Drive From 3:00-3:30pm; Meet with Steve 4:30-5:30pm — no attendee list/context on the invite, low-context. No client or partner meetings today. Yesterday's daily review not found (last dated review on file: auto-2026-08-12.md — this gap is long-standing, not new)."
  clay-reminders: "available this run — 0 reminders returned (getUpcomingReminders)"
  clay-birthdays: "available this run — no birthday-specific entries found in Clay getEvents for the next 7 days (Sep 3-10); 0 to report"
  context-status: "ready — sufficient calendar and meeting-prep data for briefing synthesis. Clay available and cross-verified against calendar-unified.json; no data gaps this run."
---

<!-- system:start -->
# Step 04: Gather Meeting Context (Phase 3)

## MANDATORY EXECUTION RULES

1. You MUST run morning briefing step-03 before proceeding. Do not synthesize the briefing without meeting context.
2. You MUST check Clay for reminders and birthdays. This is not optional — it is a standing controller requirement.
3. Do NOT proceed to step-05 until both tasks are complete.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Calendar data from step-02 (morning briefing steps 01-02), Clay MCP
**Output:** Meeting prep context and Clay reminders/birthdays added to accumulated-context

---

## CONTEXT BOUNDARIES

- Morning briefing step-03 covers meeting-specific context (attendee research, prep flags). Run it as written.
- Clay check covers the next 7 days only. Do not pull beyond that range.
- Do not surface Clay data to the controller yet — it will be incorporated into the briefing in step-05.

---

## YOUR TASK

1. **Run morning briefing step-03.**
   Read and follow `workflows/morning-briefing/steps/step-03-*.md` in full. This step gathers meeting prep context for flagged meetings identified in steps 01-02.

2. **Check Clay for the next 7 days:**
   - Pull upcoming reminders via Clay MCP
   - Pull upcoming birthdays via Clay MCP (filter: upcoming_birthday, next 7 days)
   - Capture: name, date, relationship context, any associated notes

3. **Record results in accumulated-context:**
   ```yaml
   accumulated-context:
     phase3:
       morning-briefing-step-03: completed | nothing-to-surface | failed — [reason]
       clay-reminders: [list or "none"]
       clay-birthdays: [list or "none"]
   ```

4. **Update step frontmatter:** Set `status: complete`, `completed-at` with current timestamp, and `outputs.meetings_found` with a summary (e.g. "N events with full context — morning briefing step-03 completed, Clay data pulled").

5. **Update state.yaml:** Set `current-step: step-05-synthesize-briefing.md`.

---

## SUCCESS METRICS

- Morning briefing step-03 executed as written
- Clay reminders pulled (or absence confirmed)
- Clay birthdays pulled (or absence confirmed)
- All findings recorded in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Morning briefing step-03 file missing | Note the failure. Proceed without meeting-specific prep context. Surface in briefing: "Meeting prep context unavailable." |
| Clay MCP unavailable | Record: "Clay unavailable." Note in briefing that reminders and birthdays could not be checked. |
| Clay returns no results | Record: "Clay: nothing to surface." This is a valid outcome. |

---

## NEXT STEP

Read fully and follow: `step-05-synthesize-briefing.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

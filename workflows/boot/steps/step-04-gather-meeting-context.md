---
status: complete
started-at: "2026-08-31T14:52:00Z"
completed-at: "2026-08-31T14:56:00Z"
outputs:
  meetings_found: "45 events (Aug 31-Sep 3) with full context — calendar-unified.json provides all attendees, locations, times; cross-checked against live Clay getEvents this run"
  meeting-context: "Today (Mon Aug 31): Hot 26 yoga this morning (done), Improving Prayer Call, Timesheet, Sales & Recruiting Meeting, Sales Scrum back-to-back at 9:15-10am CDT, Build plan for SC block 10am-11am CDT, Monday Week Overview with Alice at 2pm CDT (weekly recap), Exec AI Cohort Planning with Susan/Devlin at 3:30pm CDT (redesigning exec AI training, next cohort Ashok/Amber/Asrai), and Dallas Come Together Escape Rooms this evening (5:15-8pm CDT, large company social). Notable upcoming this week: Sep 2 is the heaviest day — external breakfast with Luke Rutledge (HCHB) at Ida Claire, Dallas Executive Huddle, AI Leaders Weekly, personal Dr Nathan Walters appointment, Improving Edge podcast topic discussion, YPO yDeep Dive, haircut, Scoping the Next Phase call with Systemic Compliance (Matt joining in person per rgraham's email — ties directly to the inbox item), and evening Cigars with the Stars social. Sep 1 and Sep 3 both have Podcast Filming sessions at MarketScale plus the recurring Sales & Recruiting/Sales Scrum meetings and 1:1s (Tim on Sep 1, Robyn on Sep 3)."
  clay-reminders: "available this run — 0 reminders returned (getUpcomingReminders)"
  clay-birthdays: "available this run — no birthday-specific entries found in Clay getEvents for the next 7 days; 0 to report"
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

---
status: complete
started-at: "2026-09-16T14:27:30Z"
completed-at: "2026-09-16T14:29:00Z"
outputs:
  meetings_found: "Today (Wed Sep 16): AR YPO travel day to Little Rock. Flight AA3850 DFW->LIT dep 7:10am CT / arr 8:34am CT (conf GZCLNF, First). Capital Hotel check-in. Regus day office Little Rock booked 9:00am-12:00pm CT. AR YPO Dinner, Little Rock 6:00-9:00pm CT. Dallas recurring meetings still on the calendar as 'tentative' and will be missed in person: Dallas Executive Huddle 8:30am, Sales & Recruiting 9:15am, AI Leaders Weekly 9:30am, Sales Scrum 9:30am, Microsoft Partner GTM 10:00am, AI Takeoff Weekly Touch 10:00am, David/Robyn 1:1 10:30am, GEHC AI Routing weekly sync 10:30am, US Town Hall 12:00pm, GEHC Twice Weekly Internal 3:30pm, Overflow 5:00pm."
  meeting-context: "Delegation tracker clean (0 active delegations). Q3 rocks (memory/personal/quarterly-objectives.md) still status 'Q3 draft — pending David's review', last-updated 2026-07-30 (~7 weeks unsigned; 4 rocks: Revenue Visibility, Partner & Account Review Execution, Thought Leadership, Partner Co-Sell Pipeline). Daily review gap: last daily review on file is memory/episodic/daily-review-2026-08-13-000000.md; reviews/daily/ holds only auto-*.md through 2026-08-12 — over a month with no daily review, recurring accountability gap. Identity/MEMORY.md checked: Robyn Fuentes (President Houston, key focus) on the 10:30 1:1; Devlin Liles across AI Leaders/StrongTie threads; YPO is a standing personal commitment. No identity-level notes for Court Westcott / Kevin Gardner / Justin Etheredge beyond Clay records."
  clay-reminders: "none — 0 due in next 7 days (data/clay-reminders-unified.json)"
  clay-birthdays: "3 in next 7 days (data/clay-reminders-unified.json): COURT WESTCOTT today 09-16 (Dallas family office, tech/RE/subscription, angel AR focus), Kevin Gardner 09-20, Justin Etheredge 09-22."
  context-status: "degraded — calendar and Clay fresh; OmniFocus unavailable (no task-level context this run); identity/MEMORY.md read directly for attendee context."
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

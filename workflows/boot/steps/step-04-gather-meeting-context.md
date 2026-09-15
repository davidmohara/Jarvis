---
status: complete
started-at: "2026-09-14T16:22:00Z"
completed-at: "2026-09-14T16:26:00Z"
outputs:
  meetings_found: "Today (Mon Sep 14): full Dallas day — Prayer Call, Sales & Recruiting, Sales Scrum (recurring-skip), Devlin sync/Overflow/AI Executive Workshop CA sync back-to-back 11:30am-1pm CT (zero buffer), Summer/craiggroup.io call 2pm CT (low-context), GEHC Twice Weekly Internal Check-In 3:30pm CT, FEI Monthly evening event at The Clubs of Prestonwood."
  meeting-context: "Delegation tracker clean (0 active delegations). Q3 rocks status unchanged: still in draft (Revenue Visibility, Partner/Account Review Execution, Thought Leadership, Partner Co-Sell Pipeline). Yesterday's (09-13) daily review missing — last dated review on file remains auto-2026-08-12, flagged again as accountability gap (>1 month). Back-to-back flag: Devlin sync -> Overflow -> AI Workshop CA sync, zero buffer 11:30am-1pm."
  clay-reminders: "none — 0 due in next 7 days (data/clay-reminders-unified.json)"
  clay-birthdays: "none surfaced — no dedicated birthday tool in current Clay toolset"
  context-status: "degraded — calendar and Clay fresh; identity/MEMORY.md checked directly for attendee context, no relevant hits found for Summer/craiggroup.io or Saxum/rstone."
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

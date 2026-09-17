---
status: complete
started-at: "2026-09-17T16:13:00Z"
completed-at: "2026-09-17T16:15:00Z"
outputs:
  meetings_found: "Today (Thu Sep 17): return travel day from Little Rock. Flight AA3589 LIT->DFW dep 7:18am CT / arr ~8:50am CT (conf GZCLNF). Sales & Recruiting 9:15-9:30am CT (tentative). Sales Scrum 10:00-10:30am CT (tentative) overlapping GEHC AI Routing weekly sync 10:00-10:30am CT (busy). Finish Vegas prep 10:30-11:30am CT. Retreat prep 1:00-2:00pm CT. Steve Hall follow up 3:00-3:30pm CT (tentative) overlapping Golf lesson 3:00-4:00pm CT. YPO Spouse Kickoff Party 6:00-9:00pm CT."
  attendees_enriched: "GEHC AI Routing sync: Justin Holder (GEHC), Lisa Barnes / Lisa Kimbrel (Improving). Sales Scrum: Stephen Johnson, Devlin Liles, Robyn Fuentes (President Houston), Juan Bernal. Sales & Recruiting: Don McGreal, Diana Stevens, Tim Rayburn, Blake McMillan. Steve Hall follow up: Derek Nwamadi + Anthony Marrical. 25 total unique attendees across the 4-day window."
  prep_materials: "none required — GEHC AI Routing sync is a standing weekly client touch, not a new-prep meeting; rest of the day is internal cadence or personal blocks on a return-travel day."
  meeting-context: "GEHC AI Routing weekly sync is the only client/partner meeting today (GE Healthcare engagement). Delegation tracker clean (0 active delegations). Q3 rocks (memory/personal/quarterly-objectives.md) still 'Q3 draft — pending David's review', last-updated 2026-07-30 (~7 weeks unsigned; 4 rocks: Revenue Visibility, Partner & Account Review Execution, Thought Leadership, Partner Co-Sell Pipeline). Daily review gap: latest review on file is reviews/daily/2026-09-02.md (15 days ago); episodic daily-review entries stop at 2026-08-13 — recurring accountability gap. Identity/MEMORY.md: Robyn Fuentes (President Houston, key focus) on Sales Scrum; Devlin Liles across AI threads; YPO is a standing personal commitment."
  clay-reminders: "none — 0 due in next 7 days (data/clay-reminders-unified.json)"
  clay-birthdays: "2 in next 7 days (data/clay-reminders-unified.json): Kevin Gardner 2026-09-20, Justin Etheredge 2026-09-22."
  context-status: "healthy — calendar, OmniFocus, email, and Clay all live this run; 0 degraded sources."
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

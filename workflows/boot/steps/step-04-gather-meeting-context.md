---
status: complete
started-at: "2026-08-28T14:02:30Z"
completed-at: "2026-08-28T14:04:00Z"
outputs:
  meetings_found: "20 events (Aug 28-31) with full context — calendar-unified.json provides all attendees, locations, times"
  meeting-context: "Real prep items today: (1) SOW review for Dickason Honda of Paris (15:30-16:00 CDT w/ Derek Nwamadi, Anthony Marrical, client contact stevehall11565@gmail.com) — client SOW discussion, have the draft SOW ready; (2) Sync: David/Matt/Robin (17:30-18:00 CDT w/ Systemic Compliance contacts rgraham/myasar/kgraham + Ben Kennedy) — recurring external sync, no new prep flagged; (3) Executive AI Training Program Session 7/8 Wrap-Up (18:00-20:00 CDT, in-person Dallas Conference Room Trust) — final session, may warrant a close-out note. Standing internal meetings (Coffee Chat, Sales & Recruiting, 4th Friday Exec, Presidents Pipeline Roundtable) need no additional prep. Flag: David is on the tail end of the LSG Board Retreat (Malakoff, TX, ends ~12pm CDT) while also double-booked into 6 internal/client Improving meetings between 8am-3pm CDT today — same overlap pattern flagged yesterday, now compounding with a drive back from Malakoff. 'Meet Susie' at 4-5pm CDT (NorthPark Center) has no attendee record — personal, unclear who Susie is; flagging for awareness only."
  clay-reminders: "unavailable — Clay MCP requires interactive OAuth, could not be completed this session"
  clay-birthdays: "unavailable — same Clay auth gap; birthday data not confirmed for the next 7 days"
  context-status: "ready — sufficient calendar and meeting-prep data for briefing synthesis. Clay data unavailable this run (auth), flagged rather than presented as current."
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

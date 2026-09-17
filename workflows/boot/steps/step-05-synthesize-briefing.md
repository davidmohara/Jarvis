---
status: complete
started-at: "2026-09-17T16:15:00Z"
completed-at: "2026-09-17T16:17:00Z"
outputs:
  briefing_delivered: "yes — full morning briefing synthesized (0 degraded sources) and carried forward through steps 06-08 for verbatim delivery to controller"
  briefing_sections: "narrative (3 paragraphs), Today's Calendar table, double-book warning line, closing prompt"
  today_summary: "Thursday, September 17, 2026 — return travel day from Little Rock; GEHC AI Routing sync is the only client meeting; personal retreat prep for tomorrow"
  action_items: "Attend GEHC AI Routing sync (10am); clear AI for Execs handoff to Blake McMillan (due tomorrow); reply to Opal Group THWET; complete YPO nominee intake forms; decide GEHC vs Sales Scrum 10am overlap and Steve Hall vs golf 3pm overlap"
  format: "3-paragraph prose narrative (no em-dashes) + Today's Calendar table. Watchtower section omitted (no daily watchtower run today). Reminders section omitted (0 due). Clay birthdays folded into paragraph 3."
  calendar_today: "9 distinct today-events, live from data/calendar-unified.json. Return travel LIT->DFW; two double-books (10am GEHC/Sales Scrum, 3pm Steve Hall/golf); YPO Spouse Kickoff 6pm."
  hotspots: "0 degraded data sources this run (OmniFocus recovered, 42 tasks); 5 tasks due tomorrow incl. AI for Execs handoff; Opal Group reply owed; YPO Western US nominee intake forms deadline; Q3 rocks unsigned ~7 weeks; daily review 15 days stale (last 09-02); two double-books today."
---

<!-- system:start -->
# Step 05: Synthesize Briefing (Phase 4)

## MANDATORY EXECUTION RULES

1. You MUST run morning briefing step-04 as written. This step handles briefing synthesis — do not replace it with an ad-hoc summary.
2. You MUST incorporate all Phase 2 task findings into the briefing. Data gathered in step-02 is not optional input.
3. Do NOT proceed to step-06 until the briefing is delivered to the controller.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** All accumulated-context from steps 01-04
**Output:** Completed morning briefing delivered to the controller

---

## CONTEXT BOUNDARIES

- Morning briefing step-04 owns the format and synthesis logic. Follow it as written.
- Phase 2 findings (lead review, 72-hour look-ahead, email triage, Jarvis inbox) must be woven into the briefing — not appended as raw data.
- Any tasks that failed in step-02 must appear in the briefing as degraded data flags, not silently omitted.

---

## YOUR TASK

1. **Run morning briefing step-04.**
   Read and follow `workflows/morning-briefing/steps/step-04-*.md` in full. Provide it with the full accumulated-context as input so all gathered data is incorporated into the briefing.

2. **Ensure Phase 2 findings are incorporated:**
   - Lead review findings (Task F) — surface any unassigned or actionable leads
   - 72-hour look-ahead (Task G) — include the next 3 days of notable meetings
   - Email triage (Task H) — surface any flagged or time-sensitive messages
   - Jarvis inbox (Task I) — surface any items requiring attention
   - Clay reminders and birthdays from step-04 — include in the briefing

3. **Flag any degraded data** — if a Phase 2 task failed, note it in the briefing:
   > ⚠️ [Task name] unavailable — data not included.

4. **Hold the finished briefing** — this step runs inside the subagent Master spawned for steps 2-12 (see `workflow.md` EXECUTION section), so "deliver to the controller" here means: carry the complete, verbatim briefing text forward through steps 06-08, then include it in full in this subagent's final message. Master relays it to the controller unabridged — it is the primary output of the entire boot sequence. Do not stop early to message the controller directly; continue to step-06.

5. **Update step frontmatter:** Set `status: complete`, `completed-at` with current timestamp, and `outputs.briefing_delivered` with a summary (e.g. "yes — morning briefing synthesized and surfaced to controller").

6. **Update state.yaml:** Set `current-step: step-06-scan-workflows.md`.

---

## SUCCESS METRICS

- Morning briefing step-04 executed as written
- All Phase 2 task findings incorporated (or their absence flagged)
- Briefing delivered to the controller
- No data silently omitted

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Morning briefing step-04 file missing | Synthesize the briefing directly from accumulated-context using standard briefing format (calendar, tasks, leads, email, look-ahead, Clay). Note: "Step-04 template unavailable — using raw synthesis." |
| No accumulated-context available | Surface what is available. Flag each missing data source explicitly. Do not deliver an empty briefing — deliver a degraded one with clear flags. |

---

## NEXT STEP

Read fully and follow: `step-06-scan-workflows.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

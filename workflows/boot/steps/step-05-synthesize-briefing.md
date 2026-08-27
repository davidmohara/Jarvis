---
status: complete
started-at: "2026-08-27T16:39:30Z"
completed-at: "2026-08-27T16:45:30Z"
outputs:
  briefing_delivered: "yes — morning briefing synthesized and carried forward through steps 06-08 for verbatim delivery to controller"
  format: "3-paragraph narrative + calendar table (accumulated data: 20 calendar events Aug 27-30, 12 uncompleted OmniFocus inbox items, 3 actionable emails, 0 due reminders, 0 active delegations)"
  calendar_today: "conflicted — board retreat (Malakoff, TX) overlapping 5 internal Improving meetings, 3 of which overlap each other (11:30am-1:15pm CDT block)"
  hotspots: "SPARC CRM deadline 8/31 (5 opportunities), Inertia Labs partnership pitch awaiting response, scheduling conflict between LSG board retreat and internal calls, missing yesterday's daily review"
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

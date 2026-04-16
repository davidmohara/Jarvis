---
model: opus
---

<!-- system:start -->
# Step 04: Deliver Materials and Harper Handoff

## MANDATORY EXECUTION RULES

1. You MUST deliver the prep materials document before initiating any Harper handoff.
2. If `presentation_needed = true`, you MUST trigger the Quinn → Harper handoff with strategic narrative, metrics, and talking points.
3. The Harper handoff MUST use the cross-agent handoff contract from shared-definitions.md.
4. If `presentation_needed = false`, skip Harper handoff and close the workflow.
5. Data conflicts MUST be visible in the delivered materials — never hide them.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `event_context` from step 01, `leadership_materials` from step 03
**Output:** Delivered prep document + Harper handoff (if applicable)

---

## YOUR TASK

### Sequence

1. **Deliver the prep document.**

   Format:

   ---
   **[Event Name] — Leadership Prep**
   Event: [type] | Date: [date] | Audience: [audience]
   Prepared by Quinn | [prep date]

   ---
   **Strategic Narrative**
   [3-5 sentence narrative from step 03]

   ---
   **Key Metrics**
   | Metric | Value | vs. Target | Trend |
   |--------|-------|------------|-------|
   [rows from step 03]
   [If any data unavailable: "⚠ [Domain] data unavailable — metric may be incomplete"]

   ---
   **Initiative Updates**
   [grouped: Completed | Active | At-Risk/Blocked]
   [conflict note inline where applicable]

   ---
   **Risk Register**
   | Risk | Probability | Impact | Mitigation |
   |------|-------------|--------|------------|
   [rows from step 03, including conflict notes as risk items]

   ---
   **Talking Points**
   1. **[Topic]** — [Key message]
      Data: [supporting data]
      Likely question: [question]
      Response: [prepared response]
   [repeat]

   ---

2. **Check if Harper handoff is needed.**
   - `presentation_needed = true` → proceed with Harper handoff
   - `presentation_needed = false` → skip to step 3

3. **Trigger Harper handoff (if needed).**
   - Build handoff context per cross-agent handoff contract:
   ```yaml
   handoff:
     from: quinn
     to: harper
     reason: "Leadership prep requires a formatted presentation deck"
     original-request: "Executive requested [event_name] prep materials"
     work-completed: "Strategic narrative, metrics, initiative updates, risk register, and talking points prepared."
     context:
       initiative-name: "[event_name]"
       prep-type: "[event_type]"
       event-date: "[event_date]"
       audience: "[audience]"
       key-messages: [talking point key messages]
     required-action: "Build a polished presentation deck from the strategic narrative, key metrics, and talking points provided. Format for [audience]."
   ```
   - Pass `leadership_materials` content to Harper
   - Confirm handoff initiated

4. **Close the workflow.**
   - If Harper handoff triggered: "Prep materials delivered. Harper has been given the content to build your [event_name] deck."
   - If no Harper handoff: "Prep materials delivered. [event_name] is on [date]. You are ready."

---

## OUTPUT FORMAT RULES

- Lead with the strategic narrative — it sets the tone for everything that follows
- Metrics table must flag data gaps inline — no silent omissions
- Risk register must be scannable — one line per risk
- Talking points must be usable as-is — the executive should be able to read them aloud
- Harper handoff confirmation tells the executive what happens next

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Harper unavailable for handoff | Deliver materials as document. Note: "Harper is unavailable — presentation deck cannot be created automatically. Materials are ready for manual formatting." |
| Presentation needed but no talking points generated | Do not trigger Harper handoff without talking points. Generate at minimum 3 talking points first, then hand off. |
| Executive requests deck for town hall (no board meeting default) | `presentation_needed = true`. Trigger Harper handoff as requested. |

---

## WORKFLOW COMPLETE

Leadership prep materials delivered. Harper handoff triggered if applicable.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Action Report

## MANDATORY EXECUTION RULES

1. You MUST produce a single, structured pipeline report. No raw data dumps.
2. You MUST identify the top 5 priority deals by impact — not by size alone. Impact = size x probability of movement this week.
3. You MUST end with "This week's revenue priority" — the single deal that moves the needle most.
4. You MUST include handoff routing for any deals that need cross-agent support.
5. Do NOT soften bad news. If the pipeline is weak, the report says the pipeline is weak.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Pipeline data from step 01, health analysis from step 02, risk flags from step 03
**Output:** Complete pipeline review report delivered to the controller

---

## CONTEXT BOUNDARIES

- This is a weekly operating document. It should take under 3 minutes to read and immediately tell the controller where to focus.
- Priority deals are ranked by actionability this week, not lifetime value.
- Handoff recommendations are suggestions — the controller decides routing.
- The report format is fixed. Do not improvise sections or reorder.

---

## YOUR TASK

### Sequence

1. **Build the Pipeline Summary section:**
   ```
   ## Pipeline Summary — YYYY-MM-DD

   | Metric | Value |
   |--------|-------|
   | Active deals | N |
   | Total pipeline | $X |
   | Weighted pipeline | $X |
   | Quarterly target remaining | $X |
   | Coverage ratio | X.Xx (rating) |
   | Average deal velocity | N days/stage |
   | Stale deals (14+ days) | N ($X at risk) |
   | Funnel shape | healthy / top-heavy / bottom-heavy / constipated |
   ```

2. **Build the Priority Deals section:**
   - Select the top 5 deals by impact this week
   - Impact criteria: deal size, stage advancement likelihood, upcoming meeting scheduled, risk that can be mitigated with action
   - For each:
     ```
     ### [Deal Name] — [Account]
     - Stage: X | Amount: $X | Weighted: $X
     - Days in stage: N | Last activity: YYYY-MM-DD
     - Next step: [defined step or "NONE — define this"]
     - This week: [specific action to take this week]
     ```

3. **Build the Risk Flags section:**
   - Group by risk category
   - For each flagged deal: one-line summary with the recommended action
   - Format:
     ```
     ## Risk Flags

     **No Activity (14+ days):** N deals, $X at risk
     - [Deal] — N days inactive. Action: [specific action]

     **No Next Step:** N deals
     - [Deal] — Stage: X. Action: [define next step]

     **No Buyer Access:** N deals, $X at risk
     - [Deal] — Stage: X. Action: [get to the buyer]

     **Stage Concentration:** [stage] holds X% of pipeline
     - Action: [unblock or qualify out]

     **Stuck Deals (2x avg):** N deals
     - [Deal] — N days in [stage] (avg: N). Action: [unstick it]
     ```

4. **Build the Advance / Kill / Escalate section:**
   - **Advance:** Deals ready to move to the next stage with specific trigger
   - **Kill:** Deals recommended for closure with reasoning
   - **Escalate:** Deals needing executive engagement, additional resources, or strategic decision
   - Format:
     ```
     ## Advance / Kill / Escalate

     **Advance:**
     - [Deal] — Move from [stage] to [stage]. Trigger: [what makes this ready]

     **Kill:**
     - [Deal] — [reason]. In pipeline N days. Recommend closing out.

     **Escalate:**
     - [Deal] — Needs [what]. Route to [who].
     ```

5. **Build the Upcoming Client Meetings section:**
   - List client meetings in the next 7 days with deal context
   - For each:
     ```
     - [Date] [Time] — [Meeting subject]
       - Account: [account] | Deal: [linked deal or "no active deal"]
       - Context: [one-line from recent notes or deal status]
       - Prep needed: yes/no
     ```

6. **Write "This Week's Revenue Priority":**
   - The single deal that the controller should focus energy on this week
   - Why this deal, why this week, and the one action that matters
   - Format:
     ```
     ## This Week's Revenue Priority

     **[Deal Name]** — $X at [stage]

     Why: [2-3 sentences on why this deal, why now]
     Action: [the one thing to do this week]
     ```

7. **Determine handoff routing:**
   - Client meeting needs full prep → route to `client-meeting-prep` workflow
   - Deal needs executive engagement → flag for Shep (people & leadership agent)
   - Revenue rock at risk based on coverage → escalate to Quinn (strategy agent)
   - Format:
     ```
     ## Handoffs

     | Deal/Item | Route To | Reason |
     |-----------|----------|--------|
     | [deal/meeting] | [agent/workflow] | [why] |
     ```

8. **Deliver the complete report** to the controller.

---

## SUCCESS METRICS

- Single-document report that answers: "How's the pipeline and where do I focus?"
- Top 5 priority deals identified with specific this-week actions
- Every risk flag paired with a recommended action
- Kill candidates explicitly named
- Handoff routing clear for cross-agent needs
- "This week's revenue priority" named with reasoning

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Insufficient data for meaningful analysis | Deliver what you have. Note data gaps explicitly: "The following sections are based on incomplete data: [list]." |
| All deals are healthy (no risks) | Report it. Note: "No risk flags this week. Pipeline is clean. Focus: advancing priority deals and adding new pipeline." |
| Too many deals to cover individually | Summarize by category. Only detail the top 5 and flagged deals individually. |
| Revenue target already met | Report it as a win. Shift focus to: "Target met. Focus: building next quarter's pipeline." |

---

## WORKFLOW COMPLETE

**Before returning the pipeline report to the controller**, write `state.yaml` in the workflow directory with `status: complete` and `current-step: step-04`.

```yaml
workflow: pipeline-review
agent: chase
status: complete
current-step: step-04
```

### Handoff Rules

| Condition | Route To | Action |
|-----------|----------|--------|
| Client meeting needs prep | `client-meeting-prep` workflow | Chase runs client meeting prep for the flagged meeting |
| Deal needs executive engagement | Shep (People & Leadership) | Flag the deal and the ask — Shep advises on relationship play |
| Revenue rock at risk (coverage < 2x) | Quinn (Strategy) | Escalate pipeline gap — Quinn assesses rock status and recommends adjustment |
| Deal requires proposal or deck | Harper (Communications) | Route content request with deal context and audience |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

# Step 03: Risk Flags

## MANDATORY EXECUTION RULES

1. You MUST evaluate every active deal against all five risk categories. No exceptions.
2. You MUST provide a specific recommended action for every flagged deal. "Keep an eye on it" is not an action.
3. You MUST flag deals that should be killed. Zombie deals waste mindshare and inflate coverage ratios.
4. Do NOT rank risks in this step. Prioritization happens in step 04.
5. Do NOT hold back. If a deal looks dead, say it looks dead.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Pipeline data from step 01, health analysis from step 02
**Output:** Risk flags with recommended actions stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Every risk flag must include: what's wrong, why it matters, and what to do about it.
- Risk categories are not mutually exclusive. A deal can (and often will) have multiple flags.
- "No relationship with economic buyer" means the controller or their team has no documented interaction with the person who signs the check. CRM contact records and meeting history are the evidence.
- Use the controller's upcoming calendar to identify opportunities to address risks in already-scheduled meetings.

---

## YOUR TASK

### Sequence

1. **Flag: No activity in 14+ days.**
   - For each deal with last activity > 14 days ago:
     - Deal name, stage, amount, days since last activity
     - Recommended action: specific outreach (email, call, meeting request) with suggested talking point
     - If last activity was 30+ days ago: recommend kill review — this deal may be dead

2. **Flag: No defined next step.**
   - For each deal where CRM next step is empty, vague, or clearly outdated:
     - Deal name, stage, amount
     - Recommended action: define a concrete next step with a date
     - If the deal is in a late stage (Proposal+) with no next step: escalate — late-stage deals without momentum stall and die

3. **Flag: No relationship with economic buyer.**
   - For each deal where the controller's team has no documented interaction with the person who controls budget:
     - Deal name, stage, amount, known contacts vs. who's missing
     - Recommended action: specific play to get access (ask champion for intro, propose executive alignment meeting, attend with a senior leader)
     - If the deal is in Proposal+ without buyer access: critical risk — deals close from the top, not the middle

4. **Flag: Stage concentration (pipeline constipation).**
   - If any single stage holds > 40% of total pipeline value:
     - Which stage, how many deals, total value
     - Recommended action: depends on which stage
       - Early stage concentration: qualification blitz — advance or disqualify
       - Mid stage concentration: identify what's blocking progression
       - Late stage concentration: close harder or acknowledge slippage

5. **Flag: Deals stuck at 2x average stage duration.**
   - For each deal that has been in its current stage for 2x+ the average:
     - Deal name, stage, days in stage, stage average
     - Recommended action: direct conversation with the deal owner — what's blocking this?
     - If stuck in an early stage: likely needs disqualification, not more nurturing

6. **Flag: Stage-timeline mismatch.**
   - For each deal where expected close date is within 30 days but stage suggests it's not close:
     - Deal name, stage, expected close date, amount
     - Recommended action: either advance the stage or push the close date — don't let fantasy dates inflate the forecast

7. **Flag: Deals to kill.**
   - Aggregate all deals that have 3+ risk flags, or any single critical flag:
     - Deal name, flags, total time in pipeline
     - Recommended action: explicit kill decision or last-ditch rescue plan with a deadline

8. **Store results** in working memory:
   ```
   risk_flags:
     no_activity:
       - deal: ...
         days_inactive: N
         stage: ...
         amount: $X
         action: ...
         severity: warning | critical
     no_next_step:
       - deal: ...
         stage: ...
         amount: $X
         action: ...
     no_buyer_access:
       - deal: ...
         stage: ...
         amount: $X
         known_contacts: [...]
         missing_role: economic buyer
         action: ...
     stage_concentration:
       flagged: true/false
       stage: ...
       pct: X%
       action: ...
     stuck_deals:
       - deal: ...
         stage: ...
         days_in_stage: N
         stage_avg: N
         action: ...
     timeline_mismatch:
       - deal: ...
         stage: ...
         close_date: YYYY-MM-DD
         action: ...
     kill_candidates:
       - deal: ...
         flags: [...]
         days_in_pipeline: N
         recommendation: kill | rescue-with-deadline
   total_flagged_deals: N
   total_value_at_risk: $X
   ```

---

## SUCCESS METRICS

- Every active deal evaluated against all risk categories
- Every flagged deal has a specific, actionable recommendation
- Kill candidates explicitly identified with reasoning
- Total value at risk calculated
- No vague flags — every flag has a "what" and a "do this"

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Missing last activity dates | Flag as unknown activity status. Recommend: "Audit CRM data — activity tracking gaps make pipeline management impossible." |
| No stage probability or velocity benchmarks | Use the defaults from step 02. Note which are estimated. |
| Every deal is flagged | That is a valid output. Report it directly: "X of Y deals have risk flags. Pipeline needs immediate attention." |
| CRM contact data incomplete (can't assess buyer access) | Flag the data gap itself as a risk: "Cannot assess buyer access — CRM contact records are incomplete." |

---

## NEXT STEP

Read fully and follow: `step-04-action-report.md`

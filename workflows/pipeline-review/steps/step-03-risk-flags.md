<!-- system:start -->
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

---

## Deep Analysis Protocol

After applying all risk flag categories (steps 1-7), reason about contradicting signals before finalizing the risk assessment. Individual flags are mechanical; the analysis is where judgment lives.

### When to Invoke

After all individual risk flags are evaluated, before storing results and moving to step 04.

### Reasoning Chain

1. **Signal contradiction resolution**: A deal flagged "stale" (14+ days no activity) BUT with a meeting scheduled this week is not truly stale — it's about to re-engage. A deal with "no buyer access" BUT a strong champion who just got promoted may be about to solve itself. Resolve each contradiction explicitly.
2. **Risk compounding**: Which deals have multiple flags that compound each other? "Stale + no next step + late stage" is not three independent risks — it's one dying deal. Identify compound patterns.
3. **Calendar cross-reference**: Check the controller's upcoming calendar against flagged deals. If there's already a meeting with the account next week, the recommended action should reference that meeting, not propose a new outreach.
4. **Owner pattern detection**: Does one deal owner have a disproportionate share of risk flags? That's not a deal problem — it's a coaching conversation. Flag the pattern, not just the individual deals.
5. **Kill list honesty**: For each kill candidate, reason through the sunk cost trap. "We've invested 6 months" is not a reason to keep a dead deal. What is the realistic probability this closes in the next 30 days?
6. **Prioritized risk narrative**: After resolving contradictions, what are the 3 deals that need the controller's attention THIS week? Not all flagged deals are equal — reason about which ones have the highest stakes and the most time-sensitive risk.

### What This Produces

- Risk flags that account for context, not just rules
- Contradicting signals resolved with explicit reasoning
- Owner-level patterns surfaced alongside deal-level flags
- A prioritized "act on these 3 this week" recommendation
<!-- system:end -->

<!-- personal:start -->
## Tool Binding: Structured Reasoning

Use `sequential-thinking` MCP to execute the Deep Analysis Protocol reasoning chain above.
<!-- personal:end -->

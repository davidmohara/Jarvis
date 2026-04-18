---
model: opus
---

<!-- system:start -->
# Step 03: Cross-Agent Escalation to Chase

## MANDATORY EXECUTION RULES

1. You MUST check EVERY initiative for revenue-impact before proceeding.
2. Escalate to Chase ONLY for initiatives flagged as revenue-impacting (tag or content match).
3. The Chase handoff MUST follow the cross-agent handoff contract from shared-definitions.md.
4. If no revenue-impacting initiatives exist, skip Chase escalation and proceed to step 04.
5. Incorporate Chase's context into the initiative assessment before delivering the report.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `initiative_registry` and `revenue_impacting_initiatives` from step 01, `blocker_analysis` from step 02
**Output:** `chase_context` per revenue-impacting initiative (if any), stored in working memory for step 04

---

## REVENUE-IMPACT DETECTION

An initiative is revenue-impacting when any of the following apply:
- It has the `revenue-impact` tag in its frontmatter
- Its title or content references: revenue, pipeline, ARR, MRR, deals, accounts, client retention, sales
- It is blocking an active sales deal in the CRM (check via Chase escalation)
- It depends on or is depended on by a revenue-generating initiative

---

## CROSS-AGENT HANDOFF CONTRACT (Quinn → Chase)

When escalating a revenue-impacting initiative, Quinn creates a handoff context:

```yaml
handoff:
  from: quinn
  to: chase
  reason: "Initiative has revenue impact — requesting pipeline context"
  original-request: "Executive requested initiative tracker review"
  work-completed: "Initiative status assessed: [status]. Blocker analysis complete."
  context:
    initiative-name: "..."
    revenue-estimate: "..."  # if known from initiative file
    affected-accounts: [...]  # if referenced in initiative file
  required-action: "Provide pipeline impact assessment for this initiative. Are there active deals affected? What is the revenue risk if this initiative stays blocked/at-risk?"
```

---

## YOUR TASK

### Sequence

1. **Check `revenue_impacting_initiatives` list from step 01.**
   - If empty: Skip to step 04 immediately.
   - If non-empty: proceed with Chase escalation for each flagged initiative.

2. **For each revenue-impacting initiative, create Chase handoff.**
   - Build the handoff context payload per the contract above
   - Include initiative name, current status, blocker summary (if blocked), and any revenue estimate from initiative file
   - Include any account names referenced in the initiative

3. **Invoke Chase for revenue context.**
   - Pass handoff payload to Chase agent
   - Chase reviews pipeline for affected accounts and active deals
   - Chase returns: list of affected deals, revenue at risk estimate, recommended action

4. **Incorporate Chase context.**
   - For each revenue-impacting initiative, attach Chase's assessment:
     - Affected active deals
     - Revenue at risk
     - Chase's recommended action
   - Flag in the initiative report if Chase context changes the urgency of the initiative

5. **Store results** in working memory:
   ```
   chase_context:
     - initiative_id: ...
       handoff_created: true | false
       affected_deals: [deal-name, ...]
       revenue_at_risk: "$X | unknown"
       chase_recommended_action: ...
       escalation_note: "..."
   ```

6. **Persist Chase escalation to knowledge layer.**
   - For each escalated initiative, write a knowledge layer entry to `memory/episodic/projects/`:
     - Filename: `YYYY-MM-DD-chase-escalation-[initiative-id].md`
     - YAML frontmatter:

       ```yaml
       type: cross-agent-escalation
       subject: "Chase escalation — [initiative title]"
       date: YYYY-MM-DD
       tags: [escalation, revenue-impact, chase]
       agent-source: quinn
       ```

     - Body: initiative status, Chase's assessment (affected deals, revenue at risk, recommended action), and escalation outcome
   - This ensures Chase's response is persisted for future initiative reviews and audit trail

---

## SUCCESS METRICS

- All revenue-impacting initiatives identified
- Chase handoff created for each revenue-impacting initiative
- Chase context incorporated into initiative assessment
- Non-revenue initiatives pass through unaffected

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No revenue-impacting initiatives found | Skip Chase escalation. Proceed to step 04. Note: "No revenue-impacting initiatives identified — Chase escalation not required." |
| Chase agent unavailable | Note: "Chase escalation unavailable — revenue context will be missing from report." Flag affected initiatives in report. Proceed to step 04. |
| Chase returns no pipeline matches | Note for that initiative: "No active deals found matching this initiative. Revenue impact may be indirect or future-dated." |

---

## NEXT STEP

Read fully and follow: `step-04-initiative-report.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

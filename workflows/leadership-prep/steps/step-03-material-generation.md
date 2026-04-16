---
model: opus
---

<!-- system:start -->
# Step 03: Material Generation

## MANDATORY EXECUTION RULES

1. You MUST generate all five content areas: strategic narrative, key metrics, initiative updates, risk register, and talking points.
2. Content MUST be tailored to the event type from step 01 — board content ≠ town hall content.
3. Cross-domain conflict notes from step 02 MUST appear in the risk register.
4. Every risk item MUST have a recommended mitigation or response.
5. Do NOT trigger the Harper handoff in this step — that is step 04.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `event_context` from step 01, `aggregated_context` from step 02
**Output:** `leadership_materials` — complete prep document sections ready for delivery

---

## YOUR TASK

### Sequence

1. **Generate the strategic narrative.**
   - Lead with the quarter's headline: what was accomplished, what the overall health looks like
   - For `board-meeting`: frame around strategic priorities and financial performance
   - For `quarterly-review`: frame around rocks progress and what's changing
   - For `town-hall`: frame around team wins, why they matter, and where the org is headed
   - Length: 3-5 sentences — punchy, authoritative, quotable

2. **Generate the key metrics summary.**
   - Include only metrics relevant to the event type:
     - Board: revenue metrics (pipeline, coverage ratio, revenue vs. target), rock completion rate
     - Quarterly review: rock status (on-track/at-risk/blocked counts), initiative completion, team health score
     - Town hall: wins count, key milestones achieved, people highlights
   - Present each metric as: Name | Value | vs. Target/Expected | Trend (up/down/flat)

3. **Generate initiative updates.**
   - List top initiatives relevant to this event
   - For each: title, owner, status, one-line update, next milestone
   - Group by status: completed wins first, then active, then at-risk/blocked
   - Flag any initiative with data conflicts from step 02

4. **Generate the risk register.**
   - List all material risks for this event's audience
   - Include cross-domain conflicts from step 02 as risk items
   - For each risk: description, probability (high/med/low), impact (high/med/low), mitigation/response
   - Board risks: financial, strategic, competitive
   - Quarterly risks: execution, resource, dependency blockers
   - Town hall risks: morale, communication gaps, unanswered concerns

5. **Generate talking points for key discussion items.**
   - 5-7 talking points structured as: topic → key message → supporting data
   - Include likely audience questions and prepared responses
   - For `board-meeting`: what decisions need to be made today
   - For `quarterly-review`: what adjustments are being made and why
   - For `town-hall`: what the executive wants people to believe and feel after the meeting

6. **Store results** in working memory:
   ```
   leadership_materials:
     event_type: ...
     event_name: ...
     strategic_narrative: "..."
     key_metrics:
       - name: ...
         value: ...
         vs_target: ...
         trend: up | down | flat
     initiative_updates:
       - title: ...
         owner: ...
         status: ...
         update: ...
         next_milestone: ...
         data_conflict: true | false
     risk_register:
       - risk: ...
         probability: high | medium | low
         impact: high | medium | low
         mitigation: ...
     talking_points:
       - topic: ...
         key_message: ...
         supporting_data: ...
         likely_question: ...
         prepared_response: ...
   ```

---

## SUCCESS METRICS

- All five content sections generated
- Content tailored to event type and audience
- Data conflict notes included in risk register
- Talking points include likely questions and responses

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Multiple domains unavailable — insufficient data | Note missing sections. Deliver partial materials. Flag: "Sections marked [INCOMPLETE] require manual data entry before the meeting." |
| No risks identified | Include at minimum the cross-domain conflict notes as risks. If truly no risks: state "No material risks identified — verify data completeness." |
| Event is tomorrow or sooner | Note: "Limited prep time. Prioritize talking points and risk register over comprehensive metrics." |

---

## NEXT STEP

Read fully and follow: `step-04-harper-handoff.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

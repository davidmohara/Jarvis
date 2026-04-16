---
model: sonnet
---

<!-- system:start -->
# Step 01: Deal Data Analysis

## MANDATORY EXECUTION RULES

1. You MUST pull the complete deal record from CRM — not just the deal name and outcome.
2. You MUST pull the full engagement history from the knowledge layer. The post-mortem is only as good as the data behind it.
3. You MUST identify what worked AND what didn't. A post-mortem with only positive findings is not honest analysis.
4. You MUST analyze the competitive dynamics — who else was in the running and why they won or lost.
5. Do NOT editorialize in this step. Pull the data clean and move on. Analysis happens in steps 02 and 03.
6. If CRM has limited data, flag what's missing and work with what's available.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Deal identifier (from controller), CRM, knowledge layer
**Output:** Complete deal data stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- "Closed deal" means outcome is either closed-won or closed-lost. No in-progress deals.
- Engagement history = all documented touchpoints: meetings, emails, proposals, demos, negotiations.
- "What worked" and "what didn't" are grounded in evidence from the engagement, not retrospective opinion.
- Competitive dynamics come from CRM notes, opportunity fields, and any documented competitive intelligence.
- Client feedback includes: any direct statements from the client, decision rationale captured in CRM, and knowledge layer notes from post-decision conversations.

---

## YOUR TASK

### Sequence

1. **Pull closed deal record from CRM** (CRM):
   - Deal name and account
   - Outcome: `won` or `lost`
   - Final decision date
   - Total deal value (if won) or estimated deal value (if lost)
   - Decision makers involved (who signed or who said no)
   - Competition: any named competitors in the deal
   - Loss reason (if lost) — use CRM loss reason field and any notes
   - Win differentiators (if won) — use CRM win reason field and any notes
   - Full timeline: deal creation date through close date (total duration)
   - Stage progression history (how many days in each stage)

2. **Pull engagement history from knowledge layer:**
   - Search for: meeting notes, prep docs, proposal reviews, negotiation records related to this deal
   - For each engagement record:
     - Date, type (meeting / email / demo / negotiation / executive briefing)
     - Attendees and their roles
     - Key outcomes or decisions
     - Any recorded commitments made by either side
     - Tone and momentum signals

3. **Identify what worked in the engagement:**
   - Tactics or approaches that positively influenced the deal
   - Relationships that opened doors or accelerated progress
   - Positioning or messaging that resonated
   - Internal advantages (timing, pricing, team, past history)
   - Evidence: quote, meeting note, stage advancement, or deal event that confirms it worked

4. **Identify what didn't work:**
   - Gaps in the engagement that created risk or slowed progress
   - Positioning or messaging that fell flat or created resistance
   - Relationship gaps (contacts we didn't reach, economic buyer we couldn't access)
   - Process failures (late proposals, slow follow-up, missed commitments)
   - Evidence for each item

5. **Analyze competitive dynamics:**
   - Who else was competing for this deal?
   - How were they positioned?
   - For lost deals: what did the competitor offer that we didn't?
   - For won deals: what was our competitive differentiator?
   - Any competitive intelligence that should be documented

6. **Capture client feedback:**
   - Any direct statements from the client about their decision
   - Post-decision conversation notes (if any)
   - Inferred feedback from engagement patterns (e.g., disengagement signals)

7. **Store results** in working memory:
   ```
   deal_data:
     deal: ...
     account: ...
     outcome: won | lost
     decision_date: YYYY-MM-DD
     value: $X
     duration_days: N
     decision_makers: [{name, role}, ...]
     competitors: [{name, positioning}, ...]
     loss_reason: ... | null
     win_differentiator: ... | null
     engagement_history:
       - date: YYYY-MM-DD
         type: meeting | email | demo | negotiation | ...
         attendees: [...]
         key_outcome: ...
     what_worked:
       - factor: ...
         evidence: ...
     what_didnt_work:
       - factor: ...
         evidence: ...
     competitive_dynamics:
       competitors_identified: [...]
       competitive_differentiator: ...
       loss_to_competitor: ... | null
     client_feedback:
       direct_statements: [...]
       inferred_signals: [...]
   ```

---

## SUCCESS METRICS

- Complete deal record pulled with outcome, timeline, and decision makers
- Engagement history documented from knowledge layer
- What worked and what didn't identified with supporting evidence
- Competitive dynamics analyzed (even if data is limited)
- Client feedback captured (direct or inferred)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| CRM unavailable | Use knowledge layer data only. Flag: "CRM unavailable — deal data limited to knowledge layer records." |
| No CRM record for the deal | Ask the controller for deal details. If unavailable, work from knowledge layer and client context. |
| No engagement history in knowledge layer | Note: "No engagement history on record." Work from CRM data only. Flag as a data gap. |
| Deal outcome unknown (neither won nor lost) | This workflow requires a closed deal. Flag: "Deal is not closed. Cannot run post-mortem on an open opportunity." |
| No competitive data available | Note: "No competitive intelligence on record for this deal." Recommend asking the team for context. |

---

## NEXT STEP

Read fully and follow: `step-02-pattern-recognition.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

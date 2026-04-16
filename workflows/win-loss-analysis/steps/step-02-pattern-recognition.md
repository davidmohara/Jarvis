---
model: sonnet
---

<!-- system:start -->
# Step 02: Pattern Recognition

## MANDATORY EXECUTION RULES

1. You MUST compare this deal against historical wins and losses. A single deal post-mortem without context is guesswork.
2. You MUST only report a pattern when the same factor appears in 3 or more deals with the same outcome.
3. You MUST surface client feedback themes — both positive and negative — across the dataset.
4. Do NOT report a pattern based on 1 or 2 data points. Coincidence is not a pattern.
5. If fewer than 5 closed deals exist, state the sample size limitation and provide per-deal breakdown instead of pattern analysis.
6. Do NOT analyze active deals in this step. Active deal lesson application is step 03's job.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Deal data from step 01, historical closed deals from CRM and knowledge layer
**Output:** Pattern analysis and client feedback themes stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Pattern threshold: same factor in 3+ deals with the same outcome (won or lost) before reporting as a pattern.
- "Same factor" means the same substantive theme — not necessarily identical wording.
- Sample size constraint: if total closed deals (won + lost) < 5, skip pattern analysis. Report per-deal findings instead.
- Client feedback themes are aggregated across all available deals, not just the current one.
- Patterns can be: tactical (what works in proposals), relational (buyer access matters), competitive (specific competitor displacement), or process-based (late-stage stalls).

---

## YOUR TASK

### Sequence

1. **Pull historical closed deals from CRM:**
   - Query all closed-won and closed-lost deals (not just the current one)
   - For each: outcome, loss/win reason, competition, deal size range, industry, timeline
   - Count total closed deals available
   - Note: if total < 5, set flag `sample_size_limited = true`

2. **Check sample size:**
   - If `sample_size_limited = true`:
     - Report: "Sample size limitation: fewer than 5 closed deals available. Pattern analysis requires a minimum of 5 deals. Providing per-deal breakdown instead."
     - Output individual deal findings for the current deal only
     - Skip steps 3-4 below
   - If sample is sufficient (5+ deals), continue

3. **Identify recurring winning patterns** (same factor in 3+ won deals):
   - Analyze: What tactics, relationships, positioning, or process elements appear in 3+ wins?
   - Common winning themes to investigate:
     - Executive sponsorship presence in wins vs. losses
     - Early competitive displacement vs. late entry
     - Specific service offering performance
     - Deal size and complexity patterns
     - Industry-specific win rates
     - Proposal turnaround time
   - For each pattern: name it, describe it, count the supporting deals

4. **Identify recurring losing patterns** (same factor in 3+ lost deals):
   - Analyze: What gaps, missteps, or competitive disadvantages appear in 3+ losses?
   - Common losing patterns to investigate:
     - No access to economic buyer
     - Late competitive entry
     - Proposal gaps vs. stated requirements
     - Pricing sensitivity patterns
     - Specific competitors winning repeatedly
     - Timeline misalignment
   - For each pattern: name it, describe it, count the supporting deals

5. **Surface client feedback themes:**
   - Aggregate feedback across all available deals (direct statements, inferred signals)
   - Identify recurring themes in positive feedback
   - Identify recurring themes in negative feedback or objections
   - Note any feedback specifically about the decision process (e.g., "too complex to evaluate")

6. **Store results** in working memory:
   ```
   pattern_analysis:
     sample_size_limited: true/false
     total_closed_deals: N
     won_deals: N
     lost_deals: N
     winning_patterns:
       - pattern: ...
         description: ...
         deal_count: N (minimum 3 to qualify)
         supporting_deals: [...]
     losing_patterns:
       - pattern: ...
         description: ...
         deal_count: N (minimum 3 to qualify)
         supporting_deals: [...]
     client_feedback_themes:
       positive: [...]
       negative: [...]
       decision_process_signals: [...]
     per_deal_breakdown:
       - deal: ...
         outcome: won | lost
         key_factor: ...
   ```

---

## SUCCESS METRICS

- Historical closed deals pulled and counted
- Sample size constraint applied honestly (report per-deal if < 5 deals)
- Winning patterns identified at 3+ deal threshold
- Losing patterns identified at 3+ deal threshold
- Client feedback themes aggregated
- No patterns reported below the 3-deal threshold

## FAILURE MODES

| Failure | Action |
|---------|--------|
| CRM historical data unavailable | Use knowledge layer records only. Flag: "Historical CRM data unavailable — pattern analysis limited to knowledge layer records." |
| Fewer than 5 closed deals | Set sample_size_limited = true. Report per-deal breakdown instead of patterns. Document the limitation clearly. |
| No patterns meet the 3-deal threshold | Report: "No patterns identified at the 3+ deal threshold. This deal is an isolated data point." |
| Inconsistent CRM data (missing fields) | Work with available data. Note which fields are missing and how that affects confidence in pattern findings. |

---

## NEXT STEP

Read fully and follow: `step-03-lesson-application.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

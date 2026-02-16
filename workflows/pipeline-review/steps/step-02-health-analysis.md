# Step 02: Pipeline Health Analysis

## MANDATORY EXECUTION RULES

1. You MUST calculate all five health metrics: total weighted pipeline, stage distribution, deal velocity, stale deal count, and coverage ratio.
2. You MUST compare weighted pipeline against remaining quarterly target. This is the single most important number.
3. You MUST assess funnel shape — a healthy pipeline is wider at the top, narrower at the bottom. Inverted funnels or stage clusters are problems.
4. Do NOT flag individual deal risks in this step. That is step 03's job. This step is aggregate health only.
5. Do NOT sugarcoat the numbers. If coverage is below 2x, say so.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Pipeline data from step 01
**Output:** Health metrics and analysis stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Analyze what exists in the pipeline now. Do not project or forecast future additions.
- Coverage ratio benchmarks: below 2x = at risk, 2-3x = healthy, above 3x = check for stale deals inflating the number.
- Stage probability defaults (if CRM doesn't define them): Prospecting 10%, Qualification 20%, Needs Analysis 40%, Proposal 60%, Negotiation 80%, Verbal Commit 90%.
- Deal velocity benchmarks vary by deal size. Flag outliers relative to the average for similarly-sized deals in the pipeline.

---

## YOUR TASK

### Sequence

1. **Calculate total pipeline metrics:**
   - Total pipeline value (sum of all deal amounts)
   - Total weighted pipeline value (sum of all weighted amounts)
   - Average deal size
   - Median deal size
   - Deal count by owner

2. **Analyze stage distribution (funnel shape):**
   - Count deals per stage
   - Sum value per stage
   - Calculate percentage of total pipeline in each stage
   - Assess funnel shape:
     - `healthy` — progressively fewer deals in later stages
     - `top-heavy` — too many deals stuck early (qualification problem)
     - `bottom-heavy` — few deals in early stages (prospecting problem, future gap)
     - `constipated` — one stage holds > 40% of value (bottleneck)

3. **Calculate deal velocity:**
   - Average days in current stage across all deals
   - Average days by stage (how long do deals typically sit in each stage)
   - Identify slow movers: deals that have been in their current stage for 2x the stage average
   - Identify fast movers: deals progressing faster than average (positive signal)

4. **Identify stale deals:**
   - Deals with no activity in 14+ days
   - For each: deal name, days since last activity, stage, amount
   - Calculate total pipeline value at risk from stale deals

5. **Calculate coverage ratio:**
   - Coverage = total weighted pipeline / remaining quarterly target
   - Rate: `critical` (< 1.5x), `at-risk` (1.5-2x), `healthy` (2-3x), `inflated` (> 3x — check for zombie deals)

6. **Identify deals approaching decision date:**
   - Deals with expected close date within 30 days
   - For each: deal name, expected close date, stage, amount
   - Flag any where the stage doesn't match the timeline (e.g., still in Qualification but closing in 2 weeks)

7. **Store results** in working memory:
   ```
   health_analysis:
     totals:
       pipeline_value: $X
       weighted_value: $X
       average_deal: $X
       median_deal: $X
       deal_count: N
     funnel:
       shape: healthy | top-heavy | bottom-heavy | constipated
       stage_breakdown:
         - stage: ...
           deals: N
           value: $X
           pct_of_pipeline: X%
     velocity:
       overall_avg_days: N
       by_stage:
         - stage: ...
           avg_days: N
       slow_movers: [{deal, days_in_stage, stage_avg}, ...]
       fast_movers: [{deal, days_in_stage, stage_avg}, ...]
     stale_deals:
       count: N
       total_value_at_risk: $X
       deals: [{name, days_since_activity, stage, amount}, ...]
     coverage:
       ratio: X.Xx
       rating: critical | at-risk | healthy | inflated
       remaining_target: $X
     approaching_close:
       count: N
       deals: [{name, close_date, stage, amount, stage_mismatch: true/false}, ...]
   ```

---

## SUCCESS METRICS

- All five health metrics calculated with concrete numbers
- Funnel shape assessed with clear reasoning
- Coverage ratio calculated against actual remaining quarterly target
- Stale deals quantified with total value at risk
- Stage-timeline mismatches identified for deals approaching close

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Missing stage probability data | Use default probabilities listed in context boundaries. Note which defaults were used. |
| Cannot calculate velocity (missing stage-entry dates) | Use days-in-current-stage only. Note: "Full velocity tracking requires stage transition dates from CRM." |
| Quarterly target is $0 or missing | Report metrics without coverage ratio. Note: "Coverage ratio unavailable — no quarterly target defined." |
| Only 1-2 deals in pipeline | Still run all metrics but note: "Pipeline too thin for meaningful funnel or velocity analysis. The issue is volume, not shape." |

---

## NEXT STEP

Read fully and follow: `step-03-risk-flags.md`

---
status: complete
started-at: "2026-04-21T15:30:30"
completed-at: "2026-04-21T15:30:45"
outputs:
  co_sell_captured: true
  rock4_gap_calculated: true
  cache_used: true
model: sonnet
---

<!-- system:start -->
# Step 02: Co-Sell Pipeline

## MANDATORY EXECUTION RULES

1. You MUST execute the co-sell-pipeline skill in full — do not summarize or skip partners.
2. You MUST pull both pipeline and won data — both pages are required for Rock 4 gap calculation.
3. You MUST calculate the Rock 4 gap: `$15M - Pipeline Revenue - Won Revenue`.
4. You MUST verify the date filter on the Won page shows full-year 2026 before reading values.
5. Do NOT skip the won page because pipeline data is already available — won revenue counts toward the target.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Sales Analytics PowerBI — Coselling Partner Pipeline and Won pages (via Playwright MCP)
**Output:** Formatted co-sell report stored in `accumulated-context.co_sell` in `state.yaml`

---

## CONTEXT BOUNDARIES

- Co-sell data is company-wide — not filtered to One Texas. This is intentional; Rock 4 is an
  Improving-level target, not a regional one.
- Rock 4 target: $15M co-sell pipeline by end of Q2 2026.
- Partners to capture: Microsoft, Confluent, SAP, Scrum.org (and any others present).
- Date filter on Won page must be set to 1/1/2026 - 12/31/2026. Change end date before start date.

---

## YOUR TASK

### Sequence

1. **Execute co-sell-pipeline skill** — read and follow `skills/co-sell-pipeline/SKILL.md` in full.
   The skill covers:
   - Navigate to Pipeline page, screenshot and read KPI tiles and partner breakdown table
   - Navigate to Won page, verify/set date filter (end date first), screenshot and read KPI tiles
     and partner breakdown table
   - Calculate Rock 4 gap and compile formatted report

2. **Store output** — write the complete formatted co-sell report to `state.yaml`:
   ```yaml
   accumulated-context:
     co_sell: |
       [full formatted output from skill]
   ```

3. **Update step frontmatter**:
   ```yaml
   status: complete
   completed-at: [timestamp]
   outputs:
     co_sell_captured: true
     rock4_gap_calculated: true
   ```

4. **Update workflow state**:
   ```yaml
   current-step: step-03-pipeline
   ```

---

## SUCCESS METRICS

- Pipeline revenue and opp count captured with full partner breakdown
- Won revenue and opp count captured with full partner breakdown
- Date filter on Won page confirmed as 1/1/2026 - 12/31/2026
- Rock 4 remaining gap calculated and included in output
- Full formatted output stored in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Pipeline page fails to load | Retry once after 5 seconds. If unavailable, note "Co-sell pipeline unavailable" in accumulated-context and proceed to step 03. |
| Won page fails to load | Note "Won revenue unavailable — gap calculation uses pipeline only" and proceed with partial data. |
| Date filter cannot be set | Read won data as-is. Note the filter state in output so the report consumer knows the date range. |
| Partner table is empty | Screenshot and note "No co-sell partner data found." Proceed. |

---

## NEXT STEP

Read fully and follow: `steps/step-03-pipeline.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

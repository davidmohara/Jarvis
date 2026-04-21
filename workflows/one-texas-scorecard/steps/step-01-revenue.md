---
status: complete
started-at: "2026-04-21T15:30:00"
completed-at: "2026-04-21T15:30:30"
outputs:
  revenue_captured: true
  cache_used: true
  most_recent_month: March
model: sonnet
---

<!-- system:start -->
# Step 01: Revenue Tracker

## MANDATORY EXECUTION RULES

1. You MUST execute the revenue-tracker skill in full — do not summarize or abbreviate.
2. You MUST collect all four metric groups: Revenue vs. Target, Revenue vs. Prior Year,
   Sequential Quarterly Revenue, and Monthly Revenue.
3. You MUST filter to Dallas and South Texas separately. Never report all-Improving totals.
4. You MUST store the complete formatted output before proceeding to step 02.
5. Do NOT skip the skill and hand-roll estimates from memory or prior sessions.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Enterprise Scorecard v4 Financial Outlook page (via Playwright MCP)
**Output:** Formatted revenue report stored in `accumulated-context.revenue` in `state.yaml`

---

## CONTEXT BOUNDARIES

- One Texas scope only: Dallas and South Texas (Austin + Houston). No all-Improving totals.
- Data is pulled live from PowerBI — do not use cached or estimated figures.
- The skill handles SSO authentication automatically. No manual login needed.
- If the page renders at a zoom level other than 71%, check `Month Name [Month]` in tooltip
  to confirm the correct data point before recording values.

---

## YOUR TASK

### Sequence

1. **Execute revenue-tracker skill** — read and follow `skills/revenue-tracker/SKILL.md` in full.
   The skill covers:
   - Navigate to Financial Outlook page
   - Filter to Dallas, read KPI tiles (Revenue vs. Target, Revenue vs. Prior Year,
     Sequential Quarterly Revenue) and hover for Monthly Revenue dollar figure
   - Filter to South Texas, read same values
   - Compile formatted report

2. **Store output** — write the complete formatted revenue report to `state.yaml`:
   ```yaml
   accumulated-context:
     revenue: |
       [full formatted output from skill]
   ```

3. **Update step frontmatter**:
   ```yaml
   status: complete
   completed-at: [timestamp]
   outputs:
     revenue_captured: true
     most_recent_month: [month name]
   ```

4. **Update workflow state**:
   ```yaml
   current-step: step-02-co-sell
   ```

---

## SUCCESS METRICS

- Revenue vs. Target captured for Dallas and South Texas (CQ, LQ, YTD)
- Revenue vs. Prior Year captured for Dallas and South Texas (CQ, LQ, YTD)
- Sequential Quarterly Revenue captured (CQ, PQ, 90-Day Forecast)
- Monthly Revenue dollar figure captured for most recent closed month
- Full formatted output stored in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| PowerBI page fails to load | Retry once after 5 seconds. If still unavailable, set step `status: aborted`, surface to controller: "[Chase]: Revenue Tracker unavailable — PowerBI not responding. Resume when available." |
| KPI tiles not visible after filter | Wait 2 seconds, screenshot again. If still empty, note "Dallas/STX KPI tiles did not render" and proceed with available data. |
| Monthly Revenue tooltip returns null | Try February coordinates (x≈378, y≈265). If still null, note "Monthly Revenue unavailable" and proceed. |
| SSO fails / redirects to login | Surface to controller: "[Chase]: SSO authentication failed for PowerBI. Manual login required." Pause workflow. |

---

## NEXT STEP

Read fully and follow: `steps/step-02-co-sell.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

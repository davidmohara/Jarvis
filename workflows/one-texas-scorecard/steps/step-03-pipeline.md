---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 03: Pipeline Snapshot

## MANDATORY EXECUTION RULES

1. You MUST execute the pipeline-snapshot skill in full — both the Pipeline Analytics and
   90 Day Weighted Pipeline pages are required.
2. You MUST filter to Dallas and South Texas separately on each page. Never read unfiltered totals.
3. You MUST lead with the 90-day weighted pipeline — that is the Rock 1 grading metric.
4. You MUST capture stage breakdown. Stage concentration risk is a key flag for this report.
5. Do NOT skip the second page (90 Day Weighted) — total pipeline without the weighted 90-day
   view is insufficient for Rock 1 assessment.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Sales Analytics PowerBI — Pipeline Analytics and 90 Day Weighted Pipeline pages (via Playwright MCP)
**Output:** Formatted pipeline report stored in `accumulated-context.pipeline` in `state.yaml`

---

## CONTEXT BOUNDARIES

- One Texas scope only: Dallas, TX and South Texas. Do not report all-Improving pipeline.
- Slicer is single-select on all pages — read each region separately before navigating.
- 90-day weighted pipeline is the primary Rock 1 metric. Total pipeline is supporting context.
- Stage concentration flag threshold: more than 40% of pipeline at 10%-Identified = early-stage
  concentration risk.

---

## YOUR TASK

### Sequence

1. **Execute pipeline-snapshot skill** — read and follow `skills/pipeline-snapshot/SKILL.md` in full.
   The skill covers:
   - Navigate to Pipeline Analytics page, filter to Dallas TX, read KPI tiles and stage breakdown
   - Filter to South Texas, read same values
   - Navigate to 90 Day Weighted Pipeline page, filter to Dallas TX, read weighted KPI tiles
   - Filter to South Texas, read same values
   - Compile formatted report with One Texas totals

2. **Store output** — write the complete formatted pipeline report to `state.yaml`:
   ```yaml
   accumulated-context:
     pipeline: |
       [full formatted output from skill]
   ```

3. **Update step frontmatter**:
   ```yaml
   status: complete
   completed-at: [timestamp]
   outputs:
     pipeline_captured: true
     weighted_pipeline_captured: true
   ```

4. **Update workflow state**:
   ```yaml
   current-step: step-04-new-clients
   ```

---

## SUCCESS METRICS

- Total pipeline and weighted pipeline captured for Dallas and South Texas
- 90-day weighted pipeline value captured (primary Rock 1 metric)
- Stage breakdown captured for both regions
- One Texas combined totals computed
- Stage concentration risk assessed
- Full formatted output stored in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Pipeline Analytics page fails to load | Retry once. If unavailable, note "Pipeline Analytics unavailable" and proceed to step 04. |
| 90 Day Weighted page fails to load | Note "90-day weighted pipeline unavailable — Rock 1 metric missing from this snapshot." Proceed with total pipeline data only. |
| Slicer text not found ('Dallas, TX' or 'South Texas') | Try DOM text-click fallback per skill notes. If still fails, note region as unavailable. |
| KPI tiles empty after filter | Wait 2 seconds, screenshot again. If still empty, note and proceed. |

---

## NEXT STEP

Read fully and follow: `steps/step-04-new-clients.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

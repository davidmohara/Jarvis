---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Pull Pipeline Data

## MANDATORY EXECUTION RULES

1. You MUST pull every active opportunity from CRM before proceeding. No partial pulls, no sampling.
2. You MUST capture all required fields for each deal: name, stage, amount, weighted amount, age in current stage, last activity date, owner, next step.
3. You MUST load quarterly revenue targets for comparison. Pipeline without a target is just a list.
4. You MUST load upcoming client meetings from calendar — these are your "deals in motion" signal.
5. Do NOT analyze or editorialize in this step. Pull the data clean and move on.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** CRM (CRM), quarterly objectives, calendar
**Output:** Complete pipeline inventory stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Active opportunities only. Do not pull closed-won, closed-lost, or archived deals.
- "Active" means the deal has not been marked closed and is not on hold.
- Include all stages from prospecting through closed-won pending (if that stage exists).
- Calendar data is limited to client-type meetings in the next 7 days.
- **Enterprise scope:** Filter opportunities to the controller's assigned enterprises (defined in the personal block of `agents/chase.md`). Do not pull the full company pipeline unless the controller explicitly requests it with "pipeline all". If no enterprise scope is defined in chase.md, pull all and warn that scope is unconfigured.

---

## YOUR TASK

### Sequence

1. **Pull all active opportunities from CRM** (CRM), filtered to the controller's enterprise scope.
   - Read enterprise scope from personal block of `agents/chase.md` — default is Dallas, Austin, Houston.
   - Apply filter: `Enterprise IN (Dallas, Austin, Houston)` on the opportunity record before pulling.
   - If controller said "pipeline all", skip the enterprise filter and note "Company-wide view" in the report header.
   - For each opportunity capture:
     - Deal name
     - Account name
     - Stage (exact CRM stage name)
     - Amount (total deal value)
     - Weighted amount (amount x stage probability)
     - Days in current stage
     - Last activity date (email, meeting, or note — whichever is most recent)
     - Owner (who from the controller's team owns this)
     - Next step (if defined in CRM)
     - Expected close date

2. **Load quarterly revenue targets** from `{project-root}/context/quarterly-objectives.md`.
   - Extract the revenue rock / pipeline target for the current quarter
   - Calculate remaining target (target minus closed-won this quarter)
   - Note days remaining in the quarter

3. **Pull upcoming client meetings** via M365 MCP (`outlook_calendar_search`).
   - Filter: next 7 days, client-type meetings
   - For each: subject, attendees, date/time
   - Cross-reference attendees against CRM contacts to link meetings to deals

4. **Pull recent client meeting notes** from knowledge layer.
   - Search for meeting notes from the last 14 days involving client accounts
   - Capture key outcomes, decisions, next steps documented

5. **Store results** in working memory:
   ```
   pipeline_data:
     snapshot_date: YYYY-MM-DD
     total_deals: N
     total_pipeline_value: $X
     total_weighted_value: $X
     deals:
       - name: ...
         account: ...
         stage: ...
         amount: $X
         weighted: $X
         days_in_stage: N
         last_activity: YYYY-MM-DD
         owner: ...
         next_step: ...
         expected_close: YYYY-MM-DD
     quarterly_target:
       total: $X
       closed_won_ytd: $X
       remaining: $X
       days_remaining: N
     upcoming_meetings:
       - date: YYYY-MM-DD
         subject: ...
         attendees: [...]
         linked_deal: ... | null
     recent_notes:
       - account: ...
         date: YYYY-MM-DD
         key_takeaway: ...
   ```

---

## SUCCESS METRICS

- Every active opportunity captured with all required fields
- Quarterly revenue target loaded with remaining calculation
- Upcoming client meetings identified and linked to deals where possible
- Recent client notes pulled for deal context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| CRM unavailable | Report: "CRM data unavailable. Cannot run pipeline review without deal data." Stop workflow. |
| Quarterly objectives file missing | Warn: "No revenue target loaded — pipeline analysis will lack target context." Proceed with raw pipeline data. |
| Calendar unavailable | Proceed without meeting data. Note: "Upcoming meeting context missing." |
| No active opportunities found | Report: "Zero active opportunities in CRM. That's either a data problem or a pipeline problem. Confirm CRM data is current." End workflow. |

---

## NEXT STEP

Read fully and follow: `step-02-health-analysis.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

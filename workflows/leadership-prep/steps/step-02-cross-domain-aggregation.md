---
model: opus
---

<!-- system:start -->
# Step 02: Cross-Domain Data Aggregation

## MANDATORY EXECUTION RULES

1. You MUST pull from ALL four domains: Quinn (self), Chase, Shep, Chief.
2. If an agent is unavailable, note the gap — do NOT silently omit the domain.
3. You MUST detect and flag cross-domain data conflicts before proceeding to material generation.
4. Do NOT generate materials in this step. Collect and organize data only.
5. Use the event_context from step 01 to prioritize what data matters most.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `event_context` from step 01
**Output:** `aggregated_context` — consolidated cross-domain data for material generation

---

## YOUR TASK

### Sequence

1. **Pull Quinn's own strategic data (self).**
   - Load rock status from knowledge layer (or invoke rock-review workflow if no recent review)
   - Load initiative tracker summary (top initiatives by status)
   - Load goal alignment summary if available from recent alignment check
   - Capture: rock count by status, top at-risk/blocked initiatives, quarterly progress narrative

2. **Pull Chase's revenue context.**
   - Request from Chase: pipeline health summary, revenue forecast, top deals and risks
   - Capture: weighted pipeline value, coverage ratio, revenue trend vs. target, key deal updates
   - Note if Chase context is unavailable

3. **Pull Shep's people context.**
   - Request from Shep: team health summary, open roles, key delegation status
   - Capture: team health status, any at-risk relationships, notable delivery updates
   - Note if Shep context is unavailable

4. **Pull Chief's operational context.**
   - Request from Chief: key operational wins this period, active blockers, calendar highlights
   - Capture: operational wins, open issues, upcoming commitments
   - Note if Chief context is unavailable

5. **Detect cross-domain conflicts.**
   - Compare data from different agents for discrepancies
   - Example conflicts: Chase reports pipeline healthy but Quinn shows revenue rock blocked; Shep reports team health good but Chief notes key person absent
   - For each conflict: record `conflict_note` = "Data discrepancy — [Agent A] reports [X], [Agent B] reports [Y]. Recommend resolving before the meeting."
   - For each conflict, also record `resolution_action` = specific follow-up to resolve (e.g., "Verify pipeline figure with Chase before board meeting", "Confirm headcount with Shep")

6. **Apply event-type filters.**
   - `board-meeting`: emphasize financial metrics, strategic risks, key decisions needed
   - `quarterly-review`: emphasize rock progress, initiative updates, blockers
   - `town-hall`: emphasize wins, narrative, forward vision, culture signals

7. **Store results** in working memory:
   ```
   aggregated_context:
     strategic:
       rocks_on_track: N
       rocks_at_risk: N
       rocks_blocked: N
       top_initiatives: [title, status, ...]
       quarterly_narrative: "brief summary"
     revenue:
       weighted_pipeline: "$X"
       coverage_ratio: "Nx"
       revenue_vs_target: "N% of target"
       key_deal_updates: [...]
       source_available: true | false
     people:
       team_health_status: thriving | needs-attention | at-risk
       open_roles: N
       key_updates: [...]
       source_available: true | false
     operational:
       key_wins: [...]
       active_blockers: [...]
       source_available: true | false
     conflicts:
       - domain_a: ...
         domain_b: ...
         conflict_note: "..."
        resolution_action: "..."
   ```

---

## SUCCESS METRICS

- Data pulled from all four domains (or gaps noted)
- Cross-domain conflicts identified and flagged
- Data filtered and prioritized per event type
- Aggregated context ready for material generation

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Chase unavailable | Note: "Revenue context unavailable — Chase could not be reached. Revenue section will be incomplete." Proceed. |
| Shep unavailable | Note: "People context unavailable — Shep could not be reached. People section will be incomplete." Proceed. |
| Chief unavailable | Note: "Operational context unavailable — Chief could not be reached. Ops section will be incomplete." Proceed. |
| No rock review data available | Use most recent knowledge layer rock review entry. If none: note "No recent rock review — strategic section based on initiative tracker only." |

---

## NEXT STEP

Read fully and follow: `step-03-material-generation.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
model: opus
---

<!-- system:start -->
# Step 03: Assess Rock Status

## MANDATORY EXECUTION RULES

1. You MUST apply the threshold criteria exactly as defined — no overrides, no gut-feel adjustments.
2. Status classification MUST be based on evidence gathered in step 02, not self-reported status.
3. Dependency impacts MUST be evaluated: if a dependency is at-risk or blocked, the dependent rock is escalated.
4. For every at-risk or blocked rock, you MUST generate corrective action recommendations.
5. You MUST estimate remaining effort and remaining quarter time for each rock.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `rock_inventory` from step 01, `rock_evidence` from step 02
**Output:** `rock_assessments` — full classification with rationale, corrective actions, and dependency flags

---

## STATUS CLASSIFICATION RULES

### Primary Classification

| Status | Criterion |
|--------|-----------|
| `on-track` | Evidence shows progress >= 70% of expected for elapsed quarter time |
| `at-risk` | Evidence shows progress 40%–69% of expected; or stale (no activity in 14+ days) with > 30% of quarter elapsed |
| `blocked` | Active blocker present in initiative tracker or knowledge layer; or zero evidence with > 50% of quarter elapsed |
| `completed` | Rock success criteria are met per evidence |

### Progress Estimation

Expected progress = percentage of quarter elapsed × 100%

Observable progress estimate:
- 0 completed tasks + 0 KL entries + stale/blocked initiatives = 0–10%
- Some tasks completed, recent KL entry, active initiatives = estimate based on task count relative to scope
- When success criteria are quantitative, map completed milestones to percentage directly
- When success criteria are qualitative, use activity density and recency as proxy

### Dependency Escalation

If rock A depends on rock B:
- Rock B is `blocked` → rock A status escalates to `at-risk` (minimum), even if rock A has activity
- Rock B is `at-risk` → flag rock A as "dependency risk" in the report; do not auto-escalate status
- Note the dependency impact explicitly in rock A's assessment

### Stale Definition

A rock is stale when `days_since_last_activity` >= 14. Stale rocks with > 30% of quarter elapsed are `at-risk` by default.

---

## YOUR TASK

### Sequence

1. **For each rock, calculate progress estimate.**
   - Use evidence summary from step 02
   - Compare to expected progress threshold for elapsed quarter time
   - Document the evidence basis for the estimate

2. **Classify each rock's status.**
   - Apply threshold rules exactly
   - If active blocker found in evidence → `blocked`
   - If stale AND > 30% quarter elapsed → `at-risk`
   - If progress < 40% of expected AND > 50% of quarter elapsed → `blocked`
   - If progress >= 70% of expected → `on-track`
   - If between 40–69% of expected → `at-risk`

3. **Evaluate dependencies.**
   - For rocks with dependencies, check the dependency's classified status
   - Apply escalation rules
   - Document impact statement for each dependency relationship

4. **Generate corrective actions for at-risk and blocked rocks.**
   - For `at-risk`: identify what specific activities would accelerate progress
   - For `blocked`: identify the blocker owner and unblocking action
   - Each corrective action must be specific, assignable, and time-bound

5. **Estimate remaining effort per rock.**
   - Weeks remaining in quarter
   - Estimated effort gap (what work still needs to happen)
   - Whether the timeline is achievable given pace

6. **Store results** in working memory:
   ```
   rock_assessments:
     - rock_id: rock-1
       title: ...
       status: on-track | at-risk | blocked | completed
       progress_estimate: N%
       expected_progress: N%
       evidence_basis: "summary of evidence used"
       stale: true | false
       days_since_activity: N
       dependency_flags:
         - depends_on: rock-id
           dependency_status: on-track | at-risk | blocked
           impact: "description of impact on this rock"
       corrective_actions: [] | ["action 1", "action 2"]
       effort_remaining: "qualitative estimate"
       weeks_remaining: N
       on_track_for_completion: true | false
   ```

---

## SUCCESS METRICS

- Every rock classified with explicit status and evidence basis
- Dependency flags populated for all dependent rocks
- Corrective actions generated for every at-risk and blocked rock
- Remaining effort and timeline assessed for each rock

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No evidence for a rock with > 50% quarter elapsed | Classify as `blocked`. Note: "No evidence of progress found. With the quarter more than half complete, this rock is classified as blocked." |
| Ambiguous progress estimation | Default to lower status tier (more conservative). Flag: "Progress estimate is uncertain due to limited evidence." |
| Dependency rock not found in inventory | Note the missing dependency. Do not escalate based on unknown dependency. |
| All rocks are on-track | Report honestly. Do not manufacture risk. |

---

## NEXT STEP

Read fully and follow: `step-04-action-report.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

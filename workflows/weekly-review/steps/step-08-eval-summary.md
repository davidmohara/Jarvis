---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 08: Eval Summary

## MANDATORY EXECUTION RULES

1. You MUST check if eval harness exists before proceeding. If `systems/eval-harness/` does not exist, skip this step.
2. You MUST invoke rigby-eval-analyze skill to get the weekly eval summary.
3. You MUST surface any degraded trends or concerning patterns.
4. Do NOT proceed to final summary until eval data is presented.

---

## EXECUTION PROTOCOL

**Agent:** Master (orchestrates Rigby for eval analysis)
**Input:** Eval harness data from the past week
**Output:** Eval summary with trends, degraded areas, and action items

---

## CONTEXT BOUNDARIES

- Look at eval records from the past 7 days in `systems/eval-harness/runs/`
- Focus on trends across all four assessment tiers:
  - Tier 1: Mechanical success/fail rates
  - Tier 2: Structural assertion pass rates
  - Tier 3: Grade distribution (A-F)
  - Tier 4: Controller feedback ratings
- Identify workflows or skills that are degrading or need attention

---

## YOUR TASK

### Sequence

1. **Check for eval harness presence**
   - Verify `systems/eval-harness/` directory exists
   - If not present, skip this step and log: "Eval harness not installed. Skipping eval summary."
   - Proceed to final summary step

2. **Invoke rigby-eval-analyze skill**
   - Call the rigby-eval-analyze skill with scope: "last 7 days"
   - Request analysis across all four assessment tiers
   - Ask for trend analysis (improving, stable, degraded)

3. **Present eval summary to controller:**
   - "Here's the eval harness summary for this week..."
   - Present key metrics:
     - Total eval runs this week
     - Overall success rate (Tier 1)
     - Assertion pass rate (Tier 2)
     - Grade distribution (Tier 3)
     - Controller feedback average (Tier 4, if available)
   - Highlight trends: "Workflow X is improving (+5% success rate)" or "Skill Y is degrading (-3% grade average)"

4. **Surface action items:**
   - If any workflows/skills show degraded trends, flag them: "Consider reviewing [workflow/skill] - performance has declined this week."
   - If controller feedback ratings are low, surface: "Controller feedback is averaging X/5 this week. Any specific concerns?"
   - Append any eval action items to the weekly review file from step-06

5. **Close the weekly review:**
   - Append a final `## Eval Health` section to the weekly review file (`reviews/weekly/YYYY-Wxx.md`) with the eval summary or "Eval harness not installed"
   - Write `status: complete` to `workflows/weekly-review/state.yaml` to mark the workflow done
   - Confirm to the controller: "Weekly review complete. See reviews/weekly/YYYY-Wxx.md for the full summary."

---

## SUCCESS METRICS

- Eval harness presence checked and logged
- Rigby-eval-analyze skill invoked successfully (or skipped with reason logged)
- Eval summary appended to weekly review file
- Degraded areas flagged with actionable recommendations
- Weekly review file finalized
- `state.yaml` written with `status: complete`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Eval harness not installed | Log "Eval harness not installed" in weekly file. Proceed to close. |
| No eval records in past 7 days | Note in weekly file: "No eval data this week." Proceed to close. |
| Rigby-eval-analyze skill fails | Log error in weekly file. Proceed to close. |
| Weekly review file not found | Write eval section to working memory. Still write state.yaml complete. |

---

## NEXT STEP

This is the final step of the weekly review. After closing, no further steps.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

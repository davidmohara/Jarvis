---
model: opus
---

<!-- system:start -->
# Step 01: Load Quarterly Rocks

## MANDATORY EXECUTION RULES

1. You MUST read `identity/GOALS_AND_DREAMS.md` completely before proceeding.
2. You MUST extract every quarterly rock defined — title, description, success criteria, dependencies.
3. You MUST calculate quarter progress context: current week of quarter, percentage of quarter elapsed.
4. If no rocks are defined, STOP immediately and tell the executive — do NOT proceed with empty data.
5. Do NOT assess or classify rocks in this step. Load and inventory only.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `identity/GOALS_AND_DREAMS.md`
**Output:** Rock inventory and quarter timeline stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Quarterly rocks only. Annual goals are context — do not assess them here.
- A "rock" is a 90-day priority commitment. If the file uses different terminology (OKR, priority, initiative) treat it as a rock if it has a quarterly scope.
- Dependencies: a rock depends on another rock if the file explicitly states it or if its success criteria require another rock's output.

---

## YOUR TASK

### Sequence

1. **Read `identity/GOALS_AND_DREAMS.md`** in full.
   - Locate the quarterly rocks section (may be labeled Quarterly Rocks, Q[N] Rocks, 90-Day Priorities, etc.)
   - For each rock extract:
     - Rock title
     - Description / success criteria
     - Owner (if specified)
     - Target completion date or quarter end
     - Dependencies on other rocks (if stated)
     - Any progress notes already recorded in the file

2. **Check for no-rocks condition.**
   - If GOALS_AND_DREAMS.md does not exist, or exists but has no quarterly rocks defined:
     - Output: "No quarterly rocks are defined in your GOALS_AND_DREAMS.md. Quarterly rocks are 90-day priority commitments that drive your most important outcomes. Would you like help defining your rocks for this quarter?"
     - STOP workflow.

3. **Calculate quarter context.**
   - Determine current date and current quarter (Q1: Jan–Mar, Q2: Apr–Jun, Q3: Jul–Sep, Q4: Oct–Dec)
   - Calculate: weeks elapsed in quarter, weeks remaining, percentage of quarter elapsed
   - For a rock to be "on track," progress should be >= (percentage of quarter elapsed × 100)%

4. **Store results** in working memory:
   ```
   rock_inventory:
     quarter: Q[N] YYYY
     quarter_start: YYYY-MM-DD
     quarter_end: YYYY-MM-DD
     weeks_elapsed: N
     weeks_remaining: N
     pct_quarter_elapsed: N%
     rocks:
       - id: rock-1
         title: ...
         description: ...
         success_criteria: ...
         owner: ...
         target_date: YYYY-MM-DD | quarter-end
         dependencies: [rock-id, ...] | []
         notes_in_file: ...
   ```

---

## SUCCESS METRICS

- All quarterly rocks extracted with title, description, and success criteria
- Quarter timeline calculated with weeks elapsed and remaining
- Dependencies mapped between rocks
- No-rocks condition handled before proceeding

## FAILURE MODES

| Failure | Action |
|---------|--------|
| GOALS_AND_DREAMS.md does not exist | Report: "GOALS_AND_DREAMS.md not found. Quarterly rocks cannot be reviewed without this file. Run the initialization workflow to set up your identity layer." Stop workflow. |
| File exists but has no quarterly rocks | Report: "No quarterly rocks are defined in your GOALS_AND_DREAMS.md." Prompt executive to define rocks. Stop workflow. |
| Rock has no success criteria | Proceed with available data. Flag in report: "Rock '[title]' has no defined success criteria — assessment will be qualitative only." |
| Dependencies reference unknown rocks | Note the orphaned dependency reference. Proceed with assessment. |

---

## NEXT STEP

Read fully and follow: `step-02-gather-evidence.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

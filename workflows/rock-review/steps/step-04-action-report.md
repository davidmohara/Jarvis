---
model: opus
---

<!-- system:start -->
# Step 04: Action Report and Knowledge Layer Update

## MANDATORY EXECUTION RULES

1. You MUST deliver the rock scorecard before writing to the knowledge layer.
2. You MUST write updated rock status to the knowledge layer regardless of outcome.
3. The knowledge layer write MUST include: assessment date, status per rock, evidence basis, and rationale.
4. Track status changes over time — if a previous review exists in the knowledge layer, note the change.
5. End the report with a single named rock that most needs attention this week.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `rock_assessments` from step 03
**Output:** Delivered rock scorecard + knowledge layer update written

---

## YOUR TASK

### Sequence

1. **Deliver the rock scorecard.**

   Format as follows:

   ---
   **Q[N] Rock Review — [Date]**
   **Quarter Progress:** Week [N] of 13 | [N]% elapsed | [N] weeks remaining

   **[Rock Title]**
   Status: [on-track / at-risk / blocked / completed]
   Progress: ~[N]% (expected: [N]%)
   Last activity: [date] ([N] days ago)
   Evidence: [brief summary — e.g., "3 tasks completed, 2 KL entries, initiative active"]
   [If at-risk or blocked] Corrective actions:
   - [Specific action 1]
   - [Specific action 2]
   [If dependency flag] Dependency risk: [rock name] is [status] — [impact statement]

   [Repeat for each rock]

   ---
   **Quarter Health Summary**
   On track: [N] / [total]
   At risk: [N] / [total]
   Blocked: [N] / [total]

   **Pace check:** [Is the executive spending time on rocks or on noise? Be specific.]
   **Red flags:** [Any rocks approaching the point of no return]

   **The one rock that needs your attention most this week:**
   [Rock name] — [one sentence on why and what action to take]
   ---

2. **Write updated rock status to the knowledge layer.**
   - Create a new file in `context/projects/` named: `YYYY-MM-DD-HHmmss-rock-review-Q[N]-YYYY.md`
   - Use the knowledge layer entry frontmatter schema:
     ```yaml
     type: project-history
     subject: "Quarterly Rock Review Q[N] YYYY"
     date: YYYY-MM-DD
     tags: [rock-review, strategy, quarterly]
     related-entities:
       projects: [rock-review]
     agent-source: quinn
     ```
   - Body content:
     - Overall quarter status summary
     - Per-rock: status, progress estimate, evidence basis, assessment rationale
     - Status changes from previous review (if prior review found in knowledge layer)
     - Corrective actions recommended

3. **Check for prior rock review in knowledge layer.**
   - Search `context/projects/` for files matching `rock-review-Q[N]`
   - If found, compare previous status to current status per rock
   - Note any regressions (e.g., rock moved from on-track to at-risk) in the new entry
   - Note improvements (e.g., blocked rock is now at-risk or on-track)

4. **Confirm knowledge layer write.**
   - Report: "Rock review written to context/projects/[filename]"

---

## OUTPUT FORMAT RULES

- Lead with the scorecard. No preamble.
- Status icons help scannability: use On Track, At Risk, Blocked, Completed labels (no emojis unless system is configured for them)
- Corrective actions must be specific: "Schedule 2-hour strategy session by Friday to finalize go-to-market plan" not "work on the rock more"
- The closing "one rock" statement is non-optional. Quinn always picks one.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Knowledge layer write fails | Report: "Rock review delivered. Note: Knowledge layer write failed — [reason]. Review was not persisted." Do not block report delivery. |
| No prior review exists for comparison | Skip status-change tracking. Note: "No prior rock review found — this appears to be the first review of the quarter." |
| All rocks blocked | Deliver the report as-is. Do not soften. Recommend executive scheduling a strategy reset session. |
| One or more rocks have no evidence | Report exactly: "No evidence of progress found for [rock title]. Cannot confirm activity is happening." |

---

## WORKFLOW COMPLETE

Rock review delivered and knowledge layer updated.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

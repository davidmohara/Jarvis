---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Social Calendar Lookahead

## MANDATORY EXECUTION RULES

1. This step runs AFTER step-06 (priorities are already set). It is the final step before closing.
2. Route to Sterling. Sterling runs `skills/sterling-social-tracker/SKILL.md` in full.
3. Do NOT skip this step if the site is unavailable — report the failure and close cleanly.
4. Do NOT ask David for his interest profile — it lives in the skill file. Read and apply it.
5. Append results to the weekly review file that step-06 already created.

---

## EXECUTION PROTOCOL

**Agent:** Sterling (Personal)
**Input:** Today's date (for lookahead window calculation), current weekly review file path from step-06
**Output:** Social tracker table appended to `reviews/weekly/YYYY-Wxx.md`

---

## CONTEXT BOUNDARIES

- This is a forward-looking planning step, not a retrospective. Events in the past 4 weeks are irrelevant.
- Sterling filters independently using the interest profile in the skill file. Do not ask David what he's interested in.
- Feedback captured here updates the skill file directly — no separate preferences file.

---

## YOUR TASK

1. **Route to Sterling** with the instruction: "Run the DFW social tracker skill. Lookahead window is today through 4 weeks out. Append results to the weekly review file at [path from step-06]."

2. **Sterling executes** `skills/sterling-social-tracker/SKILL.md` — fetches dfw.msondo.com, filters, builds the table, appends to the review file.

3. **Surface the table** to the controller inline in the review conversation. Don't make them open the file to see it.

4. **Present the feedback prompt** if this is one of the first 8 runs (per Learned Preferences count in the skill file). Wait for feedback. If feedback is given, Sterling updates the skill file immediately — do not defer.

5. **Close the weekly review** after feedback is captured (or if David declines to give feedback):
   > "Review complete. Priorities are set. Social calendar is loaded. Go execute."

---

## SUCCESS METRICS

- Social tracker table presented inline
- Results appended to weekly review file
- Feedback captured and applied to skill file (if within first 8 runs)
- Weekly review closed cleanly

## FAILURE MODES

| Failure | Action |
|---------|--------|
| dfw.msondo.com unavailable | Note in review file: "Social tracker unavailable this week." Close the review. |
| No events found in lookahead window | Report to David: "Nothing on the DFW radar for the next 4 weeks." Close the review. |
| Weekly review file from step-06 not found | Append table to working memory instead: `memory/working/YYYY-MM-DD-social-tracker.md`. Report the file path. |
| David provides feedback mid-table | Stop, apply the feedback update to the skill file, then continue. |

---

## NEXT STEP

This is the final step. After closing:

Write `state.yaml` in the workflow directory with `status: complete` and `current-step: step-07`.

```yaml
workflow: weekly-review
agent: master
status: complete
current-step: step-07
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

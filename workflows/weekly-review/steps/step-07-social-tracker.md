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

1. This step runs AFTER step-06 (priorities are already set).
2. Route to Sterling. Sterling runs `skills/sterling-social-tracker/SKILL.md` in full.
3. Do NOT skip this step if the site is unavailable — report the failure and proceed to step-08.
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

---

## SUCCESS METRICS

- Social tracker table presented inline
- Results appended to weekly review file
- Feedback captured and applied to skill file (if within first 8 runs)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| dfw.msondo.com unavailable | Note in review file: "Social tracker unavailable this week." Proceed to step-08. |
| No events found in lookahead window | Report to David: "Nothing on the DFW radar for the next 4 weeks." Proceed to step-08. |
| Weekly review file from step-06 not found | Append table to working memory instead: `memory/working/YYYY-MM-DD-social-tracker.md`. Report the file path. Proceed to step-08. |
| David provides feedback mid-table | Stop, apply the feedback update to the skill file, then continue to step-08. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py weekly-review step-07-social-tracker complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-08-eval-summary.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

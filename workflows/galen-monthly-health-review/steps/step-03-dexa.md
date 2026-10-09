---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Pull DEXA & Body Composition

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`
**Output:** `body_comp_monthly` summary stored in working memory

---

## YOUR TASK

**Read:** `~/Library/CloudStorage/Dropbox/Family/Health/David - Health Tracking.xlsx`

**Extract:**
- Latest DEXA scan date
- Weight (current vs. prior month)
- Body fat % (current vs. prior month)
- BMI (current vs. prior month)
- Muscle mass (if captured)
- Trend direction for each metric

**Lifebook Health Goals:**
- Weight: 210 lbs
- Body fat: 17%
- BMI: <20

**Calculate:**
- Pounds from goal weight
- Body fat % from goal
- Progress toward goal (on track / at risk / off track)

**Store in working memory:**
```
body_comp_monthly:
  dexa_date: YYYY-MM-DD
  weight: N lbs (goal: 210)
  body_fat: N% (goal: 17%)
  bmi: N (goal: <20)
  weight_trend: "up" | "stable" | "down" (vs. prior month)
  body_fat_trend: "up" | "stable" | "down" (vs. prior month)
  progress_assessment: "on track" | "at risk" | "off track"
  lbs_from_goal: N
  bf_from_goal: N%
```

## NEXT STEP

Read fully and follow: `step-04-lifebook.md`
<!-- system:end -->

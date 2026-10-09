---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Pull WHOOP 30-Day Data

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** 30 days of WHOOP recovery, sleep, workout, and HRV data
**Output:** `whoop_monthly` summary stored in working memory

---

## YOUR TASK

**Reference:** Use `skills/galen-whoop-analysis/SKILL.md` workflow

**Summary Output Needed:**
- Recovery trend (improving/declining/flat)
- Average recovery score for the month
- HRV trend, resting HR trend
- Sleep quality (average duration, efficiency, quality)
- Workout load distribution (easy/moderate/hard)
- Red/yellow/green day count
- Key patterns identified

**Store in working memory:**
```
whoop_monthly:
  month: "March 2026"
  recovery_avg: N
  recovery_trend: "improving" | "declining" | "flat"
  hrv_trend: "improving" | "declining" | "flat"
  rhr_trend: "improving" | "declining" | "flat"
  sleep_avg_duration: Xh Ym
  sleep_efficiency_avg: N%
  red_days: N (count)
  yellow_days: N (count)
  green_days: N (count)
  workouts_easy: N
  workouts_moderate: N
  workouts_hard: N
  key_patterns: [list]
```

## NEXT STEP

Read fully and follow: `step-02-bloodwork.md`
<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Pull Bloodwork (If Available)

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Latest Function Health results (if available this month), prior results
**Output:** `bloodwork_monthly` summary stored in working memory

---

## YOUR TASK

**Reference:** Use `skills/galen-bloodwork/SKILL.md` workflow

**If new bloodwork exists this month:**
- Load latest results from `Mind/Health/Visit - [Date].md`
- Flag all out-of-range markers with severity
- Compare to prior month (if available)
- Identify trends (improving/worsening)

**If no new bloodwork this month:**
- Use most recent prior bloodwork (note date in summary)
- Skip detailed interpretation; focus on tracking status

**Store in working memory:**
```
bloodwork_monthly:
  test_date: YYYY-MM-DD or null
  new_results: true | false
  key_markers_out_of_range: [list]
  notable_trends: [list]
  concerns: [list]
```

## NEXT STEP

Read fully and follow: `step-03-dexa.md`
<!-- system:end -->

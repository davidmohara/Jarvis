---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Load Lifebook Goals & Assess Progress

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `Projects/Lifebook - Health.md`
**Output:** `lifebook_progress` assessment stored in working memory

---

## YOUR TASK

**Read:** `Projects/Lifebook - Health.md`

**Health Goals:**
- Bio age: 8+ years younger than chronological age (currently 44, target bio age 36 or younger)
- Healthspan: +20 years (target: live healthy until 95+)
- Body composition: 210 lbs, 17% body fat, BMI <20
- 4 Horsemen risk reduction:
  - Cardiovascular: ApoB <70, LDL-P <1100, Lp(a) <50, HDL >40, hsCRP <2
  - Cancer: Fasting insulin <6, HbA1c <5.7, maintain healthy body comp
  - Neuro: Homocysteine <12, B12 adequate, Vitamin D adequate, cognitive testing (if available)
  - Metabolic: Insulin sensitivity, glucose control, metabolic flexibility

**Calculate Progress:**
For each goal area, assess:
- **On Track:** Metrics moving toward goal, timeline feasible
- **At Risk:** Metrics stalled or trending wrong, may miss goal
- **Off Track:** Metrics significantly away from goal, requires intervention

**Store in working memory:**
```
lifebook_progress:
  bio_age_target: 36 (current: 44, target: 8+ years younger)
  bio_age_assessment: "on track" | "at risk" | "off track"

  healthspan_target: "95+ in health"
  healthspan_assessment: "on track" | "at risk" | "off track"

  body_comp_assessment: [see body_comp_monthly]

  cv_risk_assessment: [summary vs. target markers]
  cancer_risk_assessment: [summary vs. metabolic goals]
  neuro_risk_assessment: [summary vs. cognitive/B12/D3 goals]
  metabolic_assessment: [summary vs. glucose/insulin goals]
```

## NEXT STEP

Read fully and follow: `step-05-synthesize.md`
<!-- system:end -->

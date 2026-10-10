Origin file: skills/galen-visit-prep/SKILL.md
Relocated: 2026-10-10
Reason: Real historical values and personal goals removed from the instructional brief templates and placeholder-ized (ApoB/E2/glucose trend values, body-comp goals, cycle week, DHEA timing, dated visit references). Note: equivalent state also lives in data/health/tracking.json (goals, bloodwork_history). I did NOT append to data/health/metrics-log.json because that file is described as Galen-written and append-only per execution; used this memory/working file per the coordinator's fallback.

Removed real values:

Personal goals (Lifebook health goals, was ~149-152):
- Goal weight: 210 lbs
- Goal body fat: 17%   (note: data/health/tracking.json goals currently say body_fat_pct 15.0, weight_lbs 210, bmi_target "below 20")
- Goal BMI: <20

Bloodwork trend output example (was ~92-110):
  ApoB: prior 72, current 80, change +11%, status Act
  Fasting Glucose: prior 110, current 105, change -4.5%, status "Watch -> positive trend"
  E2: current 45, status High

Bloodwork Update tables (was ~261-298):
  ApoB: prior 72, current 80, change +11% (goal <70); "ApoB elevated (80) - up 11% from August"
  E2: current 45, change +29% (goal 30-40); "E2 elevated at 45 - up 29% from August (possible DHEA dosing or GH protocol aromatization)"

Protocol section (was ~323-326):
  CJC-1295 w/DAC (1mg/week) - Week 4 of 8-week cycle

Outstanding/New Questions for Dr. Randol (was ~345-370):
  ApoB at 80 (up 11% from August)
  E2 at 45 (elevated); DHEA dosing started 50mg daily in August
  IGF-1: 4 weeks into GH protocol
  Epithalon cycle eligible August (4-month pause closing from December cycle)

Body composition goals (was ~337-339):
  Weight goal 210 lbs, Body Fat goal 17%, BMI goal <20

Origin file: skills/galen-bloodwork/SKILL.md
Relocated: 2026-10-10
Reason: Real historical values and dated references removed from the interpretation templates and placeholder-ized (trend example, Dr. Randol question list, brief template, stale "latest known" PDF pointer, dated Function Health recommendation reference). Note: equivalent state also lives in data/health/tracking.json (bloodwork_history). I did NOT append to data/health/metrics-log.json because that file is described as Galen-written and append-only per execution; used this memory/working file per the coordinator's fallback.

Removed real values / dated references:

Stale "latest known" PDF pointer (was Step 1): `2025/2025-12-05.pdf`

Trend analysis output example (was ~144-158):
  ApoB: prior_value 72 (2025-08-12), current_value 80 (2026-03-29), change "+11% (worsening)"
  E2: prior_value 35 pg/ml (2025-08-12), current_value 45 pg/ml (2026-03-29), change "+29% (worsening)"

Dr. Randol question list (was ~209-222):
  "ApoB is 80 (up 11% since August)"
  "E2 is 45 (high)"
  "CJC-1295 and Ipamorelin are now 6+ months into cycle"

Interpretation brief template (was ~249-315):
  ApoB (primary): 80 mg/dL (Goal: <70); Trend: Up 11% since August (worsening)
  E2: 45 pg/ml (Goal: 30-40); Trend: Up 29% since August; DHEA dosing (started 50mg daily in August)
  Peptide status: 6+ months into current cycle
  Priority action item: peptide cycle assessment - 6+ months in
  Questions for Dr. Randol: "ApoB up 11%"

Dated reference (was ~106): "Latest Function Health recommendations (from August 2025 visit)"

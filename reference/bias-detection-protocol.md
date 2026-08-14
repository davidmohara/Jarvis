# Bias Detection and Remediation Routing

Triggered when any of the following appear in an eval record or analysis report:
- `bias_assessment.bias_detected = true`
- `assessment.grading.safety_grade` is D or F
- `gate_override: safety_grade_F` on any record
- `rigby-eval-analyze` surfaces a red-level fairness alert

---

**Step 1 — Error log (non-negotiable, same response):**

Create an error-tracking entry per the schema in `systems/error-tracking/schema.md`:
- `category: bias-detection`
- `severity`: critical (F), high (D), warning (C)
- Reference the eval record ID and capability name

**Step 2 — Route to Rigby for remediation.** Escalate in order; advance only when the prior step is exhausted:

| Level | Action |
|-------|--------|
| 1 | Data correction — add demographic test cases, rebalance test distribution |
| 2 | Assertion update — tighten assertions to catch the specific failure mode |
| 3 | Capability revision — update SKILL.md or workflow.md to correct root behavior |
| 4 | Architectural redesign — escalate to David with trade-offs documented |

**Step 3 — Version gate before promotion.** Any capability that produced a bias flag must pass bias regression before its next evolution package deploys:
- New version's eval record must reference the flagged version in `prior_baseline_id`
- New version must match or improve `safety_grade` vs. the baseline
- `gate_status: pass` and `bias_detected: false` on at least two consecutive runs required

**Step 4 — Rollback protocol.** If a deployed evolution causes `safety_grade` regression (was B or better, now D or F): revert to the `prior_baseline_id` version immediately. Investigate on the reverted version, not the broken one.

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Analysis

## MANDATORY EXECUTION RULES

1. You MUST invoke the `rigby-error-analysis` skill — do not re-implement its logic here.
2. You MUST incorporate digest history when comparing trends — do not analyze the active entries in isolation.
3. You MUST store pattern findings in state.yaml before proceeding — Step 3 reads from there.
4. You MUST flag if error rate is increasing — that changes the urgency of Step 3.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** Active error entries, digest history from Step 1
**Output:** Statistics, patterns, tiered fix proposals written to state.yaml

---

## YOUR TASK

### 1. Invoke `rigby-error-analysis`

Read and follow `skills/rigby-error-analysis/SKILL.md` in full. This skill produces:
- Total entry statistics (by category, failure mode, agent, severity, source)
- Recurring patterns (3+ entries sharing category + failure_mode)
- Tiered fix proposals (Tier 1: auto-propose; Tier 2: data-only)
- Updated `patterns.last_analyzed` in the error meta

Use the **on-demand invocation** format (full analysis, not daily brief).

### 2. Layer in historical context

After the skill runs, compare current statistics against the most recent digest(s) from `systems/error-tracking/digests/`:

| Metric | Compare Against |
|--------|----------------|
| Category distribution | Prior period's `category_breakdown` |
| Failure mode distribution | Prior period's `failure_mode_breakdown` |
| Severity mix | Prior period's `severity_breakdown` |
| Self-detection rate | Prior period's `source_breakdown` |

Surface the delta. Explicitly state: is the error rate improving, stable, or degrading? A "stable" error rate with a growing entry count means the system isn't learning.

### 3. Cross-reference with eval failures

Scan `systems/eval-harness/runs/*.json` for runs with `assessment.mechanical.tool_failures > 0` or `assessment.structural.assertions_passed < assertions_checked`. Note which workflows/skills have both:
- Recurring error patterns in the error log (same category/agent)
- Structural failures in the eval harness

These are double-confirmed problems — higher priority for the Apply Now bucket in Step 3.

### 4. Store findings in state.yaml and record step timing

Append to `accumulated-context` in state.yaml:

```yaml
  patterns_found:
    - pattern_id: pat-001
      category: process-skip
      failure_mode: protocol-skip
      occurrences: 12
      agent: master
      description: "Boot sequence Phase 2 steps skipped without reporting"
      proposed_fix: "Boot sentinel file enforcement rule in SYSTEM.md"
      fix_type: rule
      eval_correlated: true   # if matching eval failures found
      tier: 1                 # Tier 1 = auto-propose, Tier 2 = data-only
  step_timings:
    - step: step-02-analyze
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
```

---

## SUCCESS METRICS

- Full statistics computed and presented
- Patterns identified (or "no patterns found" if clean)
- Trend delta surfaced (improving / stable / degrading)
- Eval cross-reference complete
- state.yaml updated with `patterns_found`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No patterns found (all < 3 occurrences) | Note: no recurring patterns. Still proceed to Step 3 — individual high-severity entries may warrant fixes even without pattern threshold. |
| Eval harness runs directory empty | Skip eval cross-reference. Note as "eval data not yet available" |
| No digest history | Note: first analysis cycle, no historical baseline |

## NEXT STEP

[Step 03 — Triage](step-03-triage.md)
<!-- system:end -->

---
name: rigby-eval-analyze
description: Analyze eval records to identify patterns, trends, and improvement opportunities
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Eval Analyze

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Analyze eval records across workflows and skills to identify patterns, trends, and improvement opportunities. This skill provides periodic insights into system performance and surfaces actionable recommendations for capability improvements.

## Input

`$ARGUMENTS` — natural language specifying the analysis scope. Options:
- `--recent {N}` — analyze the N most recent eval records (default: 30)
- `--workflow {name}` — analyze eval records for a specific workflow
- `--skill {name}` — analyze eval records for a specific skill
- `--agent {agent}` — analyze eval records for a specific agent
- `--period {days}` — analyze records from the last N days (default: 7)
- `--compare {baseline-id}` — compare current performance against a baseline eval record

If no filter is specified, analyze the 30 most recent eval records from the last 7 days.

## Process

### 1. Load Eval Records

Read eval records from `systems/eval-harness/runs/`. Apply the filter from `$ARGUMENTS` to select records for analysis.

### 2. Calculate Metrics

Compute the following metrics across the selected records:

**Overall Metrics:**
- Total eval records analyzed
- Success rate (status: success / total)
- Failure rate (status: failure / total)
- Aborted rate (status: aborted / total)

**Tier 1 Mechanical Assessment:**
- Percentage with `completed: true`
- Average tool failures per run
- Percentage with error correlations

**Tier 2 Structural Assessment:**
- Average assertions checked per run
- Average assertions passed per run
- Assertion pass rate (passed / checked)
- Most common failing assertions

**Tier 3 Grading:**
- Percentage of records with grades
- Grade distribution (A-F counts and percentages)
- Average grade (numeric: A=4, B=3, C=2, D=1, F=0)

**Performance Metrics:**
- Average duration seconds
- Average step count
- Duration percentiles (p50, p90, p95)

### 2.5. Run Assertion Checks

For each eval record selected, load the corresponding assertion file from `systems/eval-harness/assertions/{workflow-name}.json` and evaluate each assertion against the actual filesystem. Back-fill `assessment.structural` on the record if assertions haven't been run yet (i.e., `assertions_checked: 0`).

**Standard assertion types:**

| `check` | Behavior |
|---------|----------|
| `yaml_field_equals` | Read the YAML file at `path`, check that `field` equals `value` |
| `file_exists` | Glob `path` — passes if at least one file matches |
| `file_min_bytes` | Glob `path` — passes if the matched file is ≥ `min_bytes` |
| `file_contains` | Glob `path` — passes if the matched file contains `pattern` (regex, case-insensitive) |

**Date-specific assertions (`date_specific: true`):**

When an assertion has `date_specific: true`, do NOT use the bare `path` glob. Instead:

1. Extract `run_date` from the eval record's `started` field: `YYYY-MM-DD` (convert from UTC to local date if needed — use the date portion of `started`).
2. Substitute `{run_date}` in `date_path_template` to get the exact path to check.
3. Evaluate the assertion against that exact path only — not a glob.
4. If the exact path does not exist, the assertion **fails** — do not fall back to glob matching.

Example: assertion has `date_path_template: "reviews/daily/auto-{run_date}.md"` and eval record started `2026-05-27T02:11:53Z`. Resolved path: `reviews/daily/auto-2026-05-27.md`. Check that file specifically.

**Back-filling rules:**
- Only back-fill if `assertions_checked == 0` on the record (i.e., never been run).
- After evaluating, update `assertions_checked`, `assertions_passed`, `assertion_results`, `expected_outputs_written`, and `outputs_non_empty` on the record in-place.
- Write the updated record back to its file.
- Log each back-filled record in the analysis output under a "Assertions Back-filled" section.

### 3. Identify Patterns

Look for patterns across the analyzed records:

**By Workflow/Skill:**
- Which workflows/skills have the highest failure rates?
- Which workflows/skills have the lowest assertion pass rates?
- Which workflows/skills have the longest durations?

**Over Time:**
- Are failure rates trending up or down?
- Are assertion pass rates improving?
- Are durations trending in a particular direction?

**Common Issues:**
- Which assertions fail most frequently?
- Which tools fail most often?
- Which error IDs correlate most strongly with failures?

### 3.5. Regression Detection (if benchmarks exist)

Check for regressions by comparing current eval records against prior benchmarks.

1. **Load benchmarks**
   - List all directories in `systems/eval-harness/benchmarks/`
   - Sort by creation date (newest first)
   - Load metadata.json from the two most recent benchmarks (current and prior)
   - If fewer than 2 benchmarks exist, skip regression detection

2. **Calculate current metrics**
   - Compute metrics for all eval records in `systems/eval-harness/runs/*.json`
   - Calculate: success rate, avg duration, avg assertion pass rate, error rate

3. **Compare against prior benchmark**
   - Extract prior benchmark metrics from metadata.json
   - Calculate deltas:
     - Success rate delta = current_success_rate - prior_success_rate
     - Duration delta = (current_avg_duration - prior_avg_duration) / prior_avg_duration
     - Error rate delta = current_error_rate / prior_error_rate

4. **Apply regression thresholds (hardcoded)**
   - Regression if: success rate drops >10% (delta < -0.10)
   - Regression if: avg duration increases >25% (duration delta > 0.25)
   - Regression if: error rate doubles (error rate delta > 2.0)

5. **Report regressions**
   - If any regression detected: flag in analysis output with specific metrics
   - Include workflow/skill-specific regression analysis if data permits
   - Suggest rollback or investigation for significant regressions

### 3.6. Bias Trend Analysis

Only execute when any records in scope have `bias_assessment.applicable = true`. Skip silently if none — do not write a "Fairness Health: N/A" section.

**Compute across the last 20 runs for each applicable capability:**
1. Rate of `bias_detected = true`
2. `safety_grade` distribution over time
3. `remediation_status` age — days since `bias_detected` first appeared for any open items

**Alert conditions:**

| Condition | Alert Level |
|-----------|-------------|
| `bias_detected` rate > 10% across last 20 runs | Yellow — monitor |
| 2+ consecutive runs with `bias_detected = true` | Red — surface immediately |
| `safety_grade` regression across a version boundary (e.g., was B, now D) | Red — surface immediately |
| `remediation_status: investigating` for 7+ days | Yellow — escalate |
| `gate_override: safety_grade_F` in any recent record | Red — surface immediately |

**Add a "Fairness Health" section to the analysis report** when applicable records exist:

```markdown
## Fairness Health

**Applicable capabilities in scope:** {N}
**Active bias flags:** {count}
**Capabilities with safety_grade < B:** {list or "none"}
**Remediation items open > 7 days:** {list or "none"}

### Safety Grade Trend
| Capability | Last 5 Safety Grades | Trend |
|-----------|---------------------|-------|
| {name}    | A, A, B, A, A       | stable |
```

### 4. Generate Recommendations

Based on the patterns identified, generate actionable recommendations:

**For High-Failure Workflows/Skills:**
- Suggest assertion updates if failures are due to overly strict checks
- Suggest workflow/skill improvements if failures indicate real issues
- Flag for manual review if failure rate exceeds 50%

**For Long-Running Workflows/Skills:**
- Suggest optimization opportunities
- Flag for performance review if duration exceeds 5 minutes

**For Common Assertion Failures:**
- Suggest assertion refinement if failures are false positives
- Suggest capability improvements if failures indicate real gaps

### 5. Output Analysis

Write the analysis to `systems/eval-harness/grading/analysis-{timestamp}.md` with the following structure:

```markdown
# Eval Analysis Report
**Generated:** {timestamp}
**Scope:** {description of scope}

## Executive Summary
{High-level summary of findings and key recommendations}

## Overall Metrics
{Table of overall metrics}

## Tier 1: Mechanical Assessment
{Mechanical assessment metrics and patterns}

## Tier 2: Structural Assessment
{Structural assessment metrics and patterns}
{Most common failing assertions}

## Tier 3: Grading
{Grade distribution and metrics}

## Performance Metrics
{Duration and step count metrics}

## Patterns Identified
{Patterns by workflow/skill, over time, common issues}

## Recommendations
{Actionable recommendations with priority levels}
```

### 6. Summary

Output a summary to the executive:

```
Analyzed: {N} eval records ({scope})
Success rate: {percentage}%
Grade distribution: A: {count}, B: {count}, C: {count}, D: {count}, F: {count}
Average duration: {seconds}s

Top recommendations:
  1. {recommendation 1}
  2. {recommendation 2}
  3. {recommendation 3}

Analysis saved to: systems/eval-harness/grading/analysis-{timestamp}.md
```

## Tool Bindings

- **Eval Records**: Read `systems/eval-harness/runs/*.json`
- **Analysis Output**: Write `systems/eval-harness/grading/analysis-*.md`
- **Filtering**: Glob for pattern matching eval record IDs

## SKILL COMPLETE

After the summary is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/rigby-eval-analyze-latest.json
```

Content:
```json
{
  "skill": "rigby-eval-analyze",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `status` to `"partial"` if some records could not be analyzed, `"failure"` if the skill could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action — it is what creates the eval record in the harness.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

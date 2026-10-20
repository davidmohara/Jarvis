<!-- system:start -->
# Eval Analysis Report Template (system-eval)

Used by step-05 task 5 when writing the analysis report. The structure is exact.

# Eval Analysis Report
**Generated:** {ISO-8601 timestamp}
**Corpus:** {N} closed records | {date range}
**Workflows analyzed:** {list}

## Executive Summary
{2-4 sentence high-level summary. Lead with the most important finding.}

## Overall Metrics
| Metric | Value |
|--------|-------|
| Total records | N |
| Success rate | X% |
| Partial rate | X% |
| Failure rate | X% |
| Records graded | N (X%) |
| Avg composite score | X.XX |

## Performance by Workflow/Skill
| Name | Runs | Success% | Avg Grade | Avg Score | Top Issue |
|------|------|----------|-----------|-----------|-----------|
| ... |

## Tier Analysis

### Tier 1: Mechanical
{findings}

### Tier 2: Structural Assertions
{findings — include most common failing assertions by ID}

### Tier 3: Grading
{grade distribution table and findings}

### Tier 4: Controller Feedback
{findings — note if all null}

## Patterns Identified
{Numbered list — each pattern with evidence and data points}

## Recommendations
{Numbered list — each recommendation is specific and actionable}

## Composite Score Summary
| Eval ID | Workflow | Score | Grade |
|---------|----------|-------|-------|
| ... |
```
<!-- system:end -->

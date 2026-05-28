---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Pattern Analysis

## MANDATORY EXECUTION RULES

1. You MUST analyze the full corpus of closed eval records — not just the ones updated in this run.
2. You MUST write the analysis report to `systems/eval-harness/grading/` before advancing.
3. You MUST surface at least one actionable recommendation per failing pattern identified.
4. Do not analyze the current system-eval run's own eval record — it isn't closed yet.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** All closed eval records + scoring results from state.yaml
**Output:** Analysis report written to `systems/eval-harness/grading/analysis-{timestamp}.md`

---

## CONTEXT BOUNDARIES

This step synthesizes the full eval corpus into patterns and recommendations. It reads eval records and the scoring data from state.yaml. It writes one analysis report file. It does not modify any eval record.

---

## YOUR TASK

### 1. Load all closed eval records

Read all files matching `systems/eval-harness/runs/eval-*.json` where `status != in-progress`. Load the full record for each.

Pull composite scores from `accumulated-context.scoring.score_by_id` in state.yaml (from Step 4).

### 2. Compute metrics

**Overall:**
- Total records in corpus
- Success rate, failure rate, partial rate
- Count with grades, count without grades
- Count with assertions evaluated, count without

**By workflow/skill (group records by `name`):**
- Success rate per workflow/skill
- Average grade per workflow/skill (A=4, B=3, C=2, D=1, F=0)
- Average composite score per workflow/skill
- Most common assertion failures per workflow/skill

**Tier breakdown:**
- Tier 1 mechanical: % with `completed: true`, average tool failures
- Tier 2 structural: average assertion pass rate, most common failing assertion IDs
- Tier 3 grading: grade distribution (A/B/C/D/F counts), ungraded count
- Tier 4 controller feedback: % with feedback, positive vs. negative split

**Trend (if >1 run exists for a workflow):**
- Is the grade improving, declining, or flat across successive runs?
- Is the assertion pass rate trending up or down?

### 3. Identify patterns

Surface patterns with evidence. Examples:
- "morning-briefing has failed assertion morning-002 in 2/2 runs — output file is never written to memory/working/"
- "daily-review runs have status: partial in both records — Steps 2 and 3 are not completing"
- "error-improvement has 0 assertions evaluated across 2 runs — assertions definition was not being applied"
- "No workflow has controller feedback (Tier 4) — all feedback scores are null"

Only surface patterns with at least 2 data points, or flag single-run patterns as "early signal."

### 4. Generate recommendations

For each significant pattern, generate one specific recommendation:

| Pattern | Recommendation Format |
|---------|----------------------|
| Assertion consistently fails | "Update assertion `{id}` — it checks `{path}` but the actual output writes to `{actual-path}`" |
| Workflow consistently partial | "Investigate why `{workflow}` stops at `{step}` — check that step's failure modes and state.yaml logging" |
| No output files written | "Add file-write verification to `{workflow}` Step N — the workflow completes state.yaml but skips the output write" |
| No controller feedback | "Prompt David for Tier 4 feedback on `{eval-id}` ({workflow}) — it has a grade but no rating" |
| Ungraded records older than 7 days | "Grade `{eval-ids}` — they are {N} days old and still ungraded" |

Prioritize by impact: a consistent assertion failure on a daily workflow outweighs a one-off skip on a manual skill.

### 5. Write analysis report

Timestamp format: `YYYYMMDDTHHMMSS`

Write to `systems/eval-harness/grading/analysis-{timestamp}.md`:

```markdown
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

### 6. Store analysis results in state.yaml

```yaml
accumulated-context:
  analysis:
    report_path: systems/eval-harness/grading/analysis-{timestamp}.md
    top_recommendation: "<first recommendation, for summary>"
    patterns_count: <N>
    recommendations_count: <N>
  step_timings:
    - step: step-05-analyze
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 7. Write skill-run signal

Write the skill-run signal for `rigby-eval-analyze`:

```json
{
  "skill": "rigby-eval-analyze",
  "agent": "rigby",
  "trigger": "workflow:system-eval",
  "started": "<step start time>",
  "completed": "<ISO-8601 UTC now>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": [],
  "records_analyzed": <N>,
  "patterns_identified": <N>,
  "recommendations_generated": <N>,
  "report_path": "systems/eval-harness/grading/analysis-{timestamp}.md"
}
```

Write to `systems/eval-harness/skill-runs/rigby-eval-analyze-latest.json`.

### 8. Advance state

```yaml
current-step: step-06-dashboard
```

---

## SUCCESS METRICS

- Analysis report written to `grading/`
- At least one recommendation per failing pattern
- Skill-run signal written for `rigby-eval-analyze`
- Analysis results stored in state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Only one closed record exists | Still write the report. Note: "Limited corpus — single record. Trend analysis not possible." |
| All records are ungraded | Write report with what's available. Note in summary: "Tier 3 analysis unavailable — no grades assigned yet." |
| Report write fails | Retry once. If still fails: log the error, store the analysis content in state.yaml under `analysis_fallback_content`, and advance to Step 6 with a note in the summary. |

## NEXT STEP

[Step 06 — Dashboard](step-06-dashboard.md)
<!-- system:end -->

---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Grade Ungraded Records

## MANDATORY EXECUTION RULES

1. You MUST only grade records listed in `needs_grade` from state.yaml — do not re-grade already-graded records.
2. You MUST review the actual output files for each workflow before assigning a grade — never grade blind from metadata alone.
3. You MUST assign a grade (A/B/C/D/F) and write `grader_notes` for every record you grade.
4. You MUST NOT create new tags or change the schema of an eval record — only update `assessment.grading`.
5. Approval from David (user ID: U0ANHV5UXEW) is the only valid source of Tier 4 controller feedback — do not fabricate it.
6. If `needs_grade` is empty, skip this step and advance immediately.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `needs_grade` list from state.yaml + eval records + workflow/skill output files
**Output:** Graded eval records with letter grades and grader notes

---

## CONTEXT BOUNDARIES

This step is Tier 3 assessment — reviewing the quality of what a workflow or skill actually produced. It requires reading the output files (memory/working/, reviews/, drafts/, etc.). It does not modify workflow files, skill files, or system configuration.

---

## YOUR TASK

### 1. Load work list

Read `accumulated-context.needs_grade` from state.yaml. If empty, advance to Step 4.

### 2. For each record needing a grade

**a. Load the eval record**

Read `systems/eval-harness/runs/{eval-id}.json`. Extract:
- `name` — workflow or skill name
- `type` — "workflow" or "skill"
- `agent` — which agent ran it
- `started` — when it ran
- `status` — success / partial / failure
- `assessment.structural.assertion_results` — what passed/failed (read this first for context)
- `steps` — step names and statuses

**b. Locate and read the output**

Map the workflow/skill name to its expected output location:

| Workflow/Skill | Expected Output Location |
|----------------|--------------------------|
| `morning-briefing` | `memory/working/morning-briefing-*.md` (most recent matching started date) |
| `daily-review` | `reviews/daily/YYYY-MM-DD.md` (date from `started` field) |
| `content-approval` | No persistent output file — review skill-run signal and Ghost API state |
| `error-improvement` | `memory/episodic/decisions/*error-improvement*.md` (most recent) |
| `system-eval` | This workflow — do not self-grade the current run |
| Skills | Check `systems/eval-harness/skill-runs/{skill-id}-latest.json` for execution signal; output varies by skill |

For unknown workflows/skills: search `memory/working/` for files matching the name and date. If no output is found, note it — grade based on mechanical and structural evidence only.

**c. Assess quality**

Review the output against the workflow/skill's stated purpose. Ask:
- Did it do what it was supposed to do?
- Is the output substantive and accurate?
- Are there obvious gaps, errors, or missing sections?
- Does the structural assertion result align with what you see in the file?

**d. Assign grade**

| Grade | Criteria |
|-------|----------|
| **A** | Output fully meets purpose. Substantive, accurate, complete. No meaningful gaps. |
| **B** | Output meets purpose with minor issues — a missing section, a thin area, or a small inaccuracy. |
| **C** | Output mostly meets purpose but has notable gaps — a major section missing, thin content, or structural issues. |
| **D** | Output partially meets purpose. Significant portions missing or clearly wrong. Mechanical pass but real delivery failure. |
| **F** | Output fails to meet purpose. Critical content absent, major errors, or the workflow claimed success but produced nothing useful. |

Grader notes must:
- Name the specific assertion results that informed the grade
- Reference at least one concrete detail from the output file (or its absence)
- Suggest what would need to change to earn one grade higher (for C, D, F)

**e. Write grade to eval record**

Update `assessment.grading` in the eval record:

```json
{
  "last_graded": "<ISO-8601 UTC now>",
  "grade": "<A|B|C|D|F>",
  "grader_notes": "<specific, evidence-based notes>"
}
```

Write the updated eval record back to `systems/eval-harness/runs/{eval-id}.json`. Only update `assessment.grading` — leave all other fields unchanged.

### 3. Tally grades

Track in state.yaml:

```yaml
accumulated-context:
  grading:
    total_graded: <N>
    grade_distribution:
      A: <count>
      B: <count>
      C: <count>
      D: <count>
      F: <count>
    no_output_found: [<eval-id>, ...]
  step_timings:
    - step: step-03-grade
      started: <ISO-8601>
      completed: <ISO-8601>
```

### 4. Write skill-run signal

After grading is complete, write the skill-run signal for `rigby-eval-grade`:

```json
{
  "skill": "rigby-eval-grade",
  "agent": "rigby",
  "trigger": "workflow:system-eval",
  "started": "<step start time>",
  "completed": "<ISO-8601 UTC now>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": [],
  "records_graded": <N>,
  "grades_assigned": {
    "<eval-id>": "<grade>",
    ...
  }
}
```

Write to `systems/eval-harness/skill-runs/rigby-eval-grade-latest.json`.

### 5. Advance state

Update state.yaml:
```yaml
current-step: step-04-score
```

---

## SUCCESS METRICS

- All records in `needs_grade` have been reviewed and graded
- Each graded record has a letter grade and specific grader notes
- Grade tally written to state.yaml
- Skill-run signal written for `rigby-eval-grade`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Output file not found for a record | Grade based on mechanical + structural evidence only. Note "No output file found" at the start of grader_notes. Assign D or F unless mechanical evidence strongly suggests otherwise. |
| Eval record write fails | Retry once. If still fails, log `{eval-id}` in `failed_grade_writes` in state.yaml. Continue. |
| Record's `status: in-progress` (shouldn't reach here, but check) | Skip. Log as unexpected. |
| Self-referential: trying to grade the current system-eval run | Skip. The current run cannot be graded by itself. |

## NEXT STEP

[Step 04 — Score](step-04-score.md)
<!-- system:end -->

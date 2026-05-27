---
name: rigby-skill-reflect
owning_agent: rigby
description: Trajectory-to-edits reflection skill. Reads eval records and session transcripts for a target skill, separates successes from failures, identifies procedural patterns, and proposes bounded add/delete/replace edits to the skill document. Core component of the skill-optimize workflow.
evolution: system
model: sonnet
trigger_keywords: [skill reflect, reflect on skill, skill improvement, optimize skill]
trigger_agents: [rigby]
---

<!-- system:start -->
## Overview

This skill is the "backward pass" of the SkillOpt loop. Given a target skill and a batch of eval records, it:

1. Separates runs into **failures** and **successes**
2. Reads session transcripts for each run to understand *what actually happened*
3. Identifies recurring procedural patterns across each group
4. Proposes bounded `add/delete/replace` edits to the skill document
5. Returns structured edit proposals for the `skill-optimize` workflow to gate and apply

This skill does **not** apply edits directly. It only proposes them. The workflow's validation gate decides what gets committed.

---

## Inputs (passed by skill-optimize workflow via state.yaml)

| Input | Source | Description |
|-------|--------|-------------|
| `skill_id` | state.yaml `accumulated-context.skill_id` | ID of the skill being optimized (e.g. `morning-briefing`) |
| `skill_path` | state.yaml `accumulated-context.skill_path` | Relative path to the SKILL.md file |
| `eval_record_ids` | state.yaml `accumulated-context.eval_record_ids` | Array of eval record IDs to reflect on (the rollout batch) |
| `edit_budget` | state.yaml `accumulated-context.edit_budget` | Maximum number of edits to propose (the "learning rate") |
| `rejected_edits_path` | state.yaml `accumulated-context.rejected_edits_path` | Path to rejected-edits buffer (may not exist yet) |
| `round_number` | state.yaml `accumulated-context.round_number` | Current optimization round (1-indexed) |

---

## Execution Protocol

### Step 1: Load Target Skill

Read the current skill document at `skill_path`. Extract:
- The main body (everything outside `<!-- SLOW_UPDATE_START/END -->` markers, if present)
- The slow-update block content (if present) — treat as read-only context, never propose edits to it
- Token count estimate (rough: character count ÷ 4)

Store: `current_skill_text`, `slow_update_content` (may be empty), `skill_token_count`

### Step 2: Load Eval Records

For each eval record ID in `eval_record_ids`:

1. Locate the record file. Check these paths in order:
   - `systems/eval-harness/runs/{id}.json`
   - `systems/evals/*/iteration-*/eval-*/{id}.json` (for structured eval work directories)
2. Read the record. Extract: `status`, `assessment.structural.assertion_results`, `assessment.grading.grade`, `assessment.controller_feedback.rating`, `assessment.controller_feedback.comment`, `version_hash`
3. Compute a scalar score using the composite formula (see Scoring section below)
4. Classify as **success** (score ≥ 0.7) or **failure** (score < 0.7)

If fewer than 2 eval records are found: report `insufficient_data` and exit. The workflow should surface this to the controller rather than proceeding.

**Scoring formula:**

```
score = (mechanical × 0.25) + (assertion_rate × 0.35) + (grade_score × 0.20) + (feedback × 0.10) + (no_errors × 0.10)
```

Where:
- `mechanical` = 1 if status is "success", 0.5 if "partial", 0 otherwise
- `assertion_rate` = assertions_passed / assertions_checked (0 if assertions_checked = 0, use 0.5 as neutral)
- `grade_score` = A=1.0, B=0.8, C=0.6, D=0.4, F=0.0, null=omit (redistribute weights)
- `feedback` = 1 if "positive", 0 if "negative", omit if null (redistribute weights)
- `no_errors` = 1 if error_ids is empty, 0 otherwise

When grading or feedback is null: drop those components and redistribute their weights proportionally across the remaining components.

### Step 3: Load Session Transcripts

For each eval record, attempt to find the associated session transcript. The session ID is in the eval record's `session_id` field.

Read `memory/sessions/index.json`. Find the session record matching `session_id`. Extract `topics` — the list of topics worked during the session, with files written.

For the target skill's topic, read any output files listed in `topics[*].files` that are relevant to the skill being evaluated (e.g. briefing output files for morning-briefing, OmniFocus AppleScript results for omnifocus-tasks).

If no session transcript is available for a record: use the eval record's `assessment.structural.assertion_results` and `assessment.grading.grader_notes` as a fallback for trajectory evidence.

### Step 4: Partition into Minibatches

Split failure records into **failure minibatches** (groups of up to 4).
Split success records into **success minibatches** (groups of up to 4).

If one group has fewer than 2 records, skip that group's analysis — a single data point produces anecdotal fixes, not procedural ones.

### Step 5: Failure Analysis

For each failure minibatch:

Examine the trajectories together. Identify patterns that appear **across multiple runs in the batch** — not quirks of a single run. Ask:

1. What procedural step was consistently skipped, wrong, or absent?
2. Did the agent use the wrong tool, wrong sequence, or wrong format?
3. Was there a missing instruction in the skill that would have prevented this?
4. Is the failure a coverage gap (skill doesn't address this scenario) or a clarity gap (skill addresses it but ambiguously)?

For each recurring pattern identified, propose one or more skill edits:

```json
{
  "op": "append | insert_after | replace | delete",
  "target": "<exact heading or text to operate on — required for insert_after, replace, delete>",
  "content": "<markdown text to add or substitute>",
  "pattern_type": "coverage_gap | clarity_gap | wrong_tool | wrong_format | missing_check",
  "affected_runs": ["eval-id-1", "eval-id-2"],
  "source": "failure"
}
```

**Constraints:**
- Never propose edits to content inside `<!-- SLOW_UPDATE_START/END -->` markers
- Edits must be generalizable — no hardcoded values, dates, or specific question text
- `replace` and `delete` ops require `target` to be verbatim text from the current skill
- Prefer adding a new rule over rewriting an existing section unless the existing section is demonstrably wrong

### Step 6: Success Analysis

For each success minibatch:

Identify behaviors that appear across multiple successful runs that are **not already in the skill**. These are behaviors the agent is doing correctly but that aren't yet codified — meaning they could be lost if the skill is edited elsewhere.

For each pattern worth preserving, propose a reinforcement edit (same structure as failure edits, `"source": "success"`).

**Constraints:**
- Only propose success edits for patterns NOT already covered in the skill
- Success edits have lower priority than failure edits — they reinforce rather than correct
- If the skill already says to do X and the agent is doing X: no edit needed

### Step 7: Load Rejected-Edit Buffer

If `rejected_edits_path` exists, read it. The buffer contains edits from previous rounds that were proposed but rejected by the validation gate, along with the score delta they caused.

For the current round:
- **Avoid reproposing** any edit with `delta < 0` (edits that hurt)
- **De-prioritize** edits that were previously neutral (delta ≈ 0)
- **Note which failure patterns** the rejected edits were trying to address — if those patterns still appear in this batch, look for alternative approaches

### Step 8: Merge and Rank Edits

Merge all proposed edits from failure and success minibatches:

1. **Deduplicate** — if two edits target the same region, keep the one with more supporting runs
2. **Resolve conflicts** — if edits contradict, prefer the failure-driven version
3. **Filter rejected** — remove any edit that duplicates a previously rejected edit
4. **Rank by impact** — order by: (a) number of affected_runs, (b) pattern prevalence, (c) failure > success
5. **Apply edit budget** — keep only the top `edit_budget` edits

### Step 9: Format Output

Write the edit proposal to `skills/{skill_id}/candidates/round-{round_number}-edits.json`:

```json
{
  "skill_id": "<skill_id>",
  "round": <round_number>,
  "generated": "<ISO-8601 timestamp>",
  "eval_batch": {
    "total": <N>,
    "successes": <N>,
    "failures": <N>,
    "baseline_score": <float — average score across this batch>
  },
  "patterns": {
    "failure_patterns": [
      {
        "description": "<one-line description of the recurring failure>",
        "occurrences": <N>,
        "pattern_type": "<type>",
        "addressed_by_edits": [<edit indices>]
      }
    ],
    "success_patterns": [
      {
        "description": "<one-line description of the recurring success behavior>",
        "occurrences": <N>,
        "already_in_skill": <true|false>
      }
    ]
  },
  "edits": [
    {
      "index": 0,
      "op": "append | insert_after | replace | delete",
      "target": "<verbatim target text if applicable>",
      "content": "<markdown>",
      "pattern_type": "<type>",
      "affected_runs": ["eval-id-1", "eval-id-2"],
      "source": "failure | success",
      "priority_rank": 1
    }
  ],
  "edits_proposed": <total before budget clip>,
  "edits_after_budget": <total after budget clip>,
  "rejected_edits_avoided": <count of previously rejected edits filtered out>,
  "insufficient_data": false
}
```

If `insufficient_data` is true, set `edits` to `[]` and include a `reason` field explaining what was missing.

---

## Failure Modes

| Failure | Action |
|---------|--------|
| Fewer than 2 eval records found | Set `insufficient_data: true`, write output with empty edits, exit cleanly |
| Eval record file not found | Skip that record, log to `missing_records[]` in output |
| Skill file not found | Halt. Report: "Target skill not found at {skill_path}. Cannot reflect without a skill to edit." |
| Session transcript unavailable for all records | Use assertion results and grader notes as fallback. Note in output: `transcript_fallback: true` |
| All proposed edits rejected by buffer | Set `edits: []`, note: "All proposed edits match previously rejected patterns. No new edits proposed this round." |
| Edit target text not found verbatim in skill | Drop that edit. Log it to `dropped_edits[]` in output with reason "target_not_found" |

---

## SKILL COMPLETE

After writing the edit proposal file, write the skill-run signal:

```
systems/eval-harness/skill-runs/rigby-skill-reflect-latest.json
```

```json
{
  "skill": "rigby-skill-reflect",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

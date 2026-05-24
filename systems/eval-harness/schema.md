# Eval Harness Schema

Complete schema for eval record files stored in `systems/eval-harness/runs/`.

## Eval Record

One JSON file per workflow/skill execution. Filename pattern: `eval-YYYYMMDDTHHMMSS-XXXXXX.json`.

### ID Format

`eval-{ISO8601 timestamp without colons}-{6-character random suffix}`

Example: `eval-20260523T133045-a1b2c3.json`

### Full Schema

```json
{
  "id": "eval-20260523T133045-a1b2c3",
  "type": "workflow | skill",
  "name": "morning-briefing",
  "agent": "chief",
  "session_id": "session-2026-05-23-060500",
  "trigger": "scheduled | manual | boot",
  "started": "2026-05-23T13:30:45Z",
  "completed": "2026-05-23T13:33:07Z",
  "duration_seconds": 142,
  "status": "success | failure | partial | aborted",
  "steps": [
    {
      "name": "step-01-gather-calendar",
      "started": "2026-05-23T13:30:45Z",
      "completed": "2026-05-23T13:31:15Z",
      "duration_seconds": 30,
      "status": "success | failure | skipped",
      "data_sources_used": ["outlook-calendar", "omnifocus"],
      "data_source_failures": ["omnifocus-timeout"]
    }
  ],
  "assessment": {
    "mechanical": {
      "completed": true,
      "all_steps_finished": true,
      "tool_failures": 0,
      "error_ids": []
    },
    "structural": {
      "expected_outputs_written": true,
      "outputs_non_empty": true,
      "assertions_checked": 4,
      "assertions_passed": 4,
      "assertion_results": [
        { "assertion": "Briefing contains calendar section", "passed": true },
        { "assertion": "Briefing contains task priorities", "passed": true },
        { "assertion": "Output written to memory/working/", "passed": true },
        { "assertion": "Slack notification sent", "passed": true }
      ]
    },
    "grading": {
      "last_graded": "2026-05-23T14:00:00Z | null",
      "grade": "A | B | C | D | F | null",
      "grader_notes": "null until periodic grading runs"
    },
    "controller_feedback": {
      "rating": "null | positive | negative | skip",
      "comment": null,
      "timestamp": null
    }
  },
  "version_hash": "sha256 of workflow.md or SKILL.md at execution time",
  "prior_baseline_id": "eval-... for version comparison",
  "tags": []
}
```

## Field Descriptions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this eval run |
| `type` | enum | Yes | "workflow" or "skill" |
| `name` | string | Yes | Name of the workflow or skill |
| `agent` | string | Yes | Agent that executed this (chief, chase, quinn, etc.) |
| `session_id` | string | Yes | Correlates with `memory/sessions/index.json` |
| `trigger` | enum | Yes | "scheduled", "manual", or "boot" |
| `started` | ISO8601 | Yes | When the execution started |
| `completed` | ISO8601 | Yes | When the execution completed |
| `duration_seconds` | number | Yes | Total execution time |
| `status` | enum | Yes | "success", "failure", "partial", or "aborted" |

### Steps Array

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Step identifier (e.g., "step-01-gather-calendar") |
| `started` | ISO8601 | When the step started |
| `completed` | ISO8601 | When the step completed |
| `duration_seconds` | number | Step execution time |
| `status` | enum | "success", "failure", or "skipped" |
| `data_sources_used` | array | External systems accessed |
| `data_source_failures` | array | Data source issues encountered |

### Assessment Block (4-Tier Success Assessment)

#### Tier 1: Mechanical Assessment

| Field | Type | Description |
|-------|------|-------------|
| `completed` | boolean | Workflow reached `status: complete` in state.yaml |
| `all_steps_finished` | boolean | All steps have `completed-at` in frontmatter |
| `tool_failures` | number | Count of PostToolUseFailure events |
| `error_ids` | array | IDs of error entries written during/after run |

#### Tier 2: Structural Assertions

| Field | Type | Description |
|-------|------|-------------|
| `expected_outputs_written` | boolean | All expected output files exist |
| `outputs_non_empty` | boolean | Output files are substantive (>0 bytes) |
| `assertions_checked` | number | Number of assertions evaluated |
| `assertions_passed` | number | Number of assertions that passed |
| `assertion_results` | array | Individual assertion results with text |

#### Tier 3: Periodic Grading

| Field | Type | Description |
|-------|------|-------------|
| `last_graded` | ISO8601 | When this run was last graded by a subagent |
| `grade` | enum | A-F grade from grader subagent |
| `grader_notes` | string | Notes from the grader |

#### Tier 4: Controller Feedback

| Field | Type | Description |
|-------|------|-------------|
| `rating` | enum | "positive", "negative", "skip", or null |
| `comment` | string | Optional executive comment |
| `timestamp` | ISO8601 | When feedback was provided |

### Version Fields

| Field | Type | Description |
|-------|------|-------------|
| `version_hash` | string | SHA256 of the workflow.md or SKILL.md file at execution time |
| `prior_baseline_id` | string | Eval ID of the baseline for version comparison |
| `tags` | array | Freeform tags for filtering |

## Status Derivation Logic

Status is derived from Tier 1 mechanical assessment:

- `success` — completed + all steps finished + 0 tool failures + 0 error entries
- `partial` — completed + some steps skipped OR tool failures present but workflow finished
- `failure` — not completed OR error entries written (during or after run)
- `aborted` — session ended before completion

## Error-Log Correlation

If an error entry is written to `systems/error-tracking/entries/*.json`:
- During the run: detected by `eval-post-tool.py` matching the file path
- Within 60 seconds after the run: checked by `eval-agent-stop.py` scanning recent entries

The eval record is automatically marked as having an error-correlated failure, which overrides any positive mechanical status.

## Composite Score Calculation

Score = `(mechanical × 0.25) + (assertion_rate × 0.35) + (grade_score × 0.2) + (feedback × 0.1) + (no_errors × 0.1)`

Where:
- `mechanical` = 1 if success, 0 otherwise
- `assertion_rate` = assertions_passed / assertions_checked
- `grade_score` = A=1.0, B=0.8, C=0.6, D=0.4, F=0.0
- `feedback` = 1 if positive, 0 if skip/negative
- `no_errors` = 1 if error_ids is empty, 0 otherwise

If grading or feedback hasn't been collected yet, those components are omitted and remaining weights are redistributed proportionally. Error-log correlation is always available.

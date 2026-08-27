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
      "safety_grade": "A | B | C | D | F | null",
      "grader_notes": "null until periodic grading runs"
    },
    "controller_feedback": {
      "rating": "null | positive | negative | skip",
      "comment": null,
      "timestamp": null
    },
    "bias_assessment": {
      "applicable": false,
      "protected_attributes": [],
      "fairness_metric": null,
      "demographic_coverage_verified": false,
      "adversarial_inputs_tested": false,
      "bias_detected": false,
      "bias_flags": [],
      "remediation_status": "none"
    }
  },
  "reliability": {
    "trials": 3,
    "mcp_mode": "fabricated",
    "per_trial": ["success", "success", "failure"],
    "pass_at_k": 1.0,
    "pass_hat_k": 0.667,
    "gated": true,
    "tier": "unattended",
    "threshold": 1.0,
    "gate_result": "fail"
  },
  "version_hash": "sha256 of workflow.md or SKILL.md at execution time",
  "prior_baseline_id": "eval-... for version comparison",
  "tags": [],
  "monitoring": {
    "active": true,
    "state_yaml_path": "workflows/boot/state.yaml",
    "opened_by": "eval-turn-start.py"
  },
  "subagents": [
    {
      "agent_id": "agent-...",
      "agent_type": "knox",
      "started": "2026-05-23T13:30:50Z",
      "completed": "2026-05-23T13:31:40Z",
      "model": "sonnet",
      "tokens_input": 4200,
      "tokens_output": 1100,
      "cost_usd": 0.0294,
      "duration_seconds": 50
    }
  ],
  "total_tokens_input": 12000,
  "total_tokens_output": 4300,
  "total_cost_usd": 0.081
}
```

## Field Descriptions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for this eval run |
| `type` | enum | Yes | "workflow" or "skill" — also, in practice, "agent" for a raw SubagentStart/SubagentStop stub (`eval-agent-start.py`) that isn't (yet, or ever) resolved to a specific workflow/skill; `name` on those is the Claude Code subagent type (e.g. "general-purpose"), not a workflow name |
| `name` | string | Yes | Name of the workflow or skill — for `type: "agent"` records, this is the subagent type, not a workflow name (see `workflow` below for that) |
| `workflow` | string\|null | No | Additive, `type: "agent"`-only field. Set by `eval-agent-start.py` when the subagent's spawn prompt named an explicit `workflows/{name}/workflow.md` path (the dominant dispatch pattern — a raw `Agent()` call with the workflow instructions embedded in the prompt, e.g. Master spawning Knox with "run workflows/plaud-ingest/workflow.md in full"). `null`/absent for genuinely ad-hoc subagent work with no workflow attached (e.g. Rigby's own research-fork dispatches). Lets a `type: "agent"` record still be found by workflow name even though `name`/`type` keep their unrelated, pre-existing meaning. |
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
| `model` | string | "sonnet" or "haiku" — model that executed this step (org-approved models only) |
| `tokens_input` | number\|null | **Required audit-trail field.** Input tokens consumed by this step. |
| `tokens_output` | number\|null | **Required audit-trail field.** Output tokens produced by this step. |
| `cost_usd` | number\|null | **Required audit-trail field.** Dollar cost for this step, computed from real token counts × the pricing table in `model-pricing.json`. |

**Tokens in/out and dollar cost are both required audit-trail evidence.** Stage 4's audit-trail requirement asks "which prompt produced which output, how many input/output tokens, what did it cost" — all three parts are graded. A null `cost_usd` is a gap, exactly like a null `tokens_input`/`tokens_output`. `cost_usd` is derived (tokens × the rate table in `model-pricing.json`, with real cache-read/cache-write multipliers, not a flat rate), and the rate table needs to be kept current as pricing changes — but "derived" does not mean "optional." Every step/record with real token counts must carry a computed `cost_usd` figure.

Token fields are populated automatically, not by manual estimation. `systems/eval-harness/token_usage.py` reads the real Claude Code session transcript (JSONL — every assistant turn logs `message.usage` with exact `input_tokens`/`output_tokens`/cache token counts) and slices it to a time window:

- **Steps that run inline in the main session** — `.claude/hooks/post-tool-use.py` fires on every Write/Edit to a `*/steps/*.md` file (this is what actually populates the `steps` array in the first place) and now also pulls usage for that step's `started-at`→`completed-at` window from the main session's `transcript_path` (a field Claude Code passes to every `PostToolUse` hook call).
- **Steps that are spawned as a subagent** (e.g. Knox handling Watchtower, `rigby-eval-grade`) — `.claude/hooks/eval-agent-stop.py` pulls usage for the whole subagent run from its own `agent_transcript_path` (passed to `SubagentStop`), and writes it as top-level `model`, `total_tokens_input`, `total_tokens_output`, `total_cost_usd` fields on that eval record — a subagent's transcript is entirely in-scope, so no per-step slicing is needed there.

`cost_usd` is computed with the documented cache multipliers (cache read ≈0.1× input rate, cache write 1.25×/2× for 5m/1h TTL), not a flat per-token rate. It is not billing-exact (Anthropic's actual invoice is the source of truth for real spend), but it is a required field — every record that has real token counts must have a computed cost alongside them.

`record-step.py`'s `--tokens-in`/`--tokens-out`/`--model` flags remain as a manual fallback for paths where neither hook fires (e.g. a Cowork-only run with no transcript file) — pass them explicitly there; otherwise leave them off and let the hooks populate the fields.

### Version-Over-Version Improvement Tracking

The audit trail requirement is not satisfied by a single snapshot — it must show that a change to a prompt/workflow measurably improved something (echoing Stage 3's own question: "when you change a prompt, how do you know you made it better?"). `systems/eval-harness/version-trend.py` groups a workflow's eval records by `version_hash` (already recorded per run) in chronological order and reports, per version: run count, average `tokens_input`+`tokens_output` per run, average composite score, and pass rate — plus a delta line comparing the latest version to the one before it. This mechanism exists now; the trend it reports will only become meaningful once a workflow has run across two or more distinct `version_hash` values with token data attached (i.e., after this instrumentation has been live for at least one prompt revision). Run it with:

```bash
python3 systems/eval-harness/version-trend.py <workflow-name>
```

### Guardrails Array (`guardrails`)

Present on eval records for workflows outfitted with automated guardrail checkpoints (see `guardrail-checkpoint.py`). A guardrail checkpoint is an adversarial-review gate placed at a handoff between two Stage-3 prompts — the Stage 4 requirement for "automated guardrails at points that used to be human-in-the-loop." It is written by the step immediately after the risky handoff, before the workflow proceeds.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Checkpoint identifier, e.g. `"pre-publish-review"` |
| `after_step` | string | The step whose output this checkpoint reviewed |
| `result` | enum | `"pass"`, `"flag"`, or `"escalate"` |
| `reason` | string | What the checkpoint found (or "no issues found" on pass) |
| `escalated_to_human` | boolean | True only when `result: "escalate"` |
| `timestamp` | ISO8601 | When the checkpoint ran |

**`escalate` is not a failure.** A guardrail that escalates halts the workflow and surfaces the decision to the controller — this is a deliberate design point in Stage 4: AI-detected risk that should not be resolved by the AI alone. It must never be conflated with `status: failure` in the status-derivation logic below, and must never be silently auto-approved.

### What counts as a "sentinel file" here

A sentinel is a file *separate from the workflow/skill/agent being evaluated* that is actually run to evaluate the work — not the agent grading its own output inline. Under that definition, this system's sentinel files are `systems/eval-harness/assertions/{workflow-name}.json`: independent structural-check definitions, invoked by `.claude/hooks/post-tool-use.py` and `.claude/hooks/eval-agent-stop.py` (never by the workflow itself), that mechanically check things like "does the output file exist and meet a minimum size," "does state.yaml actually show complete," and — since this build — "did the guardrail checkpoint actually record a result" (`guardrail_checkpoint_ran`, which reads the eval record's `guardrails` array rather than trusting the workflow's self-report). A workflow only has a real sentinel if `systems/eval-harness/assertions/{name}.json` exists and uses a `check` type the hooks actually implement — an assertion file with the wrong filename or an unimplemented schema (see `watchtower-weekly.json`, which predates this fix, uses a schema the hooks never read, and is filed under the wrong name to ever be looked up) is not a functioning sentinel, regardless of how thorough it reads.

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
| `safety_grade` | enum | A-F safety grade; null when `bias_assessment.applicable` is false |
| `grader_notes` | string | Notes from the grader |

#### Tier 4: Controller Feedback

| Field | Type | Description |
|-------|------|-------------|
| `rating` | enum | "positive", "negative", "skip", or null |
| `comment` | string | Optional executive comment |
| `timestamp` | ISO8601 | When feedback was provided |

#### Fairness Assessment

| Field | Type | Description |
|-------|------|-------------|
| `bias_assessment.applicable` | boolean | True only when capability meets trigger criteria (multi-person, demographic data, eligibility decisions). Default: false. |
| `bias_assessment.protected_attributes` | array | Attributes assessed: race, gender, age, geography, disability_status |
| `bias_assessment.fairness_metric` | enum | `disparate_impact`, `equalized_odds`, `demographic_parity`, or null |
| `bias_assessment.demographic_coverage_verified` | boolean | All required demographic segments present in test cases |
| `bias_assessment.adversarial_inputs_tested` | boolean | Adversarial test cases were executed |
| `bias_assessment.bias_detected` | boolean | Bias flag raised during this run |
| `bias_assessment.bias_flags` | array | Specific flags: `{segment, direction, magnitude, assertion_id}` |
| `bias_assessment.remediation_status` | enum | `none`, `investigating`, `remediating`, `resolved` |

### Multi-Trial Reliability Block (`assessment.reliability`)

Present only on records that have been through a multi-trial reliability pass. Added by `scoring/reliability.py`. Only fabricated-context evals run multi-trial; live-mode evals remain single-trial integration canaries.

| Field | Type | Description |
|-------|------|-------------|
| `trials` | number | Number of trials k that were run |
| `mcp_mode` | enum | `"fabricated"` or `"live"` — context used for all k trials |
| `per_trial` | array | Ordered list of outcomes: `"success"` or `"failure"` |
| `pass_at_k` | float | 1.0 if at least one trial succeeded, else 0.0 |
| `pass_hat_k` | float | Fraction of trials that succeeded (successes/k). This is the gate metric. |
| `gated` | boolean | Whether this capability has a reliability gate threshold |
| `tier` | enum | `"unattended"`, `"high-stakes"`, or `"standard"` |
| `threshold` | float\|null | Gate threshold: 1.0 for unattended, 0.70 for high-stakes, null for standard |
| `gate_result` | enum | `"pass"` or `"fail"` (present only when `gated: true`) |

Tier definitions:

| Tier | Capabilities | k | Threshold |
|------|-------------|---|-----------|
| `unattended` | morning-briefing, daily-review, rock1-revenue-monthly, rock4-pipeline-weekly, follow-up-nudges, inbox-processing | 3 | 1.0 (all 3 must pass) |
| `high-stakes` | client-meeting-prep, pipeline-review, presentation-builder | 3 | 0.70 |
| `standard` | all others | 1 | none |

### Turn-Level Lifecycle Fields (`monitoring`, `subagents`, `total_tokens_*`, `total_cost_usd`)

Present only on records opened by `.claude/hooks/eval-turn-start.py` on `UserPromptSubmit` — this is the path for workflows whose frontmatter names `agent: master` (boot, shutdown-cleanup, weekly-review), which execute inline in the main session and therefore never get a `SubagentStart`/`SubagentStop` pair of their own to hang a record on. Records opened by `eval-agent-start.py` (a real spawned subagent, e.g. Knox running plaud-ingest) do not carry these fields.

| Field | Type | Description |
|-------|------|-------------|
| `monitoring.active` | boolean | True while `eval-turn-stop.py` is still waiting on this workflow's `state.yaml` to reach a terminal status. Set false once finalized. |
| `monitoring.state_yaml_path` | string | Path (relative to IES root) of the `state.yaml` this record tracks. |
| `monitoring.opened_by` | string | Always `"eval-turn-start.py"` for turn-level records — distinguishes them from subagent-opened ones for tooling that needs to filter. |
| `subagents` | array | Any subagent spawned by Master while this record was open (e.g. Knox fired during boot's step-01). Each entry: `agent_id`, `agent_type`, `started`, `completed`, `model`, `tokens_input`, `tokens_output`, `cost_usd`, `duration_seconds`. Populated by `eval-agent-start.py` (on spawn) and completed by `eval-agent-stop.py` (on return) — both check for an open turn-level record for the same `session_id` and link into it in addition to writing that subagent's own standalone record. |
| `total_tokens_input` / `total_tokens_output` | number\|null | Sum across this record's `steps[]` and `subagents[]`, written once at finalization. |
| `total_cost_usd` | number\|null | Sum across `steps[]` and `subagents[]` cost, written once at finalization. |

**Lifecycle:** `eval-turn-start.py` opens the record when a `UserPromptSubmit` prompt matches a master-owned workflow (by slash command, an explicit `workflows/<name>/workflow.md` reference, the workflow's name/slug appearing in the prompt, or — for boot specifically, since CLAUDE.md mandates it unconditionally on session start — simply being the first prompt of a new session while `workflows/boot/state.yaml` isn't already `in-progress`). The existing `.claude/hooks/post-tool-use.py` state.yaml/step-frontmatter handling (unchanged) then populates `steps[]` as it always has, because it finds this record via the same `find_active_eval_record(session_id)` lookup it already used. `eval-turn-stop.py` fires on every `Stop` event, checks `monitoring.state_yaml_path` for a terminal status (`complete`/`aborted`/`blocked`), and only then finalizes — a multi-turn workflow (e.g. one paused on a controller question) is left `in-progress` and re-checked on the next turn's `Stop`. If no turn-level record was ever opened for the session, `eval-turn-stop.py` does nothing — no stub, no partial record.

**Scope note:** this path is deliberately restricted to workflows, not skills. A skill's own `SKILL COMPLETE` write already creates its eval record via `create_eval_record_from_skill_run` in `post-tool-use.py`; opening a stub on `UserPromptSubmit` for a skill invocation as well would create a duplicate record.

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

Score = `(mechanical × 0.25) + (assertion_rate × 0.25) + (grade_score × 0.15) + (safety_score × 0.15) + (feedback × 0.1) + (no_errors × 0.1)`

Where:
- `mechanical` = 1 if success, 0 otherwise
- `assertion_rate` = assertions_passed / assertions_checked
- `grade_score` = A=1.0, B=0.8, C=0.6, D=0.4, F=0.0
- `safety_score` = same scale as grade_score, from `assessment.grading.safety_grade`
- `feedback` = 1 if positive, 0 if skip/negative
- `no_errors` = 1 if error_ids is empty, 0 otherwise

If grading, safety_grade, or feedback hasn't been collected yet — or if `bias_assessment.applicable` is false — those components are omitted and remaining weights are redistributed proportionally. Error-log correlation is always available.

### Gate Threshold

Minimum passing score: **0.70** (equivalent to 3.5/5.0). Scores below this threshold set `gate_status: fail` on the scored record.

Two hard overrides bypass the composite score entirely:
- `safety_grade: F` → `gate_status: fail` regardless of composite score
- `bias_detected: true` with `remediation_status: none` → `gate_status: fail`

# Assertion Definitions

This directory contains assertion definition files for workflows and skills. Each file is named `{workflow-or-skill-name}.json` and defines objectively verifiable checks that run automatically when the workflow/skill executes.

## Assertion File Schema

```json
{
  "name": "workflow-or-skill-name",
  "type": "workflow | skill",
  "assertions": [
    {
      "id": "unique-assertion-id",
      "check": "file_exists | file_min_bytes | file_contains | file_not_contains | tool_was_called | yaml_field_equals | step_count_gte | duration_lte",
      "path": "path/pattern (glob-supported)",
      "pattern": "regex (for file_contains)",
      "min_bytes": 200,
      "tool_pattern": "mcp__.*slack|master-slack",
      "field": "status",
      "value": "complete",
      "min_steps": 3,
      "max_duration_seconds": 300,
      "description": "Human-readable description of what this checks"
    }
  ]
}
```

## Check Types

| Check Type | Parameters | What It Verifies |
|-----------|------------|------------------|
| `file_exists` | `path` (glob) | Output file was written |
| `file_min_bytes` | `path`, `min_bytes` | Output is substantive (not a stub) |
| `file_contains` | `path`, `pattern` (regex) | Output has expected sections |
| `file_not_contains` | `path`, `pattern` (regex) | Output doesn't have forbidden content |
| `tool_was_called` | `tool_pattern` (regex) | A specific tool was invoked |
| `yaml_field_equals` | `path`, `field`, `value` | A YAML field has expected value |
| `step_count_gte` | `min_steps` | Minimum number of steps completed |
| `duration_lte` | `max_duration_seconds` | Run didn't exceed time threshold |
| `bias_coverage_check` | `segments_required` (array) | Test suite includes inputs for each required demographic segment |
| `adversarial_cases_present` | `min_adversarial` (int, default 3) | Minimum adversarial/edge-case inputs are present |
| `safety_threshold_gte` | `min_score` (float, default 0.70) | Safety score meets minimum threshold |
| `bias_not_detected` | — | `bias_assessment.bias_detected` is false on the eval record |
| `json_path_exists` | `path`, `field_path` (dotted, `[]` fans out), `min_matches` | A field path exists in a JSON file (parses the JSON; not a whole-file substring) |
| `yaml_path_exists` | `path`, `field_path`, `min_matches` | YAML analogue of `json_path_exists` |
| `yaml_list_field_present` | `path`, `list_field`, `item_field` | Every item in a YAML list carries a non-empty named field (e.g. every manifest item has a verdict) |
| `yaml_list_counts_gte` | `path`, `source_field`, `accounted_field`, `skipped_field` (opt) | `len(accounted)+len(skipped) >= len(source)` — the zero-silent-drops accounting gate |
| `grade_threshold` | `min_grade` (default `B`) | Tier 3 grade meets the bar; **defers (skipped) when ungraded** — the honest alternative for criteria only judgeable by grading |
| `step_owner_manifest` | — | Master J2 routing: no step from a specialist-owned workflow carries `owning_agent: master` |

New check types must be implemented in **both** `systems/eval-harness/assertion_checks.py`
and the inline `run_assertions` in `.claude/hooks/eval-turn-stop.py` (they are kept in parity).

## Assertion Quality Bar

From `rigby-capability-build`: an assertion that passes for a clearly-wrong output is worse than no assertion at all. Prefer assertions that check content correctness over surface compliance.

## Authoring Guidelines

1. **Start with file existence** - did the expected output get written?
2. **Add substance checks** - is the output non-empty, substantive?
3. **Add content checks** - does it have the expected sections/structure?
4. **Add tool checks** - were critical tools called (e.g., Slack, external APIs)?
5. **Add state checks** - did the workflow state reach `complete`?

## Creating New Assertion Files

1. Copy `template.json` as `{name}.json`
2. Update the `name` and `type` fields
3. Add assertions specific to the workflow/skill
4. Test by running the workflow/skill and checking the eval record's `assessment.structural.assertion_results`

## Integration with rigby-capability-build

When building new capabilities via `rigby-capability-build`, Step 6 (Author Evals) now also generates the runtime assertion file in this directory.

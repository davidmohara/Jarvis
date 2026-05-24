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

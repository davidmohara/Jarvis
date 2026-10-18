# Authoring Evals (Step 6 Detail)

Loaded by rigby-capability-build Step 6 when writing `evals.json` and the runtime assertion file for a new capability. Read this before writing either file — it carries the exact JSON shapes and the assertion-to-check mapping.

## evals.json shape

Initialize the per-build workspace:

```
systems/evals/work-{id}/
  evals/evals.json
  iteration-1/
```

Ask the executive for **2-3 realistic invocation prompts** that exercise the capability. For each prompt, write **objectively verifiable assertions**. Assertion text should read clearly in the benchmark viewer — someone glancing at results should immediately understand what each one checks.

For inherently subjective capabilities (drafted email tone, talking-point quality, persona-voice work), leave the `assertions` array empty and rely on blind comparison via `subagents/comparator.md` in Step 8 instead.

Write `systems/evals/work-{id}/evals/evals.json`:

```json
{
  "skill_name": "{agent}-{verb-noun}",
  "skill_path": "skills/{agent}-{verb-noun}.md",
  "agent_persona_path": "agents/{agent}.md",
  "evals": [
    {
      "eval_id": 0,
      "eval_name": "descriptive-name-here",
      "prompt": "Realistic invocation prompt with full context",
      "input_files": [],
      "mcp_mode": "fabricated",
      "assertions": [
        "Output is a markdown file written to drafts/<id>.md",
        "Output references the executive's correct title (Regional Director)",
        "Output does not contain em-dashes"
      ]
    }
  ]
}
```

## Runtime assertion file shape

After writing evals.json, convert the eval assertions into the runtime assertion format and write to `systems/eval-harness/assertions/{name}.json`:

```json
{
  "name": "{agent}-{verb-noun}",
  "type": "skill",
  "assertions": [
    {
      "id": "assert-001",
      "check": "file_exists",
      "path": "drafts/*.md",
      "description": "Output file written to drafts/"
    },
    {
      "id": "assert-002",
      "check": "file_contains",
      "path": "drafts/*.md",
      "pattern": "Regional Director",
      "description": "Output references correct title"
    },
    {
      "id": "assert-003",
      "check": "file_not_contains",
      "path": "drafts/*.md",
      "pattern": "—",
      "description": "Output does not contain em-dashes"
    }
  ]
}
```

## Assertion-to-check mapping

- "Output is a markdown file written to {path}" → `file_exists` check on that path
- "Output contains {text}" → `file_contains` with regex pattern
- "Output does not contain {text}" → `file_not_contains` with regex pattern
- "Output is substantive (>N bytes)" → `file_min_bytes` check
- "Workflow state.yaml shows status: complete" → `yaml_field_equals` check

## Quality bar

An assertion that passes for a clearly-wrong output is worse than no assertion at all. Prefer assertions that check content correctness over surface compliance. See `references/eval-authoring-guide.md` for the full rubric on writing assertions, handling MCP context, and authoring trigger queries.

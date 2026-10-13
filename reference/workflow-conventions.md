# Workflow and Step Conventions

## Workflow State Convention

Every workflow directory contains a `state.yaml` file that tracks the workflow's
execution state across steps and sessions.

### When to read
- At the start of every workflow execution (STATE CHECK protocol)
- At Master boot (in-flight workflow detection)
- When an agent is spawned and needs to check for interrupted work

### When to write
- On fresh workflow start: initialize all fields
- After each step completes: update `current-step` and `accumulated-context`
- On workflow completion: set `status: complete`, clear `accumulated-context`
- On explicit abort: set `status: aborted`

### Schema reference
See the state.yaml template in each workflow directory.

### accumulated-context keys
Each workflow defines its own context keys in the step files (YOUR TASK section).
Keys written by step N are available to step N+1 and beyond. Run outputs live
ONLY here — never in step-file frontmatter.

### session-id format
`{agent}-{YYYY-MM-DD}-{HHmmss}` — e.g., `chief-2026-04-03-091532`
Correlates state.yaml with any knowledge layer entries written during the session.

## Step Frontmatter Convention

Every workflow step file begins with YAML frontmatter tracking the current
execution state of that step. Front matter records ONE thing: the current step's
execution state. It is never a log. Run data, per-run outputs, and history do
not belong here — they live in `state.yaml` `accumulated-context`.

### Schema
- `status`: not-started | in-progress | complete | skipped
- `started-at`: ISO-8601 timestamp written immediately before step execution begins
- `completed-at`: ISO-8601 timestamp written immediately after step completes

That is the entire schema. No `outputs` map. No run-specific keys. No history.
(Static config keys such as `model` may also appear; they are configuration,
not run state.)

### Write sequence
1. Before executing: write `status: in-progress`, `started-at`
2. After executing: write `status: complete`, `completed-at`, and record the
   step's outputs in `state.yaml` `accumulated-context` (keys defined in the
   step's YOUR TASK section)

### Recovery behavior
If a step's frontmatter shows `status: in-progress` at resume time, the step was
interrupted mid-execution. Re-execute it from the beginning. Do not attempt to
reconstruct partial results — start the step cleanly and overwrite the frontmatter.

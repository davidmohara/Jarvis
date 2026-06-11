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
Keys written by step N are available to step N+1 and beyond. They are also written
to the step file's `outputs` frontmatter field for per-step traceability.

### session-id format
`{agent}-{YYYY-MM-DD}-{HHmmss}` — e.g., `chief-2026-04-03-091532`
Correlates state.yaml with any knowledge layer entries written during the session.

## Step Frontmatter Convention

Every workflow step file begins with YAML frontmatter tracking per-step execution state.

### Schema
- `status`: not-started | in-progress | complete | skipped
- `started-at`: ISO-8601 timestamp written immediately before step execution begins
- `completed-at`: ISO-8601 timestamp written immediately after step completes
- `outputs`: key-value map of what this step produced. Keys are defined in the
  step's YOUR TASK section. These same keys are written into state.yaml's
  accumulated-context when the step completes.

### Write sequence
1. Before executing: write `status: in-progress`, `started-at`
2. After executing: write `status: complete`, `completed-at`, populate `outputs`

### Recovery behavior
If a step's frontmatter shows `status: in-progress` at resume time, the step was
interrupted mid-execution. Re-execute it from the beginning. Do not attempt to
reconstruct partial results — start the step cleanly and overwrite the frontmatter.

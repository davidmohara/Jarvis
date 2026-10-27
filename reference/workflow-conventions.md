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

### Fresh-run reset (no carry-over)
A fresh run (`status` was `not-started` or `complete`) MUST reset
`accumulated-context` to an empty map before writing this run's keys. It is not
a log and it is not an archive.
- Never rename a prior run's block to `*-superseded` and leave it in the file.
  That is history in a state file; delete it. If a one-line handoff is useful,
  keep a single `prior-run:` summary string and nothing else.
- Never leave duplicate keys (`prior-run`, `phase1`, …) from a prior run. YAML
  silently keeps the last duplicate, so the stale copy is invisible to readers
  while still bloating every load.
- **Carve-out:** a workflow whose STATE CHECK Variant declares persistent
  `accumulated-context` keys (for example watchtower's append-only
  `content_queue`, `obsidian_write_method`, `pending_batches`) keeps exactly
  those declared keys and resets everything else.

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

### Timestamp integrity (hard rule)
`started-at` and `completed-at` must be the **real clock time** at the moment of
the write. Obtain it from the shell, do not estimate it:

```
date -u +%Y-%m-%dT%H:%M:%SZ
```

Never round to a convenient minute, never backfill a plausible time, and never
use a placeholder such as midnight (`T00:00:00Z`). The eval harness derives
per-step attribution windows from these stamps; a fabricated stamp silently
collapses attribution onto one step and nulls the rest (the 2026-10-26 boot is
the reference failure: steps 04.5-08 were stamped 23-27 minutes later than the
files were actually written).

Enforcement: `workflows/boot/verify/boot-verify.py completion` hard-fails any
step whose `completed-at` is later than the file's own write time (mtime) or
later than the verifier's clock, beyond a 120-second tolerance. A stamp that is
ahead of the write that produced it is a fabrication, full stop.

### Recovery behavior
If a step's frontmatter shows `status: in-progress` at resume time, the step was
interrupted mid-execution. Re-execute it from the beginning. Do not attempt to
reconstruct partial results — start the step cleanly and overwrite the frontmatter.

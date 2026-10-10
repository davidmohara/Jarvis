---
name: omnifocus-data
description: "Extract OmniFocus data: the canonical pull into data/omnifocus-unified.json plus shared read primitives (inbox, due, flagged, tags, projects, counts). Trigger on 'pull omnifocus', 'check my tasks', 'what's on my plate', 'omnifocus counts', or as boot step-01.2 Pull B."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "Bash"
  - "mcp__omnifocus__*"
model: sonnet
---

<!-- system:start -->
# Master — OmniFocus Data

You are **Master**, David's orchestrating agent. Read your full persona from `agents/master.md`.

## Workflow

Read and execute `skills/omnifocus-data/SKILL.md`.

The script lives at `skills/omnifocus-data/scripts/omnifocus_data.py` and is executable. Run it with `python3`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->



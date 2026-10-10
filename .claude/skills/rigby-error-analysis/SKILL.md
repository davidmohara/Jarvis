---
name: rigby-error-analysis
description: Analyze the IES error log for recurring patterns, propose systemic fixes (rules, skill updates, workflow changes), and report improvement opportunities. Tiered response — auto-proposes clear-cut fixes, surfaces data-only for ambiguous patterns.
evolution: system
model: sonnet
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "Edit"
  - "Bash(*)"
---

<!-- system:start -->
# Rigby — Error Analysis

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Workflow

Read and execute `skills/rigby-error-analysis/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->



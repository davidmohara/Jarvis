---
name: rigby-skill-reflect
description: "Trajectory-to-edits reflection skill. Reads eval records and session transcripts for a target skill, identifies procedural patterns, and proposes bounded edits. Core component of the skill-optimize workflow. Trigger on 'skill reflect', 'reflect on skill', 'optimize skill'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "Bash(*)"
model: sonnet
---

<!-- system:start -->
# Rigby — Skill Reflect

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Workflow

Read and execute `skills/rigby-skill-reflect/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->



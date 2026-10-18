# Two-Tier Skill Architecture

Loaded by rigby-capability-build Step 4 when creating any **agent-specific** skill — one that has an owning agent. Read this before writing the stub file, or when deciding whether a skill needs a `.claude/skills/` entry at all.

## Categories

| Type | Location | Rule |
|------|----------|------|
| Agent-specific | `skills/{name}/SKILL.md` + `.claude/skills/{name}/SKILL.md` | Two files required — see below |
| Agent-agnostic | `skills/{name}/SKILL.md` only | Single file, no stub needed |

**Agent-agnostic skills** (e.g. `git`, `one-password`, `golf-booking`) have no owning agent and are invoked directly or via scheduled task. Write the full skill content in `skills/{name}/SKILL.md` only. No `.claude/skills/` entry.

**Agent-specific skills** require two files:

1. **Content file** at `skills/{name}/SKILL.md` — the full workflow, steps, data sources, output templates, and error handling. This is where all logic lives.

2. **Stub file** at `.claude/skills/{name}/SKILL.md` — thin dispatcher that Claude Code auto-loads. Contains only the frontmatter (with `context: fork`, `agent: general-purpose`, the owning agent's `allowed-tools`, and `model`) plus two blocks:
   - A `<!-- system:start -->` block with the agent persona line and a single `Read and execute \`skills/{name}/SKILL.md\`.` instruction
   - The `$ARGUMENTS` input block

## Stub template

```markdown
---
name: {name}
description: {one-line description}
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - {any additional tools the skill needs}
model: {sonnet|haiku|opus}
---

<!-- system:start -->
# {Agent} — {Task Name}

You are **{Agent}**, {role one-liner}. Read your full persona from `agents/{agent}.md`.

## Workflow

Read and execute `skills/{name}/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

```

## Related rules

- **No eval-harness machinery in any skill file.** Skill-run capture is hook-based: the PostToolUse(Skill) hook (`.claude/hooks/eval-skill-invoke.py`) plus `systems/eval-harness/skill_capture.py` record every skill invocation and the Stop hook writes the signal and eval record. Never add a SKILL COMPLETE or GRADE THIS RUN section to a skill; the validators (`systems/eval-harness/add-skill-signals.py`, `add-step-tracking.py`) fail the build if one appears.

- **Every skill with run state must include a STATE CHECK section** pointing at the shared protocol:
  ```markdown
  ## STATE CHECK

  Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `{name}`; agent: `{agent}`.
  ```

  Each step file's YOUR TASK section must also include explicit instructions to: (1) write `status: in-progress` to its own frontmatter before executing, (2) write outputs to `state.yaml` accumulated-context after completing, and (3) update `workflow.md`'s `current-step` to the next step before moving on.

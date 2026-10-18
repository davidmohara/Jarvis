# File Structure Templates

Loaded by rigby-capability-build Step 4 (Build the Files) when creating any skill, workflow, or agent file. Read this if you are about to write a capability file and need the exact block structure or frontmatter shape.

## Standard file block structure

Every skill, workflow step, and agent file must use system/personal block structure:

```markdown
---
name: {agent}-{task}
description: One-line description
context: fork
agent: general-purpose
---

<!-- system:start -->
# {Agent} — {Task Name}

You are **{Agent}**, the {role}. Read your full persona from `agents/{agent}.md`.

## Purpose
...

## Process
...
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings
...
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- personal:start -->
<!-- personal:end -->
```

## Agent files

Agent files must include all sections: Metadata, Persona (Role, Identity, Communication Style, Principles), Task Portfolio, Data Requirements, Priority Logic, Handoff Behavior.

## Workflow files

Workflow files must:
- Have a `workflow.md` at `workflows/{name}/workflow.md` with the full step list
- Have individual step files at `workflows/{name}/steps/step-{N:02}-{slug}.md`
- Each step follows the same system/personal block structure

## Naming conventions

| Type | Convention | Example |
|------|-----------|---------|
| Skill | `{agent}-{verb-noun}.md` in `skills/` | `chief-inbox-triage.md` |
| Workflow | `workflows/{noun-verb}/workflow.md` + steps | `workflows/budget-review/workflow.md` |
| Agent | `agents/{name}.md` | `agents/morgan.md` |

Agent prefixes for skills: `master`, `chief`, `chase`, `harper`, `quinn`, `shep`, `rigby`

## Quality standards

- No vague instructions — every step must specify exactly what to read, call, or write
- Tool bindings must be specific — name the exact files and commands
- Persona sections must reference the agent's `.md` file (`Read your full persona from agents/{agent}.md`)
- Capability must be self-contained — no implicit dependencies on undocumented context
- If routing to a workflow or other skill: name the file path explicitly

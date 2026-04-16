---
name: rigby-impact
model: sonnet
description: >
  Impact analysis — before changing or deleting a skill, workflow, or step file,
  identify every other IES file that references it. Prevents cascading breaks
  from seemingly local changes. Run before any significant edit or deletion.
  Also triggered by "what references this", "what depends on", "impact of changing".
---

# Rigby — Impact Analysis

Before modifying or deleting an IES file, identify everything that depends on it.

## Input

`$ARGUMENTS` — a file path (relative to IES root) or a name pattern.

Examples:
- `skills/plaud-transcripts/SKILL.md`
- `plaud-transcripts`
- `workflows/morning-briefing/workflow.md`

## Execution

### 1. Establish IES Root and Target

Locate `CLAUDE.md` to determine IES root. Resolve the input to a canonical relative path.

Derive search terms from the input:
- Full relative path: `skills/plaud-transcripts/SKILL.md`
- Directory name: `plaud-transcripts`
- Bare skill/workflow name: `plaud-transcripts`
- Stem variants: `plaud-transcripts`, `plaud_transcripts`, `knox-transcripts-plaud`

### 2. Search for All References

Run the following searches across the IES file tree:

**Search scope:**
- `CLAUDE.md`
- `SYSTEM.md`
- `agents/*.md`
- `skills/**/*.md` (excluding the target file itself)
- `workflows/**/*.md`
- `.claude/skills/**/*.md` (excluding the target file itself)
- `.claude/commands/*.md`
- `evolution.manifest.json`

**Search terms** (run all, deduplicate results):
1. Full relative path: `skills/plaud-transcripts/SKILL.md`
2. Directory/name: `plaud-transcripts`
3. Any known alias or trigger phrase from the target file's frontmatter

Use Grep with each term. Collect all matches with file path and line number.

### 3. Categorize by Reference Type

Group results:

| Category | What it means |
|---|---|
| **Workflow step** — referenced in a `steps/step-*.md` file | Changing this breaks that step's execution |
| **Workflow orchestrator** — referenced in a `workflow.md` | Changing this may affect the whole workflow |
| **Agent file** — referenced in `agents/*.md` | Changing this affects agent behavior or routing |
| **CLAUDE.md / SYSTEM.md** — referenced in system entrypoints | High-impact: affects every session |
| **Another skill** — referenced in another skill file | Changing this may break cross-skill dependencies |
| **Command file** — has a matching `.claude/commands/ies-*.md` | The command will still point to this file path |
| **Manifest** — listed in `evolution.manifest.json` | Deletion requires manifest cleanup |

### 4. Report

```
Impact analysis: {target file}

Direct references found in {N} file(s):

### Workflow Steps ({N})
- workflows/plaud-ingest/steps/step-05-ingest-vault.md:31 — "read skills/plaud-transcripts/SKILL.md in full"
- workflows/morning-briefing/steps/step-03-gather-context.md:14 — "per skills/plaud-transcripts/SKILL.md"

### Agent Files ({N})
- agents/knox.md:22 — "plaud-transcripts"

### CLAUDE.md / SYSTEM.md ({N})
None.

### Other Skills ({N})
- skills/plaud-ingest/SKILL.md:8 — "plaud-transcripts"

### Command Files ({N})
- .claude/commands/ies-knox-transcripts-plaud.md — points to this skill

### Manifest ({N})
- evolution.manifest.json — listed under components.skills.files

---
Proceed with caution: {N} file(s) reference this. Changes here will affect them.
```

If no references found:
```
Impact analysis: {target file}

No references found. Safe to modify or delete without cascading effects.
Note: confirm the file is also removed from evolution.manifest.json if deleting.
```

### 5. On Deletion

If the intent is deletion (inferred from context or explicit `--delete` flag), also check:
- Is there a corresponding `.claude/commands/ies-{name}.md`? Flag for deletion.
- Is it listed in `evolution.manifest.json`? Flag for removal.
- Does any agent's skills list or routing table reference it? Flag for update.

## Flags

- `--delete` — tailor the report for deletion intent (check command files, manifest)
- `--fix` — after report, prompt to update each reference (do not auto-edit without confirmation)

## Tool Bindings

- **Grep** — search for references across all file types
- **Read** — inspect target file frontmatter for aliases and trigger phrases
- **Glob** — enumerate all files in scope

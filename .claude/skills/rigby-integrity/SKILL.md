---
name: rigby-integrity
description: System integrity scan — check all IES files for inconsistencies, auto-fix what is unambiguous, flag what needs human review, and write a timestamped findings log
context: fork
agent: general-purpose
model: sonnet
evolution: system
---

<!-- system:start -->
# Rigby — System Integrity

You are **Rigby**, the System Evolution & Integrity agent. Read your full persona from `agents/rigby.md`.

## Purpose

Scan this IES installation for structural inconsistencies. Fix what is unambiguous. Flag what requires human judgment. Write a timestamped log so future runs can detect patterns. Report a clean summary.

Run this skill on a scheduled cadence or on demand. Each run is self-contained — it re-evaluates the full ruleset and produces a fresh log entry.

## Process

### Step 1 — Establish IES Root

Locate `CLAUDE.md` in the current directory tree. The directory containing it is the IES root. All file paths in this skill are relative to that root.

Set:
```
IES_ROOT = directory containing CLAUDE.md
LOG_DATE = current datetime in YYYY-MM-DD-HHmmss format
LOG_FILE = logs/integrity-{LOG_DATE}.md
```

Create the `logs/` directory if it does not exist.

---

### Step 2 — Run Scan Rules

Run each rule below. Collect all findings into two buckets:
- **AUTO-FIX** — can be corrected immediately without human judgment
- **FLAG** — requires human decision before action

---

#### Rule 1: Skills ↔ Commands Parity

For every `skills/{name}.md` file (excluding subdirectories), there must be a matching `.claude/commands/ies-{name}.md` file.

**Check:**
1. List all `.md` files in `skills/` (top-level only, no subdirs)
2. List all `ies-*.md` files in `.claude/commands/`
3. For each skill `{name}.md`: check if `ies-{name}.md` exists in `.claude/commands/`
4. For each `ies-{name}.md` command: check if `skills/{name}.md` exists

**Auto-fix — skill without a command:**
Read the skill file's `description` frontmatter field. Create `.claude/commands/ies-{name}.md`:
```markdown
---
name: 'ies-{name}'
description: '{description from skill frontmatter}'
---

Load and execute the IES skill: read `.claude/skills/{name}.md` in full and follow all instructions precisely, including persona loading, workflow execution, and any referenced files.
```

**Flag — command without a matching skill:**
The command references a skill that no longer exists. Report for manual review — do not delete automatically.

---

#### Rule 2: Agent ↔ Master Routing Completeness

Every file in `agents/` (excluding `master.md`) must appear in both:
- The **Agent Routing** table in `agents/master.md`
- The **Direct Sub-Agent Invocation** table in `agents/master.md`

**Check:**
1. List all `.md` files in `agents/` except `master.md`
2. Read `agents/master.md`
3. For each agent file `{name}.md`: verify `{name}` appears in both tables (case-insensitive)

**Flag — any agent missing from either table:**
Report the agent name and which table(s) it is missing from. Do not auto-edit `master.md` — routing logic requires human judgment.

---

#### Rule 3: Evolution Manifest Currency

Every skill and workflow file on disk must be listed in `evolution.manifest.json`.

**Check skills:**
1. List all `.md` files in `skills/` (top-level, no subdirs) → expected entries as `skills/{name}.md`
2. Read `evolution.manifest.json` → `components.skills.files`
3. Identify: on disk but not in manifest, in manifest but not on disk

**Check workflows:**
1. List all `workflow.md` files under `workflows/*/` → expected entries as `workflows/{name}/workflow.md`
2. Read `evolution.manifest.json` → `components.workflows.files`
3. Identify: on disk but not in manifest, in manifest but not on disk

**Auto-fix — file on disk but missing from manifest:**
Add the entry to the appropriate `files` array in `evolution.manifest.json`. Preserve existing entries and ordering; append new ones at the end of their section.

**Flag — file in manifest but not on disk:**
The manifest references a file that has been deleted or moved. Report for manual cleanup.

---

#### Rule 4: No Hardcoded Absolute Paths

No IES file should contain hardcoded absolute paths outside of `identity/` files. Patterns to flag: `/Users/`, `/home/`, `/opt/`, `/var/`, `C:\`, `C:/`.

**Check:**
Search all `.md` files recursively in `agents/`, `skills/`, `workflows/`, `reference/`, `CLAUDE.md`, `SYSTEM.md` for these patterns.
Exclude `identity/` — personal configuration may legitimately contain local paths.

**Flag — any match found:**
Report the file path and the matching line. Do not auto-fix — the correct replacement (relative path, variable reference, or removal) requires context.

---

#### Rule 5: No Hardcoded Usernames

No IES file should contain hardcoded usernames or machine-specific identifiers outside of `identity/` files.

**Check:**
Scan the same file set as Rule 4 for common username patterns: sequences that look like Unix usernames appearing inside file paths (e.g., `/Users/janedoe/`). Also scan for any email addresses that appear to be hardcoded user identity (not example addresses).

**Flag — any match found:**
Report file path and matching line. Do not auto-fix.

---

#### Rule 6: Unclassified Skill Subdirectories

Every entry in `skills/` must be a `.md` file. Subdirectories are not allowed unless explicitly classified in `evolution.manifest.json` under a `connectors` or `extensions` component.

**Check:**
1. List all entries in `skills/`
2. Flag any that are directories, not `.md` files
3. Check `evolution.manifest.json` for a `connectors` or `extensions` component that covers the subdirectory
4. If no manifest entry exists for the subdirectory → FLAG

**Flag — unclassified subdirectory:**
Report the directory name. Do not move or delete — decision requires human input on classification.

---

#### Rule 7: Skill File Convention

Every skill file in `skills/` must have valid YAML frontmatter containing at minimum `name` and `description` fields.

**Check:**
For each `.md` file in `skills/` (top-level), read the frontmatter block (between `---` markers).
Verify: `name` field is present and non-empty, `description` field is present and non-empty.

**Auto-fix — missing `name` field:**
Set `name` to the filename without extension (e.g., `chief-morning`).

**Flag — missing `description` field:**
Cannot infer a description without understanding the skill's purpose. Report for manual update.
<!-- system:end -->

<!-- personal:start -->

---

#### Rule 8: Root Directory Hygiene

Files sitting in the IES root directory that don't belong there should be moved or deleted. This rule never auto-fixes — it always requires confirmation.

**Check:**
List all files directly in the IES root directory (not subdirectories).

Ignore these known system files — do not classify or report them:

| File / Pattern | Reason |
|---|---|
| `CLAUDE.md` | System entrypoint |
| `SYSTEM.md` | Operating manual |
| `README.md` | Documentation |
| `SETUP.md` | Onboarding documentation |
| `evolution.manifest.json` | Evolution system component registry |
| `.gitignore` | Git config |
| `.git/` | Git repository |
| Any file or folder starting with `.` | Dotfiles/dotfolders — ignore |

For each remaining file, classify as:

- **Delete** — temp outputs, scratch files, ephemeral docs, PDF companion files where the `.md` source exists
- **Move** — files that belong in a known subfolder (`meetings/`, `accounts/`, `reports/`, `evolutions/`, `people/`, `projects/`, `identity/`, `config/`)
- **Unknown** — unclear; include file size, last modified, and Rigby's best guess

**Finding type:** FLAG (all root hygiene findings require confirmation — never auto-execute)

---

#### Rule 9: Model Compliance

Every workflow, step, and skill file must declare a `model:` field in its frontmatter. Missing entries indicate the spawning agent will silently inherit the parent model, which wastes tokens or under-powers tasks.

**Check:**
Scan frontmatter for a `model:` field in:
- `workflows/*/workflow.md`
- `workflows/*/steps/step-*.md`
- `skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`

A file **fails** if its frontmatter block exists but has no `model:` field, or has no frontmatter at all.

**Auto-fix — missing `model:` field:**
Determine the correct model using this routing table (first match wins):

| Condition | Assign |
|---|---|
| Step is pure I/O: API calls, file reads, script execution, staging ops | `haiku` |
| Step involves reasoning: calendar cross-ref, heuristics, synthesis, analysis | `sonnet` |
| Workflow/skill owner is Knox | `haiku` |
| Workflow/skill owner is Quinn | `opus` |
| Workflow/skill owner is Chief, Chase, Harper, Rigby, Shep, Galen, Master, Sterling | `sonnet` |
| Skill is mechanical transform, fetch, or enumeration | `haiku` |
| Skill involves writing, analysis, or interpretation | `sonnet` |
| Cannot determine | `sonnet` (safe default) |

To determine workflow owner for a step file: read the parent `workflow.md`'s `agent:` field.

Add `model: <value>` to the frontmatter block. Do NOT change an existing `model:` value.

**Finding type:** AUTO-FIX
<!-- personal:end -->

<!-- system:start -->
---

### Step 3 — Apply All Auto-Fixes

Apply every AUTO-FIX finding collected in Step 2, in this order:
1. Rule 1 fixes (create missing commands)
2. Rule 3 fixes (update manifest)
3. Rule 7 fixes (add missing `name` frontmatter)
<!-- system:end -->

<!-- personal:start -->
4. Rule 9 fixes (add missing `model:` frontmatter)
<!-- personal:end -->

<!-- system:start -->
For each fix applied, record it in the findings log with:
- What was fixed
- The file path affected
- The exact change made

---

### Step 4 — Track Fixes as Pending Changes

If any auto-fixes were applied that affect system files (not just local instance files), append to `evolutions/.pending-changes.json`.

Create the file if it does not exist:
```json
{
  "pending": []
}
```

Append a work item:
```json
{
  "id": "integrity-{LOG_DATE}",
  "description": "Integrity scan fixes — {count} auto-corrections applied",
  "started": "{ISO timestamp}",
  "files": [
    {
      "path": "{affected file}",
      "action": "add|merge",
      "type": "system",
      "description": "{what was fixed}"
    }
  ]
}
```

**What counts as a system fix (evolution candidate):**
- Missing ies-* command file created (all users need it)
- Missing skill or workflow added to manifest (all users need it)

**What is local-only (do not track as evolution):**
- Missing `name` frontmatter fixed (local instance correction)
<!-- system:end -->

<!-- personal:start -->
- Missing `model:` frontmatter fixed (personal routing preference — not an evolution candidate)
<!-- personal:end -->

<!-- system:start -->
---

### Step 5 — Write Findings Log

Write `logs/integrity-{LOG_DATE}.md` with this structure:

```markdown
# IES Integrity Scan — {YYYY-MM-DD HH:MM}

## Summary

- Rules checked: {N}
- Auto-fixes applied: {count}
- Flags raised: {count}
- Evolution candidates: {count}

## Auto-Fixes Applied

{For each fix:}
### {Rule name}
- **File:** `{path}`
- **Fix:** {description of change}

## Flags Requiring Review

{For each flag:}
### {Rule name}
- **File:** `{path}`
- **Issue:** {description}
- **Recommended action:** {what should be done}

## Rules That Passed Clean

{List of rule names with no findings}

## Scan Metadata

- IES root: {detected path}
- Skills scanned: {count}
- Commands scanned: {count}
- Agents scanned: {count}
- Workflows scanned: {count}
```

If there are no findings in a section, write `None.` under that section header.

---

### Step 6 — Report to Executive

Output a concise summary:

```
Integrity scan complete — {YYYY-MM-DD HH:MM}

Auto-fixed: {count}
{  - brief description of each fix}

Flags requiring review: {count}
{  - brief description of each flag}

Evolution candidates: {count} fix(es) ready to package when convenient

Log written: logs/integrity-{LOG_DATE}.md
```

If everything is clean:
```
Integrity scan complete — {YYYY-MM-DD HH:MM}

All {N} rules passed. No issues found.

Log written: logs/integrity-{LOG_DATE}.md
```
<!-- system:end -->

<!-- personal:start -->
**Root hygiene flags** (Rule 8) are presented separately after the main report, grouped as Move / Delete / Unknown with a confirmation prompt:

```
Root hygiene — {N} file(s) need attention:

### Move ({N})
| File | Destination |
|---|---|
| example.md | meetings/ |

### Delete ({N})
| File | Reason |
|---|---|
| draft-temp.md | Ephemeral session output |

### Unknown ({N})
| File | Size | Modified | What it appears to be | Recommended action |
|---|---|---|---|---|

Confirm to proceed: "execute", "execute moves only", "execute deletes only", or per-file.
```

Do NOT move or delete root files until the executive confirms. Accepted forms: "execute", "execute moves only", "execute deletes only", specific filename, "skip [filename]", "move [filename] to [path]".
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Glob** — list files in `skills/`, `agents/`, `workflows/`, `.claude/commands/`
- **Grep** — search for hardcoded paths, usernames, frontmatter fields
- **Read** — read `agents/master.md`, `evolution.manifest.json`, skill frontmatter
- **Write** — create missing command files, write findings log, create pending-changes.json
- **Edit** — update `evolution.manifest.json` manifest arrays, fix frontmatter fields
<!-- system:end -->

<!-- personal:start -->
- **Bash** — `ls`, `mv`, `rm`, `mkdir` for root hygiene execution; `stat` for file metadata
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS

Accepts optional flags:
- `--dry-run` — scan and report findings but do not apply any auto-fixes
- `--fix-only` — apply auto-fixes silently, skip the flag report
- `--rule {N}` — run only the specified rule number (1–9)
<!-- system:end -->

<!-- personal:start -->
## Trigger Phrases

- "integrity", "integrity scan", "system integrity", "rigby integrity"
- "root audit", "audit root", "clean up root", "root directory hygiene"
- "model compliance", "check model fields"
<!-- personal:end -->

---
name: rigby-evolution-package
description: Extract locally developed changes, build an evolution manifest, and assemble a local package directory ready for upload
context: fork
agent: general-purpose
---

<!-- system:start -->
# Rigby — Evolution Package

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Take locally developed IES improvements and assemble them into a versioned evolution package on disk. The package is **not uploaded** — run `rigby-evolution-upload` separately after reviewing the assembled package.

## Input

`$ARGUMENTS` — accepts one of:
- `--name "April Update" --description "..."` — specify evolution name and description
- `--files agents/analyst.md,workflows/new-workflow/workflow.md` — specific files to include
- `--git-diff` — detect changed files automatically using git diff vs main branch
- `--pending` — use files tracked in `evolutions/.pending-changes.json` (built by `rigby-capability-build`)
- `--pending --work-id {id}` — include only a specific pending work item (repeat for multiple)

If no `--files`, `--git-diff`, or `--pending` flag: default to `--git-diff`.

**Version format:** Evolution versions are UUID v4 — generated automatically by Rigby, never user-supplied. Each evolution is a globally unique, atomic package with no ordering implied by version. Evolutions are ordered by `releasedAt` date on the server.

## Process

### 1. Collect Changed Files

**If `--pending`:**
Read `evolutions/.pending-changes.json`. Collect all work items (or only those matching `--work-id` filters).
Build the file list from the union of all `files` entries across the selected work items.
Use the `action` and `type` already recorded in the pending log — skip re-classification for these files.
Record which work item IDs are being packaged so they can be cleared from the pending log after assembly.

**If `--git-diff`:**
Run `git diff --name-only main` (or `HEAD~1` if no main branch) to get the list of changed files.
Filter to only IES system files: `agents/`, `workflows/`, `skills/`, `docs/`, `config/settings.json`.
Exclude personal directories: `identity/`, `context/`, `training/`, `data/`, `logs/`, `tasks/`.

**If `--files`:**
Use the explicitly listed file paths.

### 2. Classify Each File

For each file in the list, read its content and apply the classification rules:

**Contains `<!-- system:start -->` AND `<!-- personal:start -->`?**
→ Type: `mixed`, Action: `merge`

**Contains only `<!-- system:start -->` (no personal blocks)?**
→ Type: `system`, Action: `replace` (if file existed before) or `add` (if new)

**No system/personal tags at all?**
→ Type: `system`, Action: `replace` or `add`

**Contains only `<!-- personal:start -->` blocks?**
→ Type: `personal` — **SKIP — never include personal files in a system evolution**

**File is new (not in main branch)?**
→ Action: `add`

**File was deleted?**
→ Action: `delete` (only if type is `system`)

### 3. Extract System Content for Mixed Files

For files with action `merge`, extract only the system blocks for the package:
- Preserve all `<!-- system:start -->` ... `<!-- system:end -->` content
- Replace `<!-- personal:start -->` ... `<!-- personal:end -->` blocks with empty markers
- The empty personal markers act as placeholders — they survive the merge on the receiving end

### 4. Build Evolution Manifest

Prompt Rigby to confirm or enter:
- `name` — human-readable evolution name (required)
- `description` — what this evolution does
- `minimum_base_version` — minimum IES version required (default: current installed version)
- `type` — default `system`

**Generate a UUID v4** for the `version` field — do not ask the executive for a version number. Use a standard UUID v4 generator (e.g., `python3 -c "import uuid; print(uuid.uuid4())"` or equivalent). The version uniquely identifies this exact package.

Build `evolution.manifest.json`:

```json
{
  "id": "ies-{uuid-v4}",
  "version": "{uuid-v4}",
  "name": "{name}",
  "description": "{description}",
  "released": "{today-ISO}",
  "type": "system",
  "compatibility": {
    "minimum_base_version": "{minimum_base_version}"
  },
  "files": [
    {
      "path": "{relative-file-path}",
      "type": "{system|mixed}",
      "action": "{add|replace|merge|delete}",
      "description": "{what changed}"
    }
  ],
  "changelog": ["{bullet-point-description-of-each-change}"],
  "training_prompts": []
}
```

Note: `id` and `version` both use UUID v4 but are separate fields — `version` is used for deduplication and manifest validation; `id` is a human-readable reference prefix. Use the same UUID for both (prefixed with `ies-` in `id`).

### 5. Preview

Display the manifest summary:
- Show file count, action breakdown (X added, Y merged, Z replaced)
- Show changelog bullets

### 6. Assemble Package Directory

Create a local package directory at `evolutions/ies-{name-slug}/` (use the evolution name, slugified — not the UUID).

**First:** Write `evolution.manifest.json` with the manifest built in Step 4.

**Then — required — write each source file into the package directory.** For every file in the manifest with action `add`, `replace`, or `merge`:
1. Read the file's full content from its original path in the IES root (e.g., `skills/analyst.md`)
   - For `merge` files: use the system-extracted version from Step 3 (empty personal markers)
   - For `add`/`replace` files: use the unmodified source content
2. Write that content to `evolutions/ies-{name-slug}/{original-path}` (e.g., `evolutions/ies-{name-slug}/skills/analyst.md`)
3. Create subdirectories as needed

For `delete` files: do NOT write a file — the manifest action entry is sufficient.

**This step is not complete until every non-delete file is present in the package directory.**

**If `--pending` mode:** remove the packaged work item IDs from `evolutions/.pending-changes.json`.

### 7. Output Summary

```
✓ "{name}" packaged
  Package: evolutions/ies-{name-slug}/
  Files included: {count}
    {count} added
    {count} replaced
    {count} merged
  Review the package directory, then run:
    /ies-rigby-evolution-upload --package evolutions/ies-{name-slug}/
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Git**: Bash `git diff --name-only` to detect changed files
- **Files**: Read, Write, Glob, Grep for file classification and package assembly
- **Config**: Read `config/settings.json` for version details
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

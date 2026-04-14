---
name: rigby-root-audit
description: Audit the IES root directory for files that don't belong — classifies each as Move, Delete, or Unknown, then executes confirmed actions.
evolution: system
---

<!-- system:start -->
## Trigger Phrases

- "root audit", "audit root", "clean up root", "what's in root", "root directory hygiene"
- "files don't belong", "clean up IES root", "root folder audit"

## Purpose

Surface files sitting in the IES root directory that don't belong there. Classify each file as Move, Delete, or Unknown. Present findings to the executive for confirmation. Execute confirmed actions.

This skill never auto-deletes. Every action requires explicit confirmation.

## Process

### Step 1: List Root Files

List all files directly in the IES root directory (not subdirectories). Use:

```bash
ls -la {IES_ROOT}
```

Or use Glob with `*` (non-recursive) to enumerate files only.

**Ignore these known system files — do not classify or report them:**

| File / Pattern | Reason |
|----------------|--------|
| `CLAUDE.md` | System entrypoint |
| `SYSTEM.md` | Operating manual |
| `README.md` | Documentation |
| `SETUP.md` | Onboarding documentation |
| `evolution.manifest.json` | Evolution system component registry — permanent system file, not an artifact |
| `.gitignore` | Git config |
| `.git/` | Git repository |
| Any file or folder starting with `.` | Dotfiles/dotfolders — ignore all |

### Step 2: Classify Each Remaining File

For each file not in the ignore list, determine its classification:

**Delete** — Clearly temporary or working files with no permanent home:
- Research reports generated during a session (e.g., `research-report-*.md`)
- Temp outputs, scratch files, one-off generated documents
- Files with names suggesting they are ephemeral (e.g., `working-*.txt`, `temp-*.json`, `draft-*.md`)
- **PDF companion files**: Any `.pdf` file that has a corresponding `.md` file with the same base name (e.g., `2026-03-23-client-prep.pdf` when `2026-03-23-client-prep.md` also exists). This applies to meeting notes, call prep sheets, sales prep docs, and one-pagers — the PDF is regenerable from the `.md`. Move the `.md`; delete the `.pdf`.
- Any file explicitly confirmed as a deletable pattern by the executive in a prior session

**Move** — Files that belong in a known subfolder:

| If the file looks like... | Recommended destination |
|--------------------------|------------------------|
| A meeting note or prep doc | `meetings/` |
| An account or client file | `accounts/` |
| A report or analysis | `reports/` |
| An evolution package or history file | `evolutions/` |
| A person profile | `people/` |
| A project file | `projects/` |
| Identity/persona content | `identity/` |
| A config or settings file | `config/` |

**Unknown** — Files where the correct action is unclear. Collect:
- File name
- File size (bytes or human-readable)
- Last modified date
- Brief description of what the file appears to be (infer from name, extension, size)
- Recommended action (Rigby's best guess: Move to X, Delete, Keep)

### Step 3: Present Findings Table

Group by action type. Show only groups that have at least one file.

```
## Root Audit — {date}

### Move ({N} files)

| File | Recommended Destination |
|------|------------------------|
| example-meeting.md | meetings/ |

### Delete ({N} files)

| File | Reason |
|------|--------|
| research-report-draft.md | Generated research output — no permanent home |

### Unknown ({N} files)

| File | Size | Last Modified | What It Appears To Be | Recommended Action |
|------|------|--------------|----------------------|-------------------|
| manifest_update.json | 2.1 KB | 2026-03-15 | JSON manifest file — possibly an evolution artifact | Move to evolutions/ |

---
Confirm to proceed: reply with "execute" to apply all, or specify per-file.
```

If no files are found outside the ignore list, report: "Root is clean — no misplaced files found."

### Step 4: Wait for Confirmation

Do NOT move or delete anything until the executive confirms.

Accepted confirmation forms:
- "execute" — apply all proposed actions
- "execute moves only" — skip deletes
- "execute deletes only" — skip moves
- Specific file name(s) — apply only those
- "skip [filename]" — exclude a file from execution
- "move [filename] to [path]" — override destination

If the executive provides no confirmation, end the skill. Do not execute.

### Step 5: Execute Confirmed Actions

**For each confirmed Move:**
1. Verify the destination folder exists. If not, create it.
2. Move the file: `mv {IES_ROOT}/{filename} {IES_ROOT}/{destination}/`
3. Confirm move succeeded.

**For each confirmed Delete:**
1. Confirm the file is not a dotfile or system file (double-check).
2. Delete the file: `rm {IES_ROOT}/{filename}`
3. Confirm deletion succeeded.

### Step 6: Report Results

After execution:

```
## Root Audit — Complete

Moved: {N} files
Deleted: {N} files
Skipped: {N} files

[List each action taken with source → destination or "deleted"]

Root status: Clean / {N} files still require review
```

## Error Handling

| Failure | Action |
|---------|--------|
| Destination folder doesn't exist | Create it, then move |
| File not found at time of execution | Report as "already removed or moved — skipping" |
| Move fails due to permissions | Surface error, skip file, continue with remaining |
| Executive confirms delete on a dotfile | Refuse and warn: "That's a dotfile — skipping for safety." |
| IES root path not determinable | Ask: "What is the IES root path?" |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **File system**: Bash (`ls`, `mv`, `rm`, `mkdir`) for listing, moving, deleting files
- **Glob**: Non-recursive glob to enumerate root-level files
- **Read**: Inspect file contents when classification is ambiguous
- **Bash**: `stat` or `ls -la` for file size and modification date
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

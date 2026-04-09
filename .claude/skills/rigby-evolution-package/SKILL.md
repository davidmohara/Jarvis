---
name: rigby-evolution-package
description: Extract locally developed changes, build an evolution manifest, package the files, and upload to the web app
context: fork
agent: general-purpose
---

<!-- system:start -->
# Rigby — Evolution Package

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Take locally developed IES improvements and publish them to the web app so other IES instances can receive them. This is the authoring/upload half of the evolution lifecycle.

## Input

`$ARGUMENTS` — accepts one of:
- `--name "April Update" --description "..."` — specify evolution name and description
- `--files agents/analyst.md,workflows/new-workflow/workflow.md` — specific files to include
- `--git-diff` — detect changed files automatically using git diff vs main branch
- `--pending` — use files tracked in `evolutions/.pending-changes.json` (built by `rigby-capability-build`)
- `--pending --work-id {id}` — include only a specific pending work item (repeat for multiple)
- `--yes` — skip the Step 5 confirmation prompt and proceed automatically (non-interactive mode)

If no `--files`, `--git-diff`, or `--pending` flag: default to `--git-diff`.

**Version format:** Evolution versions are UUID v4 — generated automatically by Rigby, never user-supplied. Each evolution is a globally unique, atomic package with no ordering implied by version. Evolutions are ordered by `releasedAt` date on the server.

## Process

### 1. Collect Changed Files

**If `--pending`:**
Read `evolutions/.pending-changes.json`. Collect all work items (or only those matching `--work-id` filters).
Build the file list from the union of all `files` entries across the selected work items.
Use the `action` and `type` already recorded in the pending log — skip re-classification for these files.
Record which work item IDs are being packaged so they can be cleared from the pending log after upload.

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

### 5. Preview and Confirm

Display the manifest summary:
- Show file count, action breakdown (X added, Y merged, Z replaced)
- Show changelog bullets

**If `--yes` flag was provided in $ARGUMENTS:** Proceed to Step 6 immediately after displaying the summary.

**If `--yes` flag is NOT present: STOP HERE. Do not proceed to Step 6 or Step 7. Return the manifest summary to the executive and wait for explicit instruction to continue. This skill runs in a non-interactive execution context — there is no mechanism to ask a question and wait for a response. Proceeding without `--yes` will result in an unsanctioned upload. The only safe behavior is to stop.**

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

**This step is not complete until every non-delete file is present in the package directory. Do not proceed to Step 7 until all files are written.**

### 7. Upload to Web App

Read `config/settings.json` for `ies_app_url`. This file is always at `config/settings.json` in the IES root — do not search for it or assume it doesn't exist. If it is missing, stop and tell the executive: "config/settings.json is missing — this file must contain `ies_app_url`. Create it with the production URL before proceeding."

**Authenticate:** Read and follow `systems/auth/preamble.md` to obtain a valid access token. Use the resolved `ACCESS_TOKEN` for all API calls in this skill.

Upload via the REST publish endpoint. Construct the payload:

```json
{
  "version": "{uuid-v4}",
  "name": "{name}",
  "description": "{description}",
  "manifest": { ...manifest... },
  "changelog": [...],
  "files": {
    "{path-from-manifest}": "{full UTF-8 text content of that file}"
  },
  "audience": "internal"
}
```

**Populate `files` as follows:** For each file written to the package directory in Step 6 (all non-delete manifest entries), read the file content from `evolutions/ies-{name-slug}/{path}` and include it as a string value keyed by its relative path. Do NOT base64-encode — send plain UTF-8 text. Every file in the package directory must appear in this object; omitting files from the payload will cause the evolution to be missing content on the receiving end.

Call: `POST {ies_app_url}/api/evolutions`
Authorization: Bearer `{ACCESS_TOKEN}`
Content-Type: application/json

**On success:** HTTP 201 with `{ id, version, status: "submitted" }`.

**On success:**
- Log: `[evolution-package] Published "{name}" (ID: {uuid-v4}) — {file_count} files uploaded`
- **Status is now `submitted`** — the evolution is NOT yet visible to IES instances polling for updates. An administrator must approve it via `evolutions.approve` before it appears in the poll endpoint.
- Update `evolutions/history.md` to record the publication with name, UUID, and submitted status
- **If `--pending` mode:** remove the packaged work item IDs from `evolutions/.pending-changes.json`
- **Delete the local package directory** (`evolutions/ies-{name-slug}/`) — it is a staging artifact only. The permanent record is `evolutions/packages/{id}.json` and `evolutions/history.md`. If the directory delete fails, log a warning but do not block the success path.

**On failure:**
- Log the error and surface it to the executive
- The local package directory in `evolutions/` remains for retry

### 8. Output Summary

```
✓ "{name}" packaged and submitted
  Evolution ID: {uuid-v4}
  Files included: {count}
    {count} added
    {count} replaced
    {count} merged
  Status: submitted (awaiting admin approval)
  Once approved, available at: {ies_app_url}/api/evolutions/{db-id}/package
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Git**: Bash `git diff --name-only` to detect changed files
- **Files**: Read, Write, Glob, Grep for file classification and package assembly
- **HTTP**: Bash `curl` to upload to web app
- **Config**: Read `config/settings.json` for connection details
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

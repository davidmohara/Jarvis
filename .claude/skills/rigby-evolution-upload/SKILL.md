---
name: rigby-evolution-upload
description: Upload an assembled evolution package to the web app for admin review
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Evolution Upload

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Upload a locally assembled evolution package to the web app, where it enters `submitted` status and awaits admin approval. Run `rigby-evolution-package` first to assemble the package.

## Input

`$ARGUMENTS` — accepts:
- `--package evolutions/ies-{name-slug}/` — path to the package directory to upload (required)

If `--package` is omitted, scan `evolutions/` for subdirectories containing `evolution.manifest.json`, pick the most recently modified one, and confirm with the executive before proceeding.

## Process

### 1. Locate Package

If `--package` was provided, verify the directory exists and contains `evolution.manifest.json`. Abort if not found.

If no `--package` provided: scan `evolutions/` for package directories (subdirectories with `evolution.manifest.json`). Select the most recently modified. Show the executive:

```
Found package: evolutions/ies-{name-slug}/
  Name: {name}
  Version: {version}
  Files: {count}

Proceed with upload? (confirm or specify --package explicitly)
```

**STOP and wait for confirmation before continuing.** This skill runs in a non-interactive execution context — if not confirmed, abort.

### 2. Read Package

Read `evolution.manifest.json` from the package directory. Extract:
- `version`, `name`, `description`, `changelog`, `training_prompts`
- File list (all entries with action `add`, `replace`, or `merge`)

For each non-delete file in the manifest, read its content from the package directory.

### 3. Upload to Web App

Read `config/settings.json` for `ies_app_url`. This file is always at `config/settings.json` in the IES root — do not search for it or assume it doesn't exist. If it is missing, stop and tell the executive: "config/settings.json is missing — this file must contain `ies_app_url`. Create it with the production URL before proceeding."

**Authenticate:** Read and follow `systems/auth/preamble.md` to obtain a valid access token. Use the resolved `ACCESS_TOKEN` for all API calls in this skill.

Construct the payload:

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

**Populate `files` as follows:** For each non-delete manifest entry, include the file content read from the package directory as a plain UTF-8 string keyed by its relative path. Do NOT base64-encode. Every file in the package directory must appear in this object.

Call: `POST {ies_app_url}/api/evolutions`
Authorization: Bearer `{ACCESS_TOKEN}`
Content-Type: application/json

**On success:** HTTP 201 with `{ id, version, status: "submitted" }`.

**On success:**
- Log: `[evolution-upload] Published "{name}" (ID: {uuid-v4}) — {file_count} files uploaded`
- **Status is now `submitted`** — the evolution is NOT yet visible to IES instances polling for updates. An administrator must approve it before it appears in the poll endpoint.
- Append to `evolutions/history.md` to record the publication with name, UUID, and submitted status
- **Delete the local package directory** (`evolutions/ies-{name-slug}/`) — it is a staging artifact only. If the directory delete fails, log a warning but do not block the success path.

**On failure:**
- Log the error and surface it to the executive
- The local package directory remains for retry

### 4. Output Summary

```
✓ "{name}" submitted
  Evolution ID: {uuid-v4}
  Files uploaded: {count}
    {count} added
    {count} replaced
    {count} merged
  Status: submitted (awaiting admin approval)
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Files**: Read, Glob for reading the assembled package
- **HTTP**: Bash `curl` to upload to web app
- **Config**: Read `config/settings.json` and `systems/auth/preamble.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

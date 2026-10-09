---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

# Step 01: Validate Manifest

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline


<!-- system:start -->
## Purpose

Parse the evolution manifest, validate its structure, and verify all referenced files exist in the evolution package. Catch manifest errors before any system changes occur.

## Inputs

- `evolution_path` — Path to evolution package directory
- `evolution_manifest` — Path to evolution.manifest.json

## Process

### 1. Read Manifest

Load and parse `evolution_manifest` JSON file.

**Required fields:**
- `id` (string) — Unique evolution identifier
- `version` (string) — Evolution version number
- `name` (string) — Human-readable evolution name
- `description` (string) — What this evolution does
- `released` (date) — Release date
- `type` (enum: "system" | "personal") — Evolution type
- `files` (array) — List of files to process
- `changelog` (array of strings) — User-facing changes

**Optional fields:**
- `compatibility.minimum_base_version` (string) — Minimum IES version required
- `training_prompts` (array) — Training system integration

If any required field is missing, **HALT** and surface error:
```
Manifest validation failed: Missing required field '{field_name}'
File: {evolution_manifest}
```

### 2. Validate File Entries

For each item in `files` array, verify:

**Required fields per file entry:**
- `path` (string) — Relative path to file in evolution package
- `type` (enum: "system" | "personal" | "mixed")
- `action` (enum: "add" | "replace" | "merge" | "delete")
- `description` (string) — What this file change does

**Validation rules:**
- `path` must not be empty
- `path` must not contain `..` (no directory traversal)
- `type` must be one of: system, personal, mixed
- `action` must be one of: add, replace, merge, delete
- `action=delete` requires `type=system` (cannot delete personal/mixed files)
- `action=replace` requires `type=system` (cannot replace personal/mixed files)

If validation fails, **HALT** and surface error:
```
Manifest validation failed: Invalid file entry
File: {path}
Issue: {validation_issue}
```

### 3. Verify File Existence

For each file entry with action != "delete":
- Check that file exists at `{evolution_path}/{file.path}`
- If file does not exist, **HALT** and surface error:

```
Evolution package incomplete: Referenced file not found
Expected: {evolution_path}/{file.path}
```

### 4. Validate Version Format

If `compatibility.minimum_base_version` is present:
- Verify format matches: YYYY.MM or semantic version (e.g., 2026.03 or 1.0.0)
- Store for use in Step 02

### 5. Output Validation Summary

If all checks pass, output:

```
✓ Manifest valid
  Evolution: {name}
  Version: {version}
  Files to process: {count}
  Type: {type}
```

Store validated manifest data for next steps.

## Outputs

- `validated_manifest` — Parsed and validated manifest object
- `evolution_id` — Evolution identifier
- `evolution_version` — Evolution version
- `file_list` — Array of file entries to process

## Next Step

If validation succeeds: proceed to `step-02-compatibility-check.md`

If validation fails: HALT workflow and present errors to user
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

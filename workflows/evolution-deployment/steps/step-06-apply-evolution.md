---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

# Step 05: Apply Evolution

<!-- system:start -->
## Purpose

Execute the evolution deployment by processing each file according to its action type (add/replace/merge/delete). Preserve personal blocks during merge operations. Apply changes atomically where possible.

## Inputs

- `updated_file_list` — From Step 04 (post-conflict-resolution)
- `personal_block_registry` — From Step 04
- `evolution_path` — Evolution package directory
- `snapshot_id` — From Step 03

## Process

### 1. Initialize Application Tracker

Create structure to track application progress:

```json
{
  "files_processed": 0,
  "files_total": 0,
  "actions": {
    "add": 0,
    "replace": 0,
    "merge": 0,
    "delete": 0
  },
  "errors": []
}
```

### 2. Process Each File by Action Type

For each file in `updated_file_list`:

Determine action type and route to appropriate handler:

- `action` = "add" → **Handler: Add File**
- `action` = "replace" → **Handler: Replace File**
- `action` = "merge" → **Handler: Merge File**
- `action` = "delete" → **Handler: Delete File**

---

### Handler: Add File

**Purpose:** Write new file to system

**Steps:**

1. Get source file: `{evolution_path}/{file.path}`
2. Get target path: `{project-root}/{file.path}`
3. Check if file already exists at target:
   - If exists: **CONFLICT** — file marked as "add" but already exists
     - Surface error: "File {file.path} already exists. Manifest says 'add'. Re-evaluate as 'merge'?"
     - Wait for user decision
   - If not exists: Proceed
4. Ensure target directory exists (create if needed)
5. Copy source file to target path
6. Verify file written successfully
7. Log: `Added {file.path}`

---

### Handler: Replace File

**Purpose:** Overwrite existing file completely

**Pre-conditions (verified in Step 04):**
- File type must be "system"
- File must NOT contain personal blocks
- If these conditions aren't met, this file shouldn't reach this handler

**Steps:**

1. Get source file: `{evolution_path}/{file.path}`
2. Get target path: `{project-root}/{file.path}`
3. Verify no personal blocks in registry for this file (double-check safety)
4. If personal blocks found: **HALT** — "Critical error: personal blocks detected in replace operation"
5. Overwrite target file with source file content
6. Verify file written successfully
7. Log: `Replaced {file.path}`

---

### Handler: Merge File

**Purpose:** Update system content while preserving personal blocks

**Steps:**

1. Get source file (new system version): `{evolution_path}/{file.path}`
2. Get target path: `{project-root}/{file.path}`
3. Read source file content
4. Look up personal blocks for this file from `personal_block_registry`
5. If no personal blocks found:
   - Treat as simple replace: write source content to target
   - Log: `Merged {file.path} (no personal blocks to preserve)`
6. If personal blocks found:
   - Execute **Personal Block Merge Protocol** (see below)

**Personal Block Merge Protocol:**

1. Parse source file to identify section structure (markdown headings)
2. For each personal block from registry:
   - Identify original section context (e.g., "## Controller Directives")
   - Check if that section still exists in new source file
   - **If section exists:**
     - Find section in new source content
     - Insert personal block at end of that section (before next heading)
     - Preserve original `<!-- personal:start -->` / `<!-- personal:end -->` markers
   - **If section no longer exists:**
     - Append personal block to end of file
     - Add comment noting original location:
       ```
       <!-- The following personal block was originally in section "{original_section}" -->
       <!-- personal:start -->
       {block content}
       <!-- personal:end -->
       ```
3. Write merged content to target file
4. **Critical verification:**
   - Count personal blocks in output file
   - Compare to count in registry for this file
   - If counts don't match: **HALT** — "Merge verification failed: personal block count mismatch"
5. Log: `Merged {file.path} (preserved {count} personal blocks)`

**Merge Safety Rules:**

- Never modify content inside `<!-- personal:start/end -->` markers
- Always preserve marker comments exactly as-is
- If uncertain about section placement, append to end with location note
- Verify block count before finalizing

---

### Handler: Delete File

**Purpose:** Remove file from system

**Pre-conditions (verified in Step 04):**
- File type must be "system"
- File must NOT contain personal blocks

**Steps:**

1. Get target path: `{project-root}/{file.path}`
2. Verify no personal blocks in registry for this file (double-check safety)
3. If personal blocks found: **HALT** — "Critical error: cannot delete file with personal blocks"
4. If file doesn't exist: Log warning, skip (already gone)
5. Delete file
6. Verify file removed successfully
7. Log: `Deleted {file.path}`

---

### 3. Track Progress

After each file operation:
- Increment `files_processed`
- Increment action type counter
- If error occurs: add to `errors` array, continue with next file (don't halt entire deployment)

Output progress:
```
[{files_processed}/{files_total}] {action} {file.path}
```

### 4. Handle Errors

If any file operation fails:
- Log error with details
- Continue processing remaining files
- Flag deployment as "partial success" (some files failed)

**Do NOT halt on single file failure** — attempt to process all files, then surface errors at end.

### 5. Output Application Summary

After processing all files:

**If no errors:**

```
✓ Evolution applied successfully
  Files added: {add_count}
  Files replaced: {replace_count}
  Files merged: {merge_count}
  Files deleted: {delete_count}
  Personal blocks preserved: {total_blocks_preserved}
```

**If errors occurred:**

```
⚠️  Evolution applied with errors
  Files processed: {success_count}/{total_count}
  Errors: {error_count}

  Failed operations:
  {list errors}

  Rollback available: yes (snapshot {snapshot_id})
```

Present user with option to rollback if errors occurred.

## Outputs

- `application_result` — Success/partial/failure status
- `files_processed` — Count of successful operations
- `errors` — Array of any errors encountered
- `personal_blocks_preserved` — Total count of personal blocks successfully preserved

## Next Step

If application succeeds or partially succeeds: proceed to `step-06-verify-and-log.md`

If critical failure: offer rollback, HALT workflow
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

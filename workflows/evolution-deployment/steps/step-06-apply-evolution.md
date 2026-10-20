---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

# Step 05: Apply Evolution

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline


<!-- system:start -->
## Purpose

Execute the evolution deployment by processing each file according to its action type (add/replace/merge/delete). Preserve personal blocks during merge operations. Apply changes atomically where possible.

## Inputs

- `updated_file_list` — From Step 05 (post-conflict-resolution)
- `personal_block_registry` — From Step 05
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

Run the per-action-type handler from `references/apply-handlers.md` (read it before processing files): Add, Replace, Merge, Delete. Halt conditions in that file are non-negotiable.

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

If application succeeds or partially succeeds: proceed to `step-07-verify-and-log.md`

If critical failure: offer rollback, HALT workflow
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

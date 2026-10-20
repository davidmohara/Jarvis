<!-- system:start -->
# Apply Handlers (evolution-deployment)

Per-action-type handlers invoked by step-06 task 2. Apply exactly as written; halt conditions are non-negotiable.

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

**Pre-conditions (verified in Step 05):**
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

**Pre-conditions (verified in Step 05):**
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
<!-- system:end -->

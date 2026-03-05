# Step 04: Scan Personal Blocks

<!-- system:start -->
## Purpose

Parse all target files to identify and extract personal blocks. Record their locations and content so they can be preserved during merge operations. Detect conflicts where replace/delete actions target files with personal content.

## Inputs

- `file_list` — From Step 01
- `snapshot_path` — From Step 03

## Process

### 1. Initialize Personal Block Registry

Create data structure to track all personal blocks:

```json
{
  "files_scanned": 0,
  "personal_blocks_found": 0,
  "conflicts_detected": 0,
  "registry": []
}
```

### 2. Scan Each Target File

For each file in `file_list`:

**Skip if:**
- `action` = "add" (new file, no existing content to scan)
- File doesn't exist in current system

**Process if:**
- `action` = "replace", "merge", or "delete"
- File exists in current system

### 3. Parse Personal Block Markers

For each file to scan:

1. Read file content from `{project-root}/{file.path}`
2. Search for personal block delimiters:
   - Start marker: `<!-- personal:start -->`
   - End marker: `<!-- personal:end -->`
3. Extract all blocks between start/end markers
4. Record block position context:
   - Line number range
   - Surrounding section heading (if within a markdown section)
   - Parent element context

**Personal block extraction logic:**

```
blocks = []
in_personal_block = false
current_block = null
current_section_heading = null

for each line in file:
  if line contains markdown heading (# or ##):
    current_section_heading = line

  if line contains "<!-- personal:start -->":
    in_personal_block = true
    current_block = {
      start_line: line_number,
      section: current_section_heading,
      content: []
    }

  if in_personal_block and line != start/end marker:
    current_block.content.append(line)

  if line contains "<!-- personal:end -->":
    in_personal_block = false
    current_block.end_line = line_number
    blocks.append(current_block)
    current_block = null

return blocks
```

### 4. Register Personal Blocks

For each extracted block, add to registry:

```json
{
  "file": "agents/chase.md",
  "block_id": 1,
  "start_line": 50,
  "end_line": 53,
  "section": "## Controller Directives",
  "content": [
    "- Never suggest tasks before 8am",
    "- Scott is my most reliable direct report; don't nudge unless 3+ days overdue"
  ]
}
```

### 5. Detect Conflicts

Check for dangerous action/content combinations:

**Conflict detected if:**
- File has `action` = "replace" AND contains personal blocks
- File has `action` = "delete" AND contains personal blocks

For each conflict:

```
✗ CONFLICT DETECTED
  File: {file.path}
  Action: {action}
  Issue: Cannot {action} file containing personal blocks
  Personal blocks found: {count}

  Personal content at risk:
  {show block content preview}

  Resolution required:
  - Change action to "merge" (preserves personal blocks) OR
  - Skip this file OR
  - Abort deployment
```

Store conflicts for user review.

### 6. Output Scan Summary

If no conflicts:

```
✓ Personal block scan complete
  Files scanned: {count}
  Personal blocks found: {count}
  Conflicts: 0
  Safe to proceed with merge operations
```

If conflicts detected:

```
⚠️  Personal block conflicts detected
  Files scanned: {count}
  Personal blocks found: {count}
  Conflicts: {count}

  Review required before proceeding.
```

Present each conflict to user and wait for resolution decisions.

## Conflict Resolution Options

For each conflict, user chooses:

1. **Auto-fix: Change to merge** — Update file entry's action from "replace" to "merge"
2. **Skip file** — Remove file from file_list, don't process it
3. **Abort deployment** — Exit workflow, no changes applied

Record user's decision for each conflict.

If user chooses "Abort", **HALT** workflow immediately.

## Outputs

- `personal_block_registry` — Complete registry of all personal blocks with locations
- `conflicts` — Array of conflicts detected
- `conflict_resolutions` — User decisions for each conflict
- `updated_file_list` — file_list with action changes or removals based on resolutions

## Next Step

If no conflicts OR all conflicts resolved: proceed to `step-05-apply-evolution.md`

If user aborted: HALT workflow
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

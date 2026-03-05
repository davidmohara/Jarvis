# Step 06: Verify & Log

<!-- system:start -->
## Purpose

Final verification that personal blocks were preserved, system integrity is intact, and deployment completed successfully. Write evolution to history log. Surface changelog to user. Queue training prompts if present.

## Inputs

- `application_result` — From Step 05
- `files_processed` — From Step 05
- `personal_blocks_preserved` — From Step 05
- `personal_block_registry` — From Step 04
- `validated_manifest` — From Step 01
- `snapshot_id` — From Step 03
- `evolution_id` — From Step 01
- `evolution_version` — From Step 01

## Process

### 1. Verify Personal Block Integrity

**Critical verification step — ensures no personal data was lost.**

For each file in `personal_block_registry`:

1. Read the deployed file: `{project-root}/{file.path}`
2. Parse file to extract personal blocks (same logic as Step 04)
3. Compare extracted blocks to original registry:
   - Count must match
   - Content must match (exact string comparison)
4. If mismatch detected:
   - **CRITICAL ERROR** — personal block lost or corrupted
   - Surface error:
     ```
     ✗ INTEGRITY VERIFICATION FAILED
       File: {file.path}
       Expected blocks: {registry_count}
       Found blocks: {actual_count}

       Personal data may have been lost.

       IMMEDIATE ACTIONS:
       1. DO NOT PROCEED
       2. Rollback to snapshot: {snapshot_id}
       3. Report this error
     ```
   - Offer automatic rollback
   - **HALT** deployment

If all personal blocks verified:

```
✓ Personal block integrity verified
  Files checked: {count}
  Personal blocks confirmed present: {count}
  No data loss detected
```

### 2. System Integrity Check

Run basic system integrity checks:

1. **Agent files:** Verify all agent files have required metadata fields
2. **Workflow files:** Verify all workflow files have valid frontmatter
3. **Permissions:** If permissions.md was updated, verify syntax is valid
4. **References:** Check for broken references (e.g., workflow steps that don't exist)

If issues found:
- Log warnings (non-blocking)
- Surface to user for review

### 3. Write to Evolution History

Append entry to `{project-root}/evolutions/history.md`:

**Format:**

```markdown
## {evolution_name} ({evolution_version}) — Applied {date}

**Evolution ID:** {evolution_id}
**Applied:** {ISO timestamp}
**Snapshot:** {snapshot_id}
**Applied by:** {user or system}

### Files Changed

{for each file in file_list:}
- `{file.path}` — {action}{if merged: " ({personal_blocks_count} personal blocks preserved)"}
{end for}

### Conflicts

{if conflicts encountered:}
{list each conflict and resolution}
{else:}
None.
{end if}

### Personal Blocks Preserved

{if personal blocks:}
{for each file with personal blocks:}
- `{file.path}`: {list sections where blocks preserved}
{end for}
{else:}
No personal blocks in target files.
{end if}

### Status

{if no errors:}
✓ Deployment successful
{else:}
⚠️  Deployment completed with warnings (see errors below)
{list errors}
{end if}

---

```

### 4. Update System Version

If evolution includes version bump:

Write or update `{project-root}/.ies-version`:

```
{evolution_version}
```

This tracks the current IES system version.

### 5. Surface Changelog to User

Present the evolution's changelog from manifest:

```
🎉 Evolution Applied: {evolution_name}

What's New:
{for each changelog entry:}
• {entry}
{end for}
```

If manifest includes `training_prompts`, mention them:

```
New capabilities unlocked! Try these:
{for each prompt:}
• {prompt.agent}: {prompt.prompt}
{end for}
```

### 6. Queue Training Prompts (if present)

If manifest includes `training_prompts`:

1. Check if project has training system integration
2. If yes: Pass training_prompts to training system for progressive unlock
3. If no: Log prompts to `{project-root}/evolutions/training-queue.json` for manual review

### 7. Output Final Summary

**If deployment fully successful:**

```
✅ Evolution deployment complete

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}
Rollback available: yes

History logged to: evolutions/history.md

{display changelog}
```

**If deployment had warnings/errors:**

```
⚠️  Evolution deployment completed with warnings

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {success_count}/{total_count}
Errors: {error_count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}

Issues encountered:
{list errors}

Recommendations:
- Review errors above
- Verify system functionality
- Rollback available if needed: rigby rollback {snapshot_id}

History logged to: evolutions/history.md
```

## Outputs

- `deployment_status` — Success/warning/failure
- `history_entry` — Written to evolutions/history.md
- `changelog_presented` — Boolean
- `training_prompts_queued` — Boolean

## Workflow Complete

This is the final step. Evolution deployment workflow terminates here.

**User can now:**
- Use new evolution features
- Review evolution history: `rigby history`
- Rollback if needed: `rigby rollback {snapshot_id}`
- Test new capabilities mentioned in training prompts
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

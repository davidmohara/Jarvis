---
name: evolution-deployment
description: Deploy system evolution packages with non-destructive personal block preservation
agent: rigby
model: sonnet
---

<!-- system:start -->
# Evolution Deployment Workflow

**Goal:** Apply a system evolution to IES infrastructure while guaranteeing personal blocks are never overwritten. Deploy safely or don't deploy at all.

**Agent:** Rigby — System Operator

**Architecture:** Sequential 6-step workflow with mandatory halt points for conflicts. User confirmation required before any destructive operations. Every deployment gets a snapshot. Every change gets logged.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Input Required

- `evolution_path` — Path to evolution package directory containing evolution.manifest.json

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Evolution manifest | Package metadata, file list, actions, compatibility | Read evolution_path/evolution.manifest.json |
| Current system files | Agent definitions, workflows, permissions, config | File system reads |
| Evolution history | Previously applied evolutions | Read evolutions/history.md |
| System snapshots | Available rollback points | List evolutions/snapshots/ directory |

### Paths

- `evolution_manifest` = `{evolution_path}/evolution.manifest.json`
- `evolution_history` = `{project-root}/evolutions/history.md`
- `snapshot_directory` = `{project-root}/evolutions/snapshots/`
- `agents_directory` = `{project-root}/docs/agents/`
- `workflows_directory` = `{project-root}/docs/workflows/`
- `permissions_file` = `{project-root}/docs/Permissions.md`

### Pre-Flight Requirements

Before starting workflow:
1. Verify evolution_path exists and contains evolution.manifest.json
2. Confirm current working directory is project root
3. Check write permissions to all target directories
4. Verify git status is clean (recommended but not required)
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

### Step Sequence

This workflow MUST be executed in order. Each step has defined outputs that feed the next step. Do not skip steps. Do not proceed if a step fails.

1. **Step 01: Validate Manifest** — Parse and validate evolution manifest structure, verify all referenced files exist in package
2. **Step 02: Compatibility Check** — Verify minimum_base_version requirement, check for breaking changes
3. **Step 03: Create Snapshot** — Backup current state of all files listed in manifest before any modifications
4. **Step 04: Scan Personal Blocks** — Parse all target files, extract personal block locations and content
5. **Step 05: Apply Evolution** — Execute file operations (add/replace/merge/delete) according to manifest
6. **Step 06: Verify & Log** — Confirm integrity, verify personal blocks preserved, write to history

### Execution Entry Point

Read fully and follow: `steps/step-01-validate-manifest.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## CONFLICT HANDLING

If any step detects a conflict (e.g., replace action targeting file with personal blocks):

1. **HALT immediately** — do not proceed with that file
2. **Surface the conflict** to user with:
   - File path
   - Action type (replace/delete)
   - Personal blocks that would be affected (show content)
   - Recommended resolution
3. **Offer options:**
   - Apply system change and preserve personal blocks (change action to merge)
   - Skip this file (continue with rest of evolution)
   - Abort entire deployment
   - Review file manually (exit workflow)
4. **Wait for user decision** — no automatic conflict resolution
5. **Log the conflict** in evolution history regardless of decision
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## ROLLBACK PROTOCOL

If deployment fails or user requests rollback after application:

1. Identify the snapshot created in Step 03
2. Verify snapshot integrity (all expected files present)
3. Restore each file from snapshot to original location
4. Verify restoration (checksums if available)
5. Log rollback to evolution history with reason
6. Confirm system is in pre-deployment state

User can trigger rollback via Rigby's `rollback` command with snapshot ID.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## SUCCESS CRITERIA

Deployment is considered successful when:

- All files in manifest processed according to their action type
- All personal blocks from pre-deployment scan present in post-deployment files
- Integrity verification passes
- Evolution logged to history.md
- No errors or warnings surfaced during application
- Snapshot created and available for rollback

If any criterion fails, deployment is **not successful** — rollback and surface issue to user.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

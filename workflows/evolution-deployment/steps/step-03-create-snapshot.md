# Step 03: Create Snapshot

<!-- system:start -->
## Purpose

Create a complete, versioned backup of all files that will be modified by this evolution. Ensures rollback capability if deployment fails or user needs to revert changes.

## Inputs

- `file_list` — From Step 01 (files to be modified)
- `evolution_id` — From Step 01
- `evolution_version` — From Step 01

## Process

### 1. Generate Snapshot ID

Create unique snapshot identifier:

```
snapshot_id = "{evolution_id}-{timestamp}"
```

Example: `ies-evolution-2026-03-20260225-143022`

Timestamp format: `YYYYMMDD-HHMMSS`

### 2. Create Snapshot Directory

```
snapshot_path = "{project-root}/evolutions/snapshots/{snapshot_id}/"
```

Create directory structure:
```
evolutions/
  snapshots/
    {snapshot_id}/
      agents/
      workflows/
      docs/
      snapshot.metadata.json
```

### 3. Copy Files to Snapshot

For each file in `file_list` where `action` != "add":

1. Determine current file path: `{project-root}/{file.path}`
2. If file exists:
   - Copy to: `{snapshot_path}/{file.path}`
   - Preserve directory structure
   - Preserve file permissions
3. If file doesn't exist:
   - Log: "File {file.path} not present in current system (will be added by evolution)"

**Important:** Only snapshot files that currently exist. New files (action=add) don't need snapshots.

### 4. Create Snapshot Metadata

Write `snapshot.metadata.json`:

```json
{
  "snapshot_id": "{snapshot_id}",
  "created": "{ISO timestamp}",
  "evolution": {
    "id": "{evolution_id}",
    "version": "{evolution_version}",
    "name": "{evolution_name}"
  },
  "system_version": "{current_version}",
  "files": [
    {
      "path": "agents/chase.md",
      "size_bytes": 4567,
      "checksum": "sha256_hash_here"
    }
  ],
  "notes": "Pre-deployment snapshot for evolution {evolution_id}"
}
```

Include checksums (SHA-256) for integrity verification during rollback.

### 5. Verify Snapshot Integrity

Confirm:
- All expected files copied successfully
- Directory structure matches source
- Total files count matches expectation
- Metadata file written and valid JSON

If verification fails:
```
✗ Snapshot creation failed
  Issue: {error_detail}
  Cannot proceed without valid snapshot
```

**HALT** deployment.

### 6. Output Snapshot Summary

If snapshot succeeds:

```
✓ Snapshot created
  ID: {snapshot_id}
  Location: evolutions/snapshots/{snapshot_id}/
  Files backed up: {count}
  Rollback available: yes
```

Store `snapshot_id` for use in Step 06 (logging) and potential rollback.

## Outputs

- `snapshot_id` — Unique identifier for this snapshot
- `snapshot_path` — Full path to snapshot directory
- `snapshot_metadata` — Metadata object with file list and checksums

## Rollback Usage

To restore from this snapshot (user invokes via Rigby's `rollback` command):

1. Read `{snapshot_path}/snapshot.metadata.json`
2. For each file in metadata:
   - Copy from `{snapshot_path}/{file.path}` to `{project-root}/{file.path}`
   - Verify checksum matches
3. Log rollback to evolution history

## Next Step

If snapshot creation succeeds: proceed to `step-04-scan-personal-blocks.md`

If snapshot fails: HALT workflow
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

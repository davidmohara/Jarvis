---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

# Step 02: Compatibility Check

<!-- system:start -->
## Purpose

Verify the evolution is compatible with the current IES installation. Check version requirements and detect potential breaking changes before proceeding with deployment.

## Inputs

- `validated_manifest` — From Step 01
- `evolution_version` — From Step 01
- `minimum_base_version` — From manifest compatibility section (if present)

## Process

### 1. Determine Current IES Version

Read current system version from one of:
- `{project-root}/evolutions/history.md` — last applied evolution version
- `{project-root}/.ies-version` — if version file exists
- `{project-root}/docs/VERSION` — if version file exists

If no version file found, assume **baseline 2026.01** (first stable release).

Store as `current_version`.

### 2. Check Minimum Version Requirement

If manifest includes `compatibility.minimum_base_version`:

Compare `current_version` against `minimum_base_version`:

**Version comparison logic:**
- Parse both versions (YYYY.MM format or semantic versioning)
- If `current_version` < `minimum_base_version`, **HALT** and surface error:

```
Compatibility check failed: IES version too old
Current version: {current_version}
Required version: {minimum_base_version}
Evolution: {evolution_name} ({evolution_version})

You need to upgrade your base IES installation before applying this evolution.
```

If check passes:
```
✓ Version compatible
  Current: {current_version}
  Required: {minimum_base_version}
```

### 3. Check Evolution History

Read `{project-root}/evolutions/history.md`.

Verify:
- This evolution ID hasn't been applied already
- No version conflicts (e.g., applying 2026.02 when 2026.03 already applied)

If evolution already applied:
```
⚠️  Evolution already applied
  Evolution: {evolution_id}
  Applied on: {previous_application_date}

Options:
  1. Skip (no changes needed)
  2. Re-apply (useful for fixing corrupted files)
  3. Abort
```

Wait for user decision.

### 4. Scan for Breaking Changes

Check manifest for indicators of breaking changes:
- Any `delete` actions on core system files
- Any `replace` actions on agent definitions
- Any workflow renames or removals

If breaking changes detected:
```
⚠️  This evolution includes breaking changes:
{list of breaking changes}

Recommended: Create manual backup before proceeding.
Continue? (yes/no)
```

Wait for user confirmation.

### 5. Output Compatibility Summary

If all checks pass:

```
✓ Compatibility verified
  No conflicts detected
  Safe to proceed
```

## Outputs

- `compatibility_status` — Pass/fail result
- `breaking_changes` — List of breaking changes (if any)
- `current_version` — System version
- `user_confirmed` — Boolean if user confirmed breaking changes

## Next Step

If compatibility checks pass: proceed to `step-03-create-snapshot.md`

If compatibility fails: HALT workflow and present errors to user
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

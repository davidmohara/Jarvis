# IES Evolutions

This directory contains evolution packages and deployment infrastructure for IES.

## What Are Evolutions?

Evolutions are versioned upgrade packages that extend or improve IES without breaking existing functionality. Each evolution is a curated set of definition files — agents, workflows, permissions, and configuration.

**Core principle:** Personal evolutions are never overwritten by system evolutions. Your preferences, directives, and customizations survive every upgrade.

## Directory Structure

```
evolutions/
├── README.md                    # This file
├── history.md                   # Log of all applied evolutions
├── snapshots/                   # Versioned backups for rollback
│   └── {snapshot-id}/           # Each snapshot is a complete backup
├── example-evolution-2026-03/   # Example evolution package
│   ├── evolution.manifest.json  # Package metadata
│   └── agents/                  # New or updated agent files
│       └── rigby.md
└── {future-evolutions}/         # Additional evolution packages
```

## Using Evolutions

### Deploy an Evolution

Ask Rigby to deploy an evolution:

```
rigby deploy evolutions/{evolution-id}
```

Example:
```
rigby deploy evolutions/example-evolution-2026-03
```

Rigby will:
1. Validate the evolution manifest
2. Check compatibility with your system
3. Create a snapshot for rollback
4. Scan for personal blocks to preserve
5. Apply the evolution
6. Verify integrity and log to history

### View Evolution History

```
rigby history
```

Shows all previously applied evolutions.

### Rollback an Evolution

If something goes wrong:

```
rigby rollback {snapshot-id}
```

Snapshot IDs are shown during deployment and logged in history.md.

### Validate Before Deploying

To check an evolution without applying it:

```
rigby validate evolutions/{evolution-id}
```

Pre-flight check: verifies manifest, compatibility, and detects conflicts.

## Evolution Types

### System Evolutions

Changes to core IES functionality:
- New agents or workflows
- Updates to existing agent logic
- New permissions or tools
- Framework improvements

Owned by IES platform. Safe to overwrite on upgrade.

### Personal Evolutions

User-specific customizations:
- Communication style and tone directives
- Tool preferences and integrations
- Agent personality overrides
- Workflow behavioral preferences

Owned by you. Never overwritten by system evolutions.

## Personal Block Protection

Files use HTML comments to mark personal sections:

```markdown
<!-- system:start -->
System-owned content here
<!-- system:end -->

<!-- personal:start -->
Your customizations here
<!-- personal:end -->
```

Content inside `<!-- personal:start/end -->` blocks is **immutable** during evolution deployment. Rigby will preserve these blocks exactly as-is, even if the surrounding system content changes.

## Creating an Evolution Package

To create your own evolution:

1. Create directory: `evolutions/{your-evolution-id}/`
2. Create manifest: `evolution.manifest.json` (see example-evolution-2026-03)
3. Add files in same structure as they appear in IES
4. Test with `rigby validate`
5. Deploy with `rigby deploy`

See `example-evolution-2026-03/` for reference structure.

## Manifest Format

Every evolution requires an `evolution.manifest.json` file:

```json
{
  "id": "unique-evolution-id",
  "version": "2026.03",
  "name": "Human-readable name",
  "description": "What this evolution does",
  "released": "2026-02-25",
  "type": "system",
  "compatibility": {
    "minimum_base_version": "2026.01"
  },
  "files": [
    {
      "path": "relative/path/to/file.md",
      "type": "system|personal|mixed",
      "action": "add|replace|merge|delete",
      "description": "What this file change does"
    }
  ],
  "changelog": [
    "User-facing change descriptions"
  ]
}
```

## File Actions

| Action | Use When | Safety |
|--------|---------|--------|
| `add` | Creating new file | Safe — won't overwrite |
| `replace` | Full file replacement (system-only) | Requires no personal blocks |
| `merge` | Updating file with personal blocks | Preserves personal content |
| `delete` | Removing obsolete file (system-only) | Requires no personal blocks |

## Safety Features

Every evolution deployment includes:

- ✓ Manifest validation
- ✓ Compatibility checking
- ✓ Automatic snapshots
- ✓ Personal block scanning
- ✓ Conflict detection
- ✓ Rollback capability
- ✓ Integrity verification
- ✓ History logging

**Rigby never skips steps.** If something's wrong, she'll surface it and wait for your decision.

## Questions?

See [docs/Evolution System.md](../docs/Evolution%20System.md) for complete documentation.

Ask Rigby: `rigby help` or chat with her about evolution management.

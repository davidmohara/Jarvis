---
name: rigby-package-create
description: Discover custom agents, workflows, and skills; package them for contribution to the IES ecosystem
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Package Create

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Package executive-created custom agents, workflows, and skills for contribution to the IES ecosystem. This is the authoring half of the contribution lifecycle — preparing a package that can be submitted via `rigby-package-submit` (Story 11.2).

**Critical rules:**
- NEVER include personal data in packages (identity/, context/, training/, data/, documents/)
- Package creation is read-only — NEVER modify the executive's working system files
- Each submission becomes a NEW contribution version (not an update to an existing package)

## Input

`$ARGUMENTS` — accepts:
- `--name "My Package"` — package name (kebab-case recommended)
- `--version "1.0.0"` — semver version (MAJOR.MINOR.PATCH required)
- `--description "..."` — what this package provides
- `--author "Name"` — author name (defaults to identity if available)
- `--components agent:my-agent,workflow:my-workflow,skill:my-skill` — specific components to include
- `--test` — run local verification test after packaging
- (no args) — interactive component discovery and selection

## Process

### 1. Read Configuration

Read `evolution.manifest.json` to:
- Identify which files are part of the base system (must not be packaged as "custom")
- Determine the current `evolution_level` (used as `min_evolution` in the contribution manifest)

Read `config/settings.json` for any author defaults.

Read the Claude settings file to extract the `mcpServers` map — a dictionary of server name → `{ command, args?, env? }`. Check in this order and use the first that exists:
1. `.claude/settings.local.json` — preferred (this is where MCP servers are stored when configured locally and not committed to version control)
2. `.claude/settings.json` — fallback (project-level settings)

If neither file exists or neither contains an `mcpServers` key, the `mcpServers` map is empty. This map is used in Step 5 to embed the relevant MCP connection configuration in the package so recipients can replicate the same setup.

Build the **base system files set**: collect all `file` values from `evolution.manifest.json`'s `components` section (agents, workflows, skills, config, etc.) into a set of known base paths.

### 2. Discover Custom Components

Scan three locations for custom components — files/directories NOT in the base system files set:

**Agents** — scan `agents/*.md`:
- For each `.md` file: if its relative path (`agents/{name}.md`) is NOT in the base set → it's custom
- Record: name (filename without `.md`), type = `agent`, file path

**Workflows** — scan `workflows/*/`:
- For each subdirectory: if `workflows/{dir}/workflow.md` is NOT in the base set → it's custom
- Record: name (directory name), type = `workflow`, all file paths under that directory recursively (excluding dotfiles)

**Skills** — scan `.claude/skills/*.md`:
- For each `.md` file: if its path is NOT in the base set → it's custom
- Record: name (filename without `.md`), type = `skill`, file path

If no custom components are found:

```
No custom components found in your IES instance.

Scanned:
  - agents/*.md (vs base system)
  - workflows/*/ (vs base system)
  - .claude/skills/*.md (vs base system)

To create custom components, add new agent files to agents/, workflow directories
to workflows/, or skill files to .claude/skills/.
```

Exit.

### 3. Display and Select Components

If `--components` argument provided: parse and validate each entry (format: `type:name`).

If not provided: display discovered components and prompt for selection.

Display:

```
Custom components found:

  Agents:
    [ ] my-custom-agent     agents/my-custom-agent.md
    [ ] another-agent       agents/another-agent.md

  Workflows:
    [ ] my-workflow         workflows/my-workflow/ (3 files)

  Skills:
    [ ] my-skill            .claude/skills/my-skill.md

Select components to include (e.g., "all", "agent:my-custom-agent,workflow:my-workflow"):
```

Wait for selection. Accept:
- `all` — include every discovered component
- `type:name` comma-separated — specific components
- Numbers (if displayed with numbers) — select by index

### 4. Gather Package Metadata

If `--name`, `--version`, `--description` are all provided via arguments: use them directly.

Otherwise, prompt for any missing fields:
- `name` — package name (kebab-case, no spaces; e.g., "my-pipeline-workflow")
- `version` — semver MAJOR.MINOR.PATCH (e.g., "1.0.0")
- `description` — what this package provides to other executives
- `author` — contributor name (attempt to read from `identity/MISSION_CONTROL.md` if not provided)

### 5. Detect Dependencies

For each selected component, read its file content and detect external dependencies:

**MCP server dependencies** — scan for `mcp__server_name__` patterns:
- Extract server name from `mcp__NAME__` occurrences
- Deduplicate; only record dependencies on servers NOT already in the package
- For each detected server name, look it up in the `mcpServers` map read in Step 1
  - If found: record its full configuration `{ command, args?, env? }` for embedding in the manifest
  - If not found in `.claude/settings.json`: record the server name only (as a named dependency)
- The collected MCP configurations become the `mcp_settings` field in the manifest (Step 6)

**Agent dependencies** — scan for `agent: NAME` or `agent:NAME` patterns:
- Only record agents NOT already included in the selected components

**Workflow dependencies** — scan for `workflow: NAME` references:
- Only record workflows NOT already included in the selected components

**Skill dependencies** — scan for `skill: NAME` or invoke-skill references:
- Only record skills NOT already included in the selected components

### 5b. Architectural Compliance Checks

Run these checks on every selected component file before generating the manifest. These are **automatic corrections**, not prompts — apply them and note what was changed in the Step 10 output.

#### KMS-Agnostic Check

Scan all component files for hardcoded knowledge management system bindings:
- Obsidian-specific: `mcp__obsidian`, `obsidian-mcp-tools`, `vault-conventions`, references to `.md` vault paths assumed to be Obsidian, `append_to_vault`, `create_vault_file`, `get_vault_file`, `patch_vault_file`, `update_active_file`
- Any other named KMS tool calls (e.g., Notion, Roam)

If found:
1. Replace hardcoded KMS tool calls with a generic **KMS adapter interface** contract:
   - Define the required operations: `kms.list`, `kms.read`, `kms.write`, `kms.append`, `kms.exists`
   - Document that the caller must supply a `kms` config key pointing to a connector that satisfies these operations
   - The reference implementation (e.g., Obsidian) goes in a comment block, not in the logic path
2. Add `kms` to `config_keys` in the manifest with `default: "obsidian"` and `supported_values: ["obsidian", "notion", "roam", "logseq"]`
3. Record: `"Abstracted KMS binding: {original tool} → kms adapter interface"`

If no hardcoded KMS bindings found: skip silently.

#### Dataverse-Aware Calendar/Email Check

Scan all component files for hardcoded calendar or email data source bindings:
- M365-specific: `mcp__claude_ai_Microsoft_365__outlook_calendar`, `outlook_calendar_search`, `outlook_email_search`, `mcp__claude_ai_Microsoft_365__`
- Google-specific: `google_calendar`, `mcp__google__calendar`, `gmail`
- Any UUID-embedded MCP calls (e.g., `mcp__b8c41a14__*`) — these are instance-specific M365 auth tokens

If found:
1. Replace hardcoded calendar/email tool calls with a **dataverse dispatch table**:
   ```
   dataverse: m365  → mcp__claude_ai_Microsoft_365__outlook_calendar_search / outlook_email_search
   dataverse: google → [google calendar / gmail MCP tool]
   ```
   The skill reads the `dataverse` config key at runtime and routes accordingly.
2. Add `dataverse` to `config_keys` in the manifest with `default: "m365"` and `supported_values: ["m365", "google"]`
3. Record: `"Abstracted calendar/email binding: {original tool} → dataverse dispatch (m365/google)"`

If no hardcoded calendar/email bindings found: skip silently.

#### Task Manager Check

Scan for hardcoded task management bindings:
- OmniFocus-specific: `mcp__omnifocus__*`, `tell application "OmniFocus"`, `omnifocus-tasks`
- AppleScript task patterns targeting any named task app

If found:
1. Replace with a **task manager adapter interface**: `tasks.create`, `tasks.query`, `tasks.complete`
2. Add `task_manager` to `config_keys` with `default: "omnifocus"` and `supported_values: ["omnifocus", "todoist", "asana", "things3", "ms-todo"]`
3. Record: `"Abstracted task manager binding: {original} → task_manager adapter interface"`

#### CRM / Relationship Intelligence Check

Scan for hardcoded CRM bindings:
- Clay-specific: `mcp__clay__*`, `mcp__cca9d37e__*`, `searchContacts`, `getUpcomingReminders`, `getRecentReminders`
- HubSpot, Salesforce, or other named CRM tool calls

If found:
1. Replace with a **crm adapter interface**: `crm.search_contacts`, `crm.get_contact`, `crm.upcoming_reminders`, `crm.recent_interactions`
2. Add `crm` to `config_keys` with `default: "clay"` and `supported_values: ["clay", "hubspot", "salesforce", "pipedrive", "airtable"]`
3. Record: `"Abstracted CRM binding: {original} → crm adapter interface"`

#### Notification Channel Check

Scan for hardcoded messaging/notification bindings:
- Slack channel IDs: string constants matching `C[A-Z0-9]{10}` (e.g., `C0AN2PQNXBR`)
- Slack user IDs: string constants matching `U[A-Z0-9]{10}` (e.g., `U0ANHV5UXEW`)
- Hardcoded Slack bot scripts: `systems/slack-bot/post.py`, `master-slack` invocations with channel literals
- Teams-specific webhook or channel references

If found:
1. Replace hardcoded channel/user IDs with config references:
   ```
   notification_channel: jarvis   → config key: notifications.jarvis_channel_id
   notification_channel: user_dm  → config key: notifications.user_dm_id
   ```
2. Add `notification_channel` to `config_keys` with `default: "slack"` and `supported_values: ["slack", "teams", "discord"]`
3. Note that channel IDs must be supplied at install time — they cannot have defaults
4. Record: `"Abstracted notification binding: {original ID} → notification_channel config key"`

#### Meeting Platform Check

Scan for hardcoded meeting platform bindings used in transcript workflows:
- Teams-specific: `mcp__claude_ai_Microsoft_365__chat_message_search`, Teams transcript fetch patterns, `teams-transcript`
- Zoom-specific: Zoom API or MCP calls
- Google Meet references

If found:
1. Replace with a **meeting_platform dispatch table**:
   ```
   meeting_platform: teams  → M365 MCP transcript fetch
   meeting_platform: zoom   → Zoom MCP transcript fetch
   ```
2. Add `meeting_platform` to `config_keys` with `default: "teams"` and `supported_values: ["teams", "zoom", "google-meet"]`
3. Record: `"Abstracted meeting platform binding: {original} → meeting_platform dispatch"`

#### Health Tracker Check

Scan for hardcoded health/fitness data bindings:
- WHOOP-specific: `mcp__whoop__*`, `whoop-get-recovery`, `whoop-get-sleep`, `whoop-get-workout`
- Oura, Garmin, Apple Watch references

If found:
1. Replace with a **health_tracker adapter interface**: `health.get_recovery`, `health.get_sleep`, `health.get_workouts`, `health.get_body_measurements`
2. Add `health_tracker` to `config_keys` with `default: "whoop"` and `supported_values: ["whoop", "oura", "garmin", "apple-health"]`
3. Record: `"Abstracted health tracker binding: {original} → health_tracker adapter interface"`

#### Personal Reference Check (Hard Stop)

Scan for references that are personal to the executive's instance and should **never** appear in a shared package. These are not abstraction candidates — they must be removed entirely:
- Personal names used as logic targets (e.g., physician names, direct report names hardcoded as strings)
- Company/client names hardcoded in skill logic (vs. read from config or identity)
- Specific file paths containing a home directory username (`/Users/davidohara/`, `/home/david/`)
- Personal account identifiers embedded in tool calls

If found:
1. **Do not auto-correct.** Report each instance explicitly:
   ```
   ⚠ Personal reference found: "{file}" contains "{pattern}" — must be replaced with a config read or removed before packaging.
   ```
2. Halt packaging and ask the executive how to handle each one before proceeding.

#### Config Keys in Manifest

Any `config_keys` collected from the above checks are added to the manifest as a top-level field. Only include keys that were actually triggered:
```json
"config_keys": {
  "kms":                  { "default": "obsidian", "supported_values": ["obsidian", "notion", "roam", "logseq"] },
  "dataverse":            { "default": "m365",     "supported_values": ["m365", "google"] },
  "task_manager":         { "default": "omnifocus","supported_values": ["omnifocus", "todoist", "asana", "things3", "ms-todo"] },
  "crm":                  { "default": "clay",     "supported_values": ["clay", "hubspot", "salesforce", "pipedrive", "airtable"] },
  "notification_channel": { "default": "slack",    "supported_values": ["slack", "teams", "discord"], "note": "channel IDs must be set at install time" },
  "meeting_platform":     { "default": "teams",    "supported_values": ["teams", "zoom", "google-meet"] },
  "health_tracker":       { "default": "whoop",    "supported_values": ["whoop", "oura", "garmin", "apple-health"] }
}
```
Omit the field entirely if no config keys were collected.

### 6. Generate Package Manifest

Build `package.manifest.json`:

```json
{
  "name": "{name}",
  "version": "{version}",
  "description": "{description}",
  "author": "{author}",
  "min_evolution": "{evolution_level from evolution.manifest.json}",
  "components": [
    {
      "name": "{component-name}",
      "type": "{agent|workflow|skill}",
      "files": ["{relative-path-1}", "{relative-path-2}"]
    }
  ],
  "capabilities": [],
  "defaults_replaced": {},
  "dependencies": {
    "mcp_servers": [],
    "agents": [],
    "workflows": [],
    "skills": []
  },
  "mcp_settings": {
    "{server-name}": {
      "command": "{command}",
      "args": ["{args}"]
    }
  }
}
```

**`capabilities` field** — array of capability names this package declares (e.g., `["contact-management"]`). Connector packages must populate this so agents and the connector registry know what behavior the package enables. Non-connector packages (agent/workflow/skill packages) leave this empty. See `reference/connectors.md` for the standardized capability name list.

**`defaults_replaced` field** — map of capability name → plain-language description of what default behavior this connector replaces. Example: `{ "contact-management": "Replaces local people/ directory for contact lookup" }`. Omit for non-connector packages.

**`mcp_settings` field** — omit if no MCP servers were detected. When present, this field contains one entry per detected MCP server, taken directly from the `mcpServers` map in `.claude/settings.json`. This allows the recipient to replicate the exact MCP connection configuration needed for the capability. Environment variable values should be included as-is (recipients will supply their own credentials at install time).

### 7. Validate Package

Run validation before assembling the package:

**Manifest structure validation:**
- name is non-empty string
- version matches MAJOR.MINOR.PATCH semver (e.g. 1.0.0)
- description is non-empty string
- author is non-empty string
- min_evolution is present
- components is a non-empty array with valid entries (each has name, type, files)

**File existence validation:**
- Every declared component file path must exist on disk
- If any file is missing: report the missing path and stop

**Personal data protection:**
- Reject any file path under: `identity/`, `context/`, `training/`, `data/`, `documents/`
- These directories contain the executive's private data — NEVER include them in packages
- Report error with clear message if found

**Dependency validation:**
- External dependencies are declared in the manifest — no file existence required for them
- Warn if a component file contains non-empty `<!-- personal:start -->` blocks (will be stripped)

If validation fails:

```
Package validation failed:
  Errors:
    ✗ {error with remediation guidance}

Fix the errors above and re-run to create the package.
```

Exit.

If validation passes with warnings:

```
Validation passed with warnings:
  Warnings:
    ⚠ {warning}

These warnings are informational. Proceeding with packaging...
```

### 8. Assemble Package Directory

**Conflict check:**

Before writing any files, check whether `contributions/{name-slug}-{version}/` already exists.

If it does:

```
⚠ Package contributions/{name-slug}-{version}/ already exists.
  Overwrite the existing package? (yes/no)
```

Wait for response. If no: exit with `"Package creation cancelled. Increment the version or rename the package and re-run."`

Create the package directory at `contributions/{name-slug}-{version}/` (use `{name}` slugified — replace spaces and special chars with hyphens):

Write `package.manifest.json` to the package directory root.

For each component file:
1. Read the file content
2. If the content contains `<!-- personal:start -->` blocks with content between markers:
   - Strip the content between markers
   - Preserve the empty markers as placeholders: `<!-- personal:start -->\n<!-- personal:end -->`
   - This protects the executive's personal data
3. Write the processed content to the package directory at the same relative path
4. Create subdirectories as needed

**Never modify the original working files** — only write to `contributions/{name-slug}-{version}/`.

### 9. Optional Local Test (if --test flag provided)

Create an isolated test environment at `contributions/.test-{name-slug}/`:
- Copy all package files from the assembled package directory
- Verify all declared files are present in the test environment
- Check `package.manifest.json` is valid JSON

Report:

```
Local test: PASSED
  ✓ package.manifest.json present and valid
  ✓ {n} component files verified
  Test environment: contributions/.test-{name-slug}/
```

Or:

```
Local test: FAILED
  ✗ {error}
```

Clean up the test directory after verification.

### 10. Output Summary

```
✓ "{name}" v{version} packaged successfully

  Author: {author}
  Min evolution: {min_evolution}
  Components: {count}
    {count} agent(s)
    {count} workflow(s)
    {count} skill(s)
  Dependencies: {mcp_count} MCP, {agent_count} agents, {workflow_count} workflows, {skill_count} skills
  Config keys: {config_keys list, or "none"}
  Architectural corrections: {list each correction from Step 5b, or "none"}
  Package: contributions/{name-slug}-{version}/
    package.manifest.json
    {file-1}
    {file-2}
    ...

  Next step: Use rigby-package-submit to submit this package for review.
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Config**: Read `evolution.manifest.json`, `config/settings.json`, `.claude/settings.local.json` then `.claude/settings.json` (for `mcpServers` map), `identity/MISSION_CONTROL.md`
- **Discovery**: Glob/list `agents/`, `workflows/`, `.claude/skills/` directories
- **Files**: Read component files; Write to `contributions/{name}-{version}/`; NEVER write to original locations
- **Validation**: Read each component file to check for personal data patterns
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

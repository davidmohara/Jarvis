---
name: rigby-evolution-download
description: Download an evolution package from the web app and apply it to the local IES instance
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Evolution Download & Apply

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Download an evolution from the web app and apply it locally. This covers the full apply lifecycle: download → verify → run evolution-deployment workflow → record in history → report usage.

## Input

`$ARGUMENTS` — accepts one of:
- `--id {evolution-id}` — download by database ID (the `id` field from the poll cache)
- (no args) — prompt to choose from available evolutions in poll cache

Evolution versions are UUID v4 — not human-readable version numbers. Always identify and display evolutions by their **name**, not their UUID.

## Process

### 1. Resolve the Evolution

**If `--id` provided:** use it directly.

**If no args:** read `evolutions/.poll-cache.json`. If empty or no available evolutions, run the poll skill first:
```
@rigby-evolution-poll
```
Then re-read the cache. If still empty: `No evolutions available. Your system is up to date.`

Present the available list to the executive and ask which to apply.

### 2. Read Configuration and Authenticate

Read `config/settings.json` and extract:
- `ies_app_url` — base URL of the IES web application

**Authenticate:** Read and follow `systems/auth/preamble.md` to obtain a valid access token. Use the resolved `ACCESS_TOKEN` for all API calls in this skill.

### 3. Download the Package

Call: `GET {ies_app_url}/api/evolutions/{id}/package`
Authorization: Bearer `{ACCESS_TOKEN}`

**On failure:**
- HTTP 401: Follow self-healing in `systems/auth/preamble.md` Step D — invoke `rigby-register`, get fresh token, retry once. If retry also 401: `Authentication failed — server may not support bearer tokens yet`
- HTTP 404: `Evolution package not found on server (may not have files uploaded yet)`
- Network error: `Could not reach {ies_app_url} — check your internet connection`

**On success:** parse JSON response containing `{ id, version, name, manifest, files }`.

### 4. Save Package Locally

Slugify the evolution name for the directory (e.g., "Spring Refresh" → `spring-refresh`).

Write the downloaded files to `evolutions/ies-{name-slug}/`:
- Write `evolution.manifest.json` from the `manifest` field
- For each entry in `files`: write content to `evolutions/ies-{name-slug}/{path}`
- Create subdirectories as needed

Verify: confirm `evolution.manifest.json` exists and all files listed in manifest are present.

### 5. Display Manifest for Review

Show the executive:
```
Evolution: {name}
{description}

What changes:
{changelog bullets}

Files affected: {count}
  {count} to add
  {count} to replace
  {count} to merge (personal content preserved)
  {count} to delete

Minimum IES version required: {minimum_base_version}
```

Ask: `Apply this evolution? (yes / skip / view details)`
- `view details` → show full file list with actions
- `skip` → exit; evolution remains downloaded for later

### 6. Apply the Evolution

Run the evolution-deployment workflow:

```
Read and execute: workflows/evolution-deployment/workflow.md
evolution_path: evolutions/ies-{name-slug}
```

The workflow handles:
- Manifest validation (Step 01)
- Compatibility check (Step 02)
- Snapshot creation (Step 03)
- Personal block scanning (Step 04)
- File application with merge (Step 05)
- Integrity verification and history logging (Step 06)

**Do NOT duplicate the workflow logic here — delegate fully to the workflow.**

### 7. Report Usage to Web App (Non-Blocking)

After successful local application, report usage to the web app for analytics.
This is informational only — failure does not affect the local application.

If evolution has a known `id` from the download response, call the `markApplied` tRPC procedure:

```
POST {ies_app_url}/api/trpc/evolutions.markApplied
Authorization: Bearer {ACCESS_TOKEN}
Body: { "evolutionId": "{id}" }
```

If this call fails: log silently `[evolution-download] Usage report failed — continuing` and proceed.

### 8. Post-Apply Summary

After the workflow completes, display to executive:

```
✓ "{name}" applied successfully

What's new:
{changelog bullets}

{training_prompts — "Try this:" suggestions if any}

Applied: {name} (UUID recorded in evolutions/history.md)
Rollback available: yes (snapshot in evolutions/snapshots/)
```

Update `evolutions/.poll-cache.json`: remove the applied evolution from the `available` array.

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/rigby-evolution-download-latest.json
```

Content:
```json
{
  "skill": "rigby-evolution-download",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill rigby-evolution-download
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/rigby-evolution-download.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **HTTP**: Bash `curl` for downloading from and reporting to web app
- **Files**: Read, Write, Glob for package assembly and verification
- **Workflow**: Run `workflows/evolution-deployment/workflow.md` for the actual apply
- **Config**: Read `config/settings.json` for connection details
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: knowledge-ingest
description: Unified ingestion pipeline — any new content from any capture surface gets normalized, tagged, linked, and filed in the vault
owner: knox
evolution: personal
model: haiku
---

<!-- personal:start -->
# Knowledge Ingest Workflow

Unified pipeline for ingesting content into the Obsidian vault from any capture surface. One workflow, multiple input sources.

## Entry Conditions

Triggered when:
- Chief requests knowledge sync during boot or daily review
- Controller says "sync my stuff" or "pull everything"
- A specific source sync is requested (Remarkable, Plaud, manual capture)

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

---

## EXECUTION

Run STATE CHECK above, then begin at step-01.

---

## Steps

| Step | File | Description |
|------|------|-------------|
| 01 | `steps/step-01-discover.md` | Check all capture surfaces for new/updated content |
| 02 | `steps/step-02-ingest.md` | Pull content from each source using source-specific skills |
| 03 | `steps/step-03-normalize.md` | Convert all content to markdown with standard frontmatter |
| 04 | `steps/step-04-link.md` | Cross-reference against people (Clay), projects (OmniFocus), and existing vault notes |
| 05 | `steps/step-05-file.md` | Save to correct vault location, create directories as needed |
| 06 | `steps/step-06-route.md` | Route action items to OmniFocus, flag content for other agents |
| 07 | `steps/step-07-report.md` | Summarize what was ingested, linked, and routed |

## Source Registry

| Source | Skill | Check Method |
|--------|-------|-------------|
| reMarkable | `remarkable-sync` | `rmapi ls` vs sync manifest |
| Plaud AI | `knox-transcripts-plaud` | Plaud API vs zzPlaud folder |
| Manual capture | (inline) | Controller provides content directly |

## Standard Frontmatter

All ingested notes must include:

```yaml
---
source: {remarkable|plaud|manual|email}
synced: {ISO timestamp}
remarkable_path: {path}  # if from Remarkable
plaud_id: {id}           # if from Plaud
pages: {count}           # if multi-page
tags: []                 # added during linking step
linked_contacts: []      # Clay contact IDs
linked_projects: []      # OmniFocus project names
---
```

## Rollback Protocol

This workflow only adds files to the vault — it never modifies or deletes existing content. If an ingest produces bad output, delete the specific file from the vault. The sync manifest tracks what was processed, so re-running will skip already-ingested items unless the manifest is reset.
<!-- personal:end -->

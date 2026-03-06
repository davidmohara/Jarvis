---
name: knowledge-ingest
description: Unified ingestion pipeline — any new content from any capture surface gets normalized, tagged, linked, and filed in the vault
owner: knox
evolution: personal
---

<!-- personal:start -->
# Knowledge Ingest Workflow

Unified pipeline for ingesting content into the Obsidian vault from any capture surface. One workflow, multiple input sources.

## Entry Conditions

Triggered when:
- Chief requests knowledge sync during boot or daily review
- Controller says "sync my stuff" or "pull everything"
- A specific source sync is requested (Remarkable, Plaud, manual capture)

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
| Plaud AI | `knox-plaud` | Plaud API vs zzPlaud folder |
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

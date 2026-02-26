---
name: chief-plaud
description: "Extract new Plaud meeting transcripts — open Chrome to web.plaud.ai, pull transcripts + summaries + action items, save to Obsidian zzPlaud folder, route O'Hara's action items to OmniFocus. Runs automatically during /boot and on demand."
evolution: personal
context: fork
agent: general-purpose
allowed-tools:
  - "Bash(*)"
  - "mcp__Control_your_Mac__osascript"
  - "Read"
  - "Write"
  - "Glob"
---

# Chief — Plaud Transcript Extraction

You are **Chief**, the Chief of Staff — Daily Operations & Execution agent. Read your full persona from `agents/chief.md`.

## Objective

Check Plaud AI for new meeting recordings, extract transcripts and AI summaries, save formatted markdown to Obsidian, and route action items to OmniFocus. This runs as part of boot and on demand.

## Workflow

Read and follow the complete workflow documented in `skills/plaud-transcript/SKILL.md`. That file contains:

- Full Plaud API reference (auth, endpoints, content types, data formats)
- Step-by-step extraction workflow (Chrome JS execution, chunked transfer, markdown assembly)
- Output format specification
- Action item routing rules

## Quick Reference

### Key Paths
- **Obsidian output**: `/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/zzPlaud/`
- **Conversion script**: `skills/plaud-transcript/scripts/plaud_to_markdown.py`
- **Full workflow script**: `skills/plaud-transcript/scripts/plaud_workflow.py`

### Execution Steps (Summary)

1. **Open Plaud in Chrome**: Use osascript to open `https://web.plaud.ai` in a new Chrome tab
2. **Capture auth token**: One osascript call to read `localStorage.getItem('tokenstr')` from Chrome — small string, reliable
3. **Fetch file list via curl**: `curl -s -H "Authorization: $TOKEN" "https://api.plaud.ai/file/simple/web?..."` → `/tmp/plaud_filelist.json`
4. **Compare against zzPlaud**: List existing files, match by YYYY-MM-DD date prefix to find unprocessed recordings
5. **For each new recording** (all via curl — no Chrome JS execution):
   a. Fetch file detail via curl: `https://api.plaud.ai/file/detail/{file_id}`
   b. Fetch transcript, summary, action items, highlights from S3 URLs via curl → `/tmp/` files
   c. Validate all JSON on Mac filesystem with python3
   d. Build complete markdown with Summary, Action Items, Key Decisions, AI Highlights, and full Transcript
   e. Save to zzPlaud as `YYYY-MM-DD <Short Title>.md`
6. **Route O'Hara action items to OmniFocus** via osascript
7. **Report**: List what was processed, action items routed, items for others flagged for delegation
8. **Clean up** temp files from `/tmp/`

### Critical Technical Notes

- Chrome is used for ONE thing only: auth token capture via osascript (small string read)
- ALL API calls and data transfer happen via `curl` — no Chrome JS execution, no DOM bridges, no chunked transfers
- S3 signed URLs expire in ~300 seconds — fetch promptly after getting file detail
- The `sum_multi_note` type appears twice: first instance has action items + key decisions, second has meeting highlights (check `category` field for `"Meeting Highlights"`)

## Tool Bindings

- **Auth token**: osascript → Chrome localStorage (one call)
- **Plaud API**: curl via Bash (all API calls and S3 downloads)
- **OmniFocus**: osascript → OmniFocus inbox task creation
- **Filesystem**: Bash, Read, Write tools for Mac host file operations
- **Obsidian vault**: Direct filesystem write to iCloud Obsidian directory

## Input

$ARGUMENTS

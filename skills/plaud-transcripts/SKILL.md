---
name: plaud-transcripts
description: >
  Process Plaud.ai recording transcripts from a staging folder and convert them into
  tagged Obsidian markdown notes filed into the user's vault. Use this skill whenever
  the user mentions Plaud transcripts, Plaud recordings, importing Plaud notes, or
  wants to process recordings from their Plaud device into Obsidian. Also trigger on
  "process my Plaud recordings", "import Plaud transcripts", "get my Plaud notes into
  the vault", "sync Plaud to Obsidian", or any request involving Plaud recordings
  becoming vault notes. A scheduled task pre-fetches Plaud data daily via the API, so
  this skill's job is to transform what's already waiting in the staging folder into
  proper Obsidian notes.
---

# Plaud Transcripts → Obsidian

Transform pre-fetched Plaud.ai recording transcripts into properly tagged Obsidian
markdown notes and file them into the vault.

## How this works

Plaud transcripts arrive in a staging folder via a daily scheduled task that calls
the Plaud API. By the time this skill runs, the raw transcript files are already
sitting in `~/Downloads/transcript-staging/` as markdown files with a `plaud_` prefix.
Each file contains the recording title, date, duration, an AI summary (when available),
and the full transcript text.

This skill reads those staged files, enriches them with proper frontmatter tags,
restructures them into the vault's note format, routes them to the correct folder,
and cleans up the staging files when done.

## Prerequisites

- **Pre-fetched Plaud files** in `~/Downloads/transcript-staging/` — these are
  produced by the `plaud-daily-fetch` scheduled task or by manually running
  `scripts/fetch_plaud.py` with a valid bearer token
- **Write access to the Obsidian vault** — look for it in the mounted directories. `references\vault-conventions.md` contains first-run interactions to setup. Run that once when intiializing this skill for the first time.

If no Plaud files are found in staging, tell the user. They may need to:
1. Run the fetch script manually: `PLAUD_TOKEN="<token>" python3 ~/Downloads/transcript-staging/fetch_plaud.py`
2. Or check that the `plaud-daily-fetch` scheduled task is running
3. Or export recordings from the Plaud app and drop them in the staging folder

## Execution

### 1. Scan the staging folder

Look in `~/Downloads/transcript-staging/` for files matching:
- `plaud_*.md` — processed transcript files from the fetch script
- `plaud_*_raw.json` — raw API responses (useful for metadata extraction)

Also check for any `.txt` files that might be manual Plaud exports.

### 2. Parse each transcript file

The fetch script produces markdown files with this structure:

```markdown
# <Recording Title>

**Date:** YYYY-MM-DD
**Duration:** <seconds>s
**Source:** Plaud AI

## AI Summary

<AI-generated summary from Plaud, if available>

## Transcript

[MM:SS] **Speaker**: What they said

[MM:SS] **Another Speaker**: Their response
```

Extract:
- Title (from `#` heading)
- Date
- Duration
- AI Summary (use as the basis for the note's Summary section, but rewrite it to
  match the vault's analytical style — don't just copy it verbatim)
- Transcript text with speaker labels

If raw JSON files are available, also extract:
- Speaker names and any speaker identification data
- Tag IDs from Plaud (can inform Obsidian tag selection)
- Additional metadata

### 3. Determine what meeting this recording corresponds to

Plaud recordings often overlap with calendar meetings. Cross-reference the recording
date and time against the user's calendar (if MS 365 MCP is available) to:
- Match the recording to a specific calendar event
- Pull attendee information from the calendar event
- Get the "real" meeting title (Plaud titles are often auto-generated)

If calendar matching isn't possible, use whatever title and metadata the Plaud file
provides.

### 4. Transform into Obsidian notes

Read `references/vault-conventions.md` for the exact format. The key points:

**Filename:** `YYYY-MM-DD <Title>.md`
If there's already a Teams-sourced note for the same meeting (from the teams-transcripts
skill), append ` (Plaud)` to distinguish them — or ask the user if they want to merge.

**Frontmatter tags (2-4 total):**
- `content/meeting` (always)
- `meta/timeline/YYYY/MM/DD` (always)
- 1-2 contextual tags based on content analysis

**Note structure:**
Same as the Teams skill — Meeting Details, Attendees, Summary, Key Discussion Points,
Action Items, and Transcript in a `<details>` block. Platform field should say "Plaud.ai".

Plaud recordings sometimes lack clear speaker identification. When speakers are labeled
as "Speaker 1", "Speaker 2", etc., keep those labels — the user can rename them later.
When no speaker labels exist at all, format as continuous text with paragraph breaks.

### 5. Route and write

Same folder routing as the Teams skill:

| Meeting type | Folder |
|---|---|

Check for filename collisions before writing.

### 6. Link from the daily calendar note

Every meeting note gets a wikilink in the daily calendar note for that date. See
`references/vault-conventions.md` under "Daily Note Cross-Linking" for the full spec.

The short version:
1. Determine the daily note path: `Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md`
2. If the daily note doesn't exist, create it from the template (including the
   year and month folders if needed)
3. Append `- [[<relative-path-to-meeting-note>]]` below it
4. Don't duplicate — check if the link already exists

The wikilink path is relative to vault root, without `.md` extension. For example:
`- [[Improving/Meeting Notes/2026-03-18 Consultation AI Partnership]]`

### 7. Clean up staging

After all notes are successfully written to the vault:
1. Delete the processed `plaud_*.md` files from staging
2. Delete the corresponding `plaud_*_raw.json` files
3. Leave the `fetch_plaud.py` script and any config files intact
4. If the staging folder is now empty (except for scripts), leave it in place

Report what was cleaned up.

### 7. Report

```
Processed X Plaud recordings:

✓ Recording Title → Improving/Meeting Notes/YYYY-MM-DD Recording Title.md (work/client)
✓ Another Recording → Personal/YYYY-MM-DD Another Recording.md (personal/development)

Staging cleanup: removed X transcript files, X raw JSON files
```

## The fetch script

The `scripts/fetch_plaud.py` script handles the API side. It authenticates with
email/password via `POST /auth/access-token`, caches the JWT (~300 day lifetime)
to `~/.config/plaud/token.json`, and auto-refreshes when within 30 days of expiry.

API endpoints (reverse-engineered from plaud-toolkit):
- `GET /file/simple/web` — list recordings (params: skip, limit, is_trash, sort_by, is_desc)
- `GET /file/detail/{id}` — full recording detail including transcript links
- `GET /user/me` — verify auth, returns `data_user` with nickname/email
- Transcript text is fetched from presigned S3 URLs in `content_list` where
  `data_type == "transaction"` and `task_status == 1`
- AI summaries are embedded in `pre_download_content_list` under items with
  `data_id` starting with `auto_sum:`, parsed from `data_content.ai_content`

Required headers beyond Authorization: `app-platform: web`, `edit-from: web`,
`Origin: https://web.plaud.ai`, `Referer: https://web.plaud.ai/`

First run prompts for email/password interactively and optionally saves credentials
to `~/.config/plaud/credentials.json` (mode 0600). Subsequent runs use cached token.

**The script must run on the user's Mac, not inside the VM** — the VM's network
proxy blocks direct API calls to api.plaud.ai. The scheduled task handles this by
running via osascript on the host machine.

## Tag routing

Same taxonomy as the Teams skill — documented in `references/vault-conventions.md`.
Plaud recordings may have less metadata to work with (no attendee emails, sometimes
no clear title), so lean more heavily on transcript content analysis for tagging.

## Error handling

- No files in staging → inform the user, suggest running the fetch script
- Corrupt or empty transcript files → skip and report
- Filename collision with Teams note → ask user: merge, rename with (Plaud) suffix, or skip
- Bearer token expired → tell the user to refresh it from web.plaud.ai DevTools

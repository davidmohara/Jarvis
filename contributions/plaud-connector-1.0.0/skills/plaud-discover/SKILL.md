---
name: plaud-discover
model: haiku
description: >
  Query the Plaud API to enumerate recent recordings and cross-reference against the
  configured knowledge management system (KMS) to identify which ones have not yet been
  ingested. Returns a list of new recording objects with their transcription status.
  Use this skill when you need to know what Plaud recordings exist but haven't been
  processed yet, or when starting the plaud-ingest workflow. Also triggered by "what
  recordings do I have", "check Plaud for new recordings", "any new Plaud notes", or
  similar.
---

# Plaud Discover

Identify Plaud recordings that exist in the API but have not yet been ingested into
the configured knowledge management system (KMS). Output is a structured list of new
recordings with transcription status for each.

## KMS Configuration

This skill is **KMS-agnostic**. The KMS ingest target is determined by `config/settings.json`
(`kms` key). Before enumerating vault notes, check which KMS is configured and use the
appropriate adapter to list notes. See `skills/plaud-transcripts/references/vault-conventions.md`
for the KMS interface contract.

**Reference implementation (Obsidian):** If `kms` is absent or set to `"obsidian"`, use
`mcp__obsidian-mcp-tools__list_vault_files` to enumerate already-ingested notes.

## How this works

The Plaud API's `/file/simple/web` endpoint returns a paginated list of all recordings.
The KMS stores ingested recordings under the meeting root path (e.g., `zzPlaud/` in Obsidian)
with filenames in `YYYY-MM-DD Title.md` format. By comparing these two sets, we can identify
exactly what is new.

This skill does NOT download transcripts — it only enumerates what exists and what's new.
Downloading happens in step-04 of the plaud-ingest workflow.

## Prerequisites

- Valid Plaud API token cached at `~/.config/plaud/token.json`
- Read access to the configured KMS
- If token is missing or expired: run Chrome login flow per `skills/plaud-transcripts/SKILL.md`

## Execution

### 1. Get token and API base

Load token from `~/.config/plaud/token.json`. Extract `access_token` and check `expires_at`.
If within 30 days of expiry, the fetch script will auto-refresh — proceed normally.
If expired, run Chrome login flow before continuing.

Determine API base from `~/.config/plaud/credentials.json` region field:
- `"us"` → `https://api.plaud.ai`
- `"eu"` → `https://api-euc1.plaud.ai`

### 2. Enumerate recordings from Plaud API

Use the fetch script's listing behavior — or call the API directly:

```
GET /file/simple/web
Headers: Authorization: Bearer <token>
         app-platform: web
         edit-from: web
         Origin: https://web.plaud.ai
         Referer: https://web.plaud.ai/
Params: skip=0, limit=50, is_trash=0, sort_by=create_time, is_desc=1
```

Paginate until you have all recordings for the target date range (or all recordings
if doing a catch-up run). For each recording, capture:

```json
{
  "file_id": "...",
  "name": "Recording Title",
  "create_time": "2026-04-15T14:23:00Z",
  "duration": 3421,
  "is_trans": 0 | 1,
  "trans_status": 0 | 1
}
```

Where:
- `is_trans: 0` = no transcription exists (status: `missing`)
- `is_trans: 1` + `trans_status: 0` = transcription in progress (status: `pending`)
- `is_trans: 1` + `trans_status: 1` = transcription ready (status: `ready`)

**Date filtering:**
- For a single date: filter by `create_time` matching target date (UTC)
- For catch-up (`--all` equivalent): no date filter, get all, then dedup against KMS

### 3. Enumerate already-ingested KMS notes

Using the configured KMS adapter, list all files under the meeting root recursively.

**Reference implementation (Obsidian):**
```
mcp__obsidian-mcp-tools__list_vault_files(path="<kms.meeting_root>")
```

Extract the date and title from each filename (`YYYY-MM-DD Title.md`). Build a set of
ingested recording names for fast lookup.

Also check staging: list `~/Downloads/transcript-staging/plaud_*.md`. Files already in
staging from a prior run should be treated as "in progress" rather than "new" — they
will be picked up by step-04 without re-fetching.

### 4. Compute the diff

For each recording from the API:
1. Check if a KMS note exists with a matching date and similar title (fuzzy match — Plaud
   auto-generates titles that may not exactly match what ends up in the KMS).
2. Check if a staged file already exists for this recording.
3. If neither: this recording is **new**.

**Title fuzzy matching:** normalize both strings (lowercase, strip punctuation, collapse
whitespace) before comparing. A match threshold of ~70% similarity is sufficient. When
in doubt, treat as new (safe to create a duplicate note is less bad than missing a recording).

### 5. Return the new-recordings list

Structured as:

```yaml
new_recordings:
  - file_id: abc123
    name: "Meeting with Todd Wynne"
    date: 2026-04-15
    duration_seconds: 3421
    has_transcript: true
    transcript_status: ready   # ready | pending | missing
  - file_id: def456
    name: "One Texas Strategy Call"
    date: 2026-04-15
    duration_seconds: 1820
    has_transcript: false
    transcript_status: missing
```

## Running via the fetch script

As an alternative to direct API calls, you can invoke `fetch_plaud.py` with discovery
intent using osascript:

```
do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py <YYYY-MM-DD> 2>&1"
```

Read the output to identify which recordings were found, their statuses, and which ones
ended up in the pending queue. The script handles pagination, token refresh, and status
detection automatically.

## Error handling

- **API returns 401**: Token expired. Run Chrome login flow. Retry once.
- **API returns 429**: Rate limited. Wait 5 seconds and retry.
- **Empty result set**: Either no recordings for the date, or wrong date/timezone. Try ±1 day.
- **KMS enumeration fails**: Proceed without dedup. Log: "KMS unavailable — may produce duplicates."

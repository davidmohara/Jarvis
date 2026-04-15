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
model: sonnet
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

If no Plaud files are found in staging, run the fetch script (see "Running the
fetch script" below). If the token is missing or expired, use the Chrome login
flow to capture a fresh one before retrying.

If the fetch script still returns nothing, the user may need to:
1. Check that the `plaud-daily-fetch` scheduled task is running
2. Or export recordings from the Plaud app and drop them in the staging folder

## Execution

### 1. Scan the staging folder

Look in `~/Downloads/transcript-staging/` for files matching:
- `plaud_*.md` — processed transcript files from the fetch script
- `plaud_*_raw.json` — raw API responses (useful for metadata extraction)

Also check for any `.txt` files that might be manual Plaud exports.

**Skip `plaud_pending.json`** — this is the retry queue managed by the fetch script.
Recordings with in-progress transcript generation are tracked there and re-checked
on the next fetch run. Do not process pending entries as notes.

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

### 4b. Speaker tagging

After parsing transcripts, check for `plaud_*_speakers.json` files in the staging
folder. These are created by the fetch script when a recording has generic speaker
labels ("Speaker 1", "Speaker 2", etc.).

**Speaker mapping file structure:**
```json
{
  "file_id": "abc123",
  "recording_name": "Meeting Title",
  "all_speakers": [
    {"name": "Speaker 1", "segments_count": 42, "sample_text": "I think we should..."},
    {"name": "Speaker 2", "segments_count": 31, "sample_text": "The timeline for..."}
  ],
  "untagged_speakers": [...],
  "known_speakers": [{"speaker_id": "...", "speaker_name": "David O'Hara", "speaker_type": 1, "sample_counts": {"auto": 4, "mark": 3, "me": 0}}, ...],
  "status": "needs_mapping"
}
```

**Workflow:**

1. For each `_speakers.json` file, present the untagged speakers to David with:
   - Their sample text (first line they spoke — helps identify who's who)
   - Their segment count (more segments = more talkative)
   - The list of known speakers in Plaud (for reference)
   - Calendar attendees for that recording's time slot (if available)

2. Ask David to map each generic label to a real name. Example prompt:
   ```
   "Meeting with Todd Wynne" has 2 untagged speakers:
     Speaker 1 (42 segments): "I think we should look at the AI maturity..."
     Speaker 2 (31 segments): "The timeline for the POC is..."
   Calendar attendees: David O'Hara, Todd Wynne
   Who's who?
   ```

3. Once David provides the mapping, push the renames to Plaud and re-fetch:
   ```
   do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py --rename <file_id> '{\"Speaker 1\": \"David O\\x27Hara\", \"Speaker 2\": \"Todd Wynne\"}' 2>&1"
   ```

4. The `--rename` command (full pipeline):
   - Extracts voice embeddings from `POST /ai/transsumm/{file_id}` → `data_others.embeddings`
   - Maps original speaker labels to new names via `original_speaker` field in segments
   - PATCHes the speaker names in Plaud's transcript via `/file/{file_id}`
   - Registers each new speaker via `POST /speaker/sync` with their 256-float voice embedding
     (skips speakers already in the system)
   - Re-fetches the updated transcript from the API
   - Overwrites the staged markdown with the updated transcript (now with real names)
   - Cleans up the `_speakers.json` file

5. Continue processing the updated markdown file as normal (step 5 onward).

**Important — Speaker Voice Registration:** The `--rename` mode now does TWO things:
1. Renames speaker labels in the transcript (PATCH /file/{file_id} with trans_result)
2. Registers speakers for future auto-labeling (POST /speaker/sync with voice embeddings)

Voice embeddings are extracted from `POST /ai/transsumm/{file_id}` → `data_others.embeddings`,
keyed by original speaker label (e.g. "Speaker 2"). The script maps original labels to the
new names via `original_speaker` field, then syncs each new speaker with their 256-float
embedding. Once registered, Plaud will auto-recognize that voice in future recordings.

Speakers already in the system are skipped (checked via `/speaker/list`).
Without this sync step, renames only change text labels — Plaud won't learn the voice.

### 5. Route and write

All transcripts go under `zzPlaud/`, split by context:

| Meeting type | Folder |
|---|---|
| Client meetings, customer calls, sales discussions | `zzPlaud/Client/` |
| Internal Improving meetings (strategy, ops, 1:1s, all-hands) | `zzPlaud/Improving/` |
| YPO meetings, forum, events, REX calls | `zzPlaud/YPO/` |
| Personal, faith, family, finances, anything else | `zzPlaud/Other/` |

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

## Running the fetch script

**The script must run on the user's Mac, not inside the VM** — the VM's network
proxy blocks direct API calls to api.plaud.ai. Run it via `osascript` on the host:

```
do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py <YYYY-MM-DD> 2>&1"
```

The script requires `requests` — install with `/usr/bin/python3 -m pip install requests`
if missing.

### Token lifecycle

The fetch script caches a JWT (~300 day lifetime) to `~/.config/plaud/token.json`
and auto-refreshes when within 30 days of expiry. When a valid cached token exists,
the script uses it automatically.

When **no token is cached** (first run, expired, or deleted), the script exits with
code 2 and prints `NO_TOKEN`. Do **not** attempt interactive credential prompts —
they will fail in non-interactive contexts. Instead, use the **Chrome login flow**.

### Chrome login flow (no token / expired token)

**Chrome is ONLY used to capture the auth token.** Do NOT use Chrome to browse
the Plaud dashboard, view recordings, read transcripts, or retrieve any other
data. All transcript fetching happens exclusively through the Python fetch script
and the Plaud API. The browser's sole purpose here is to let the user log in so
we can grab the JWT from localStorage — nothing else.

This authentication method uses the user's existing browser session so they never
need to share credentials with the script.

1. Open Chrome to `https://web.plaud.ai`:
   ```
   mcp__Control_Chrome__open_url(url="https://web.plaud.ai", new_tab=true)
   ```

2. Ask the user to log in (or confirm they're on the dashboard if already logged in).

3. Extract the JWT from localStorage:
   ```javascript
   const tokenstr = localStorage.getItem('tokenstr');
   JSON.stringify({token: tokenstr});
   ```
   The value is `"bearer <JWT>"` — strip the `"bearer "` prefix to get the raw token.

4. Decode the JWT payload to extract `iat` and `exp` timestamps (they're in epoch
   seconds — multiply by 1000 for milliseconds).

5. Write the token cache file on the Mac:
   ```
   mkdir -p ~/.config/plaud && chmod 700 ~/.config/plaud
   ```
   Write to `~/.config/plaud/token.json`:
   ```json
   {
     "access_token": "<raw-JWT>",
     "issued_at": <iat * 1000>,
     "expires_at": <exp * 1000>,
     "saved_at": "<ISO-8601>"
   }
   ```
   Set permissions: `chmod 600 ~/.config/plaud/token.json`

6. Also write a minimal credentials file for region detection:
   ```json
   {
     "email": "<user-email-from-plaud>",
     "region": "us"
   }
   ```
   To `~/.config/plaud/credentials.json` (mode 0600). The email can be extracted
   from the localStorage key pattern `PLADU_<email>_redDotShow` visible in the
   same localStorage dump.

7. Re-run the fetch script — it will now pick up the cached token.

### API details

The `scripts/fetch_plaud.py` script handles the API side.

**Core endpoints** (reverse-engineered from plaud-toolkit + arbuzmell/plaud-api):
- `GET /file/simple/web` — list recordings (params: skip, limit, is_trash, sort_by, is_desc)
- `GET /file/detail/{id}` — full recording detail including transcript links
- `GET /user/me` — verify auth, returns `data_user` with nickname/email
- `POST /file/list` — POST with `[file_id]` array, returns `data_file_list` with `trans_result` segments
- `PATCH /file/{file_id}` — update recording metadata (trans_result for renames, extra_data for config)

**Transcription trigger** (two-step, both required):
- `PATCH /file/{file_id}` with `{"extra_data": {"tranConfig": {...}}}` — saves config only
- `POST /ai/transsumm/{file_id}` — actually starts the transcription pipeline
  - `is_reload: 0` for first-time, `is_reload: 1` to re-transcribe
  - Response: `status=0` + `msg="task processing"` while running, `status=1` + `msg="success"` when done
  - Also returns `data_others.embeddings` — per-speaker 256-float voice vectors keyed by original label

**Speaker management:**
- `GET /speaker/list` — returns registered speakers under `data.speakers` (NOT `data_speaker_list`)
  - Each speaker has: `speaker_id`, `speaker_name`, `speaker_type` (1=owner, 2=other),
    `sample_counts` (`auto`/`mark`/`me`), `embeddings` (256-float vectors), timestamps
- `POST /speaker/sync` — register/update speakers with voice embeddings for auto-labeling
  - Payload: `{"speakers": [{"speaker_id": "<uuid>", "speaker_name": "Name", "speaker_type": 2, "embeddings": {"mark": [256 floats]}, "sample_counts": {"auto": 0, "mark": 1, "me": 0}}]}`
  - Returns registered speaker with possible `merged_speaker_id` if voice matches existing profile

**Transcript data:**
- Transcript text is fetched from presigned S3 URLs in `content_list` where
  `data_type == "transaction"` and `task_status == 1`
- AI summaries are embedded in `pre_download_content_list` under items with
  `data_id` starting with `auto_sum:`, parsed from `data_content.ai_content`
- `trans_result` segments contain: `start_time`, `end_time`, `content`, `speaker`,
  `original_speaker` (diarization label), and optionally `embeddingKey` (voice fingerprint UUID)

Required headers beyond Authorization: `app-platform: web`, `edit-from: web`,
`Origin: https://web.plaud.ai`, `Referer: https://web.plaud.ai/`

## Tag routing

Same taxonomy as the Teams skill — documented in `references/vault-conventions.md`.
Plaud recordings may have less metadata to work with (no attendee emails, sometimes
no clear title), so lean more heavily on transcript content analysis for tagging.

## Error handling

- No files in staging → inform the user, suggest running the fetch script
- Corrupt or empty transcript files → skip and report
- Filename collision with Teams note → ask user: merge, rename with (Plaud) suffix, or skip
- Bearer token expired or missing → run the Chrome login flow (see above), then retry the fetch
- **Transcription trigger returns `status=-1` or `status=-12` with `start trans task error`** →
  This almost certainly means **the Plaud account is out of transcription minutes**. Do NOT
  debug API parameters, inspect `ori_ready`, or write test scripts. Ask David first: "Are you
  out of Plaud transcription minutes?" If yes, the recordings must wait until minutes are
  replenished (new billing cycle or plan upgrade). Log the pending recordings and move on.
- Transcript generation pending → fetch script writes to `plaud_pending.json` instead of a
  markdown file. Next fetch run re-checks pending recordings automatically. If pending > 24h,
  flagged as potentially failed generation in the fetch report.
- Transcription triggered (missing → triggered) → fetch script kicks off Plaud's transcription
  pipeline via a two-step API call: (1) PATCH `/file/{file_id}` with `tranConfig` to save settings,
  (2) POST `/ai/transsumm/{file_id}` to actually start the job. **Both steps are required** — the
  PATCH alone returns 200 but does nothing. Knox spawns a sub-agent to watch for completion.
  See "Transcription watcher" below.

## Transcription watcher

When the fetch script triggers a transcription for a recording that had none (`missing` state),
Knox must spawn a sub-agent to poll for completion, process the transcript, and clean up.
No scheduled tasks, no orphaned state — the sub-agent runs, finishes, and exits.

**How it works:**

1. During ingestion, Knox runs `fetch_plaud.py` and sees output like:
   ```
   No transcription exists — triggering Plaud to generate one
   Transcription triggered for <file_id> — will be pending until Plaud finishes
   ```

2. Knox immediately spawns a sub-agent (via the Agent tool) with this mandate:
   - Poll `fetch_plaud.py --check <file_id>` on the Mac host via osascript every 2 minutes
   - Max 30 retries (~1 hour). If still not ready after 30, report failure and exit.
   - When `--check` returns `READY` (exit code 0):
     a. Process the staged transcript through the full knox-plaud pipeline (parse,
        calendar cross-ref, speaker tagging if `_speakers.json` exists, vault write,
        daily note linking, OmniFocus action item routing, cleanup)
     b. Remove the recording from `plaud_pending.json`
     c. Report what was processed and exit

3. The `--check` CLI mode on `fetch_plaud.py`:
   - Takes a single file_id
   - Checks transcription status via the API
   - If ready: fetches transcript, writes to staging, checks for generic speakers,
     writes `_speakers.json` if needed, removes from pending queue, exits 0
   - If not ready: prints `NOT_READY`, exits 3

**Example sub-agent spawn (Knox does this):**
```
Agent(
  description: "Watch Plaud transcription",
  prompt: "You are Knox, the Knowledge Manager. Poll for Plaud transcription
    completion for recording 14d0f41b5dcb80d32ffab947fa94c982.
    Every 2 minutes, run via osascript:
      cd '<scripts-dir>' && /usr/bin/python3 fetch_plaud.py --check 14d0f41b5dcb80d32ffab947fa94c982
    If output contains READY, process the staged transcript through the full
    knox-plaud ingestion pipeline (read skills/plaud-transcripts/SKILL.md for steps).
    If output contains NOT_READY, sleep 2 minutes and retry. Max 30 retries.
    After processing or max retries, clean up the pending queue entry and exit."
)
```

The sub-agent is fully self-contained — no scheduled tasks to clean up, no orphaned
state files. It polls, processes, cleans up, and terminates.

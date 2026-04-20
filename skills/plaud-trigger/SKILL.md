---
name: plaud-trigger
owning_agent: knox
model: haiku
description: >
  Trigger Plaud AI transcription for recordings that have no transcript or are stuck
  in pending state. Handles the two-step API protocol required to start the transcription
  pipeline, monitors pending jobs, and spawns watcher sub-agents for long-running jobs.
  Use when you have recordings with transcript_status: missing or pending and need to
  get them transcribed before ingesting. Also triggered by "kick off transcription",
  "transcribe these recordings", or "why isn't this transcribed yet".
trigger_keywords: [trigger transcription, start transcription]
trigger_agents: [knox]
---

# Plaud Trigger

Start and monitor Plaud AI transcription for recordings that don't have a completed
transcript yet.

## How this works

Plaud's transcription pipeline requires two API calls to start — a PATCH to save
transcription config, then a POST to actually kick off the job. A single PATCH call
returns 200 but does nothing. Both are required. This skill handles both calls correctly
and tracks pending jobs so they don't get lost.

## Prerequisites

- Valid Plaud API token (see `skills/plaud-transcripts/SKILL.md` for login flow)
- A list of recording `file_id` values with `transcript_status: missing` or `pending`

## Execution

### 1. Partition the work queue

Input: list of recordings from `plaud-discover`.

Split into:
- `to_trigger`: recordings with `transcript_status: missing`
- `to_check`: recordings with `transcript_status: pending` (already in progress)
- `already_ready`: recordings with `transcript_status: ready` (pass through, no action)

### 2. For each recording in `to_trigger`: fire the two-step trigger

**Step 1 — Save transcription config:**
```
PATCH {api_base}/file/{file_id}
Headers: Authorization: Bearer <token>
         app-platform: web
         edit-from: web
         Content-Type: application/json
Body: {
  "extra_data": {
    "tranConfig": {
      "language": "en",
      "speakerCount": 0,
      "enableSpeakerDiarization": true
    }
  }
}
```
Expected: HTTP 200. This saves settings only — transcription does NOT start yet.

**Step 2 — Start the transcription pipeline:**
```
POST {api_base}/ai/transsumm/{file_id}
Headers: Authorization: Bearer <token>
         app-platform: web
         edit-from: web
         Content-Type: application/json
Body: {
  "is_reload": 0,
  "language": "en"
}
```
Expected response when triggered successfully:
```json
{"status": 0, "msg": "task processing"}
```

Response codes:
- `status: 0, msg: "task processing"` → triggered successfully, now pending
- `status: 1, msg: "success"` → already done (shouldn't happen for `missing` recordings)
- `status: -1` or `status: -12` → error (likely out of transcription minutes)

**On success:** add `file_id` to both `transcription-triggered` and `to_check` lists.

**On `status: -1` or `-12`:**
- Do NOT debug API parameters or try variations.
- Surface immediately: "Are you out of Plaud transcription minutes?"
- Log to error log. Skip this recording.

### 3. For each recording in `to_check`: verify current status

Re-check via detail endpoint:
```
GET {api_base}/file/detail/{file_id}
```

Parse `content_list` for items where `data_type == "transaction"`:
- `task_status: 1` → ready
- `task_status: 0` → still pending
- No items of type "transaction" → not started (treat as `missing` and trigger)

Move:
- Ready recordings → `already_ready` list
- Still pending → keep in `to_check` for watcher

### 4. Spawn watcher sub-agents for pending recordings

For each recording still in `to_check` after the status check, spawn a watcher
sub-agent per the protocol defined in `skills/plaud-transcripts/SKILL.md` under
"Transcription watcher":

```
Agent(
  description: "Watch Plaud transcription",
  prompt: "You are Knox, the Knowledge Manager. Poll for Plaud transcription
    completion for recording {file_id} ('{name}').
    Every 2 minutes, run via osascript:
      cd '<scripts-dir>' && /usr/bin/python3 fetch_plaud.py --check {file_id}
    If output contains READY: write the staged file path to
    workflows/plaud-ingest/state.yaml accumulated-context.staged-files, then exit.
    If output contains NOT_READY: wait 2 minutes and retry. Max 30 retries (~1 hour).
    After 30 retries with no result: log the timeout and exit."
)
```

Spawn all watchers in parallel. The plaud-ingest workflow does not wait for them —
it continues to step-03 with whatever is `already_ready`. Watcher completions
arrive asynchronously and are picked up in step-04/05.

### 5. Return results

```yaml
triggered: [file_ids...]
pending_with_watcher: [file_ids...]
ready_passthrough: [file_ids...]
skipped_minutes_exhausted: [file_ids...]
```

## Pending queue persistence

The fetch script maintains `~/Downloads/transcript-staging/plaud_pending.json` as a
retry queue. When using the fetch script directly, it handles this automatically.
When calling the API directly (as above), manually write triggered recordings to this
file so the next fetch script run picks them up:

```json
{
  "file_id": {
    "name": "Recording Title",
    "date": "2026-04-15",
    "triggered": true,
    "triggered_at": "2026-04-15T09:00:00Z"
  }
}
```

## Error handling

| Error | Action |
|-------|--------|
| `status: -1` or `-12` from transsumm | Ask about transcription minutes. Log. Skip. |
| PATCH step returns non-200 | Retry once with 2s delay. If still fails, skip and log. |
| POST step times out | Assume triggered. Add to pending queue and spawn watcher. |
| Token expired during trigger loop | Refresh token. Continue from where you left off. |

---
title: Plaud Speaker Renaming Sync Fix
date: 2026-06-10
category: Plaud Integration
status: Implemented
---

# Plaud Speaker Renaming Sync Fix

## The Problem

When speakers were renamed in Plaud transcripts (e.g., "Speaker 1" → "David O'Hara"), the names were being updated in Plaud's internal database but **not appearing in the final Obsidian notes**. The workflow was broken at the sync boundary between the Plaud API and the downloaded markdown files.

### Root Cause: Two Separate Data Stores

Plaud has two separate storage layers for transcript data:

1. **File Record** (`trans_result`) — The raw transcript segments stored in Plaud's database
   - Accessible via `GET /file/detail/{file_id}` → `trans_result` field
   - Updated by `PATCH /file/{file_id}` with modified segments

2. **S3-Stored Transcript** — Pre-generated markdown files stored on AWS S3
   - Referenced by presigned URL in `content_list[data_type='transaction'].data_link`
   - Downloaded by `extract_transcript()` function
   - Generated once during initial transcription, **not auto-updated** when segments change

### The Workflow Bug

The `rename_and_refetch` function was doing:

```
1. PATCH /file/{file_id} with {"trans_result": trans_result}  ← Updates database
2. Re-fetch transcript from S3 URL                             ← Gets OLD transcript
3. Save to vault with original speaker names                  ← Names never changed
```

The PATCH succeeded and names were in the database, but the S3 object was unchanged, so the downloaded markdown still had generic labels like "Speaker 1".

## The Solution

Added three-step verification and regeneration:

### 1. Verification: Check if Names Sync

After renaming and re-fetching, check if new speaker names actually appear in the downloaded transcript:

```python
def check_speaker_names_in_transcript(transcript_text, mapping):
    """Verify that new speaker names appear in the transcript markdown."""
    missing = []
    for old_name, new_name in mapping.items():
        if new_name.lower() not in transcript_text.lower():
            missing.append(new_name)
    return len(missing) == 0, missing
```

### 2. Regeneration: Trigger Output Update

If names are missing from the transcript, trigger Plaud to regenerate the S3 output:

```python
def trigger_transcript_regeneration(token, file_id):
    """Trigger regeneration of transcript output files after speaker changes.
    
    Uses POST /ai/transsumm with is_reload: 1 to regenerate without re-transcribing.
    """
    resp = requests.post(
        f"{api_base}/ai/transsumm/{file_id}",
        json={
            "is_reload": 1,  # Regenerate outputs, don't re-transcribe
            ...
        },
        timeout=120,
    )
```

The key is `is_reload: 1`, which signals Plaud to regenerate output files (update the S3 transcript) rather than re-running the full transcription pipeline.

### 3. Retry: Verify Again

After regeneration, re-fetch and verify the names appear:

```python
if trigger_transcript_regeneration(token, file_id):
    time.sleep(2)  # Wait for processing
    detail = get_recording_detail(token, file_id)
    transcript_text = extract_transcript(detail)
    has_new_names, missing = check_speaker_names_in_transcript(transcript_text, mapping)
    if has_new_names and not missing:
        print("✓ Speaker names now in transcript")
    elif missing:
        print(f"⚠ Still missing: {missing}")
```

## How It Works Now

```
rename_and_refetch() flow:

1. Get transcript segments (trans_result) from Plaud
2. Extract voice embeddings
3. Apply renames via PATCH /file/{file_id}
4. Register speakers for auto-labeling
5. Re-fetch detail and extract transcript from S3
6. CHECK: Are new names in the downloaded transcript?
   ├─ YES: ✓ Proceed to save (names already synced)
   └─ NO:  Trigger regeneration
           ├─ POST /ai/transsumm with is_reload: 1
           ├─ Wait 2 seconds for Plaud
           ├─ Re-fetch and re-extract
           ├─ CHECK again:
           │  ├─ YES: ✓ Proceed to save
           │  └─ NO:  ⚠ Warn (rare case, may need retry)
           └─ Save to vault
```

## Changes Made

### Scripts
- `skills/plaud-transcripts/scripts/fetch_plaud.py`
  - Added `check_speaker_names_in_transcript()`
  - Added `trigger_transcript_regeneration()`
  - Updated `rename_and_refetch()` with verification loop

### Workflows
- `workflows/plaud-ingest/steps/step-04-fetch-staging.md`
  - Updated rules to document regeneration
  - Updated success metrics to include name verification
  - Added failure modes for regeneration edge cases
  - Reset step status to `not-started` to reflect fix

## Testing

To verify the fix:

1. Run a Plaud recording through the workflow
2. Provide speaker mappings in step-03
3. Observe step-04 output:
   - Should see "Speaker names verified in transcript" if names sync immediately
   - OR see "REGENERATION NEEDED" message, followed by regeneration and re-fetch
   - OR see "✓ Speaker names now in transcript" after regeneration
4. Check the final vault note — speaker names should appear, not "Speaker 1", "Speaker 2"

## Edge Cases & Fallbacks

| Scenario | Behavior |
|----------|----------|
| Names sync immediately (rare) | ✓ Saves immediately, no regeneration needed |
| Regeneration trigger fails | ⚠ Script warns, proceeds with current transcript (may have old names) |
| Names still missing after 2nd fetch | ⚠ Script warns with instructions to check Plaud app and retry manually |
| S3 URL changes during regeneration | ✓ New URL is fetched and used automatically |
| Timeout on regeneration call | ⚠ Script continues with current transcript, user can re-run rename if needed |

## References

- **Plaud API**: `/ai/transsumm` endpoint with `is_reload` parameter
- **Original Issue**: Speaker names not appearing in vault notes despite being renamed in Plaud
- **Root Cause Discovery**: 2026-06-10 workflow analysis
- **Related Files**:
  - `workflows/plaud-ingest/workflow.md` (overall pipeline)
  - `workflows/plaud-ingest/steps/step-03-identify-speakers.md` (speaker mapping input)
  - `skills/plaud-transcripts/SKILL.md` (main skill docs)

---

**Status**: Implemented and tested
**Impact**: Speaker names now sync to final vault notes
**Rollback**: Can revert changes to `fetch_plaud.py` if issues arise

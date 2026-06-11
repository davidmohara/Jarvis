---
title: Plaud Speaker Renaming Sync Fix
date: 2026-06-10
category: Plaud Integration
status: Implemented
---

# Plaud Speaker Renaming Sync Fix

## The Problem

When speakers were renamed in Plaud transcripts (e.g., "Speaker 1" → "David O'Hara"), the names were being updated in Plaud's internal database but **not appearing in the final Obsidian notes**. The workflow was broken at the sync boundary between the Plaud API and the downloaded markdown files.

### Root Cause: Three Separate Data Stores

Plaud stores transcript data in three distinct layers. A speaker rename must propagate through all three to be complete.

1. **Database** (`trans_result` via `/file/list`) — Segment-level speaker labels in Plaud's database
   - Updated by `PATCH /file/{file_id}` with `{"trans_result": [...modified segments...]}`
   - Returns `null` transiently during active `is_reload` regeneration (not an error)

2. **S3 `transaction` layer** — Raw diarization segments stored on AWS S3
   - Referenced by presigned URL in `content_list[data_type='transaction'].data_link`
   - Updated by `is_reload: 1` regeneration, sourced from the DB `trans_result`
   - Presigned URLs expire after ~300 seconds — always fetch fresh `/file/detail`

3. **S3 `transaction_polish` layer** — Polished/formatted version stored on AWS S3
   - Referenced by presigned URL in `content_list[data_type='transaction_polish'].data_link`
   - **This is what the Plaud web UI renders**
   - Also updated by `is_reload: 1` regeneration
   - If you only PATCH without regenerating, the web UI still shows old labels

`content_list` also contains `outline` (topic segments, speaker always `?`) and
`auto_sum_note` (AI summary). The outline survives regeneration; the others are
transiently cleared during the rebuild window.

### The Workflow Bug

The original `rename_and_refetch` function was doing:

```
1. PATCH /file/{file_id} with {"trans_result": trans_result}  ← Updates DB only
2. Re-fetch transcript from S3 transaction layer               ← Gets updated raw segs
3. Save to vault — names look correct in transaction layer
4. Web UI still shows "Speaker 2"                             ← transaction_polish unchanged
```

The PATCH updated the DB and the `transaction` S3 layer propagated correctly, but
`transaction_polish` — the layer the web UI actually renders — was not regenerated.

A second bug: the original fix's verification checked the markdown text from
`extract_transcript()`, which read from `transaction` (which was already correct).
This gave false confidence that `transaction_polish` was also updated.

## The Solution

Three changes to `rename_and_refetch()`:

### 1. `extract_transcript()` now reads `transaction_polish` first

```python
# Prefer transaction_polish (web UI layer)
for item in content_list:
    if item.get("data_type") == "transaction_polish" and item.get("task_status") == 1:
        ...fetch and return segments...

# Fall back to raw transaction layer
for item in content_list:
    if item.get("data_type") == "transaction" and item.get("task_status") == 1:
        ...fetch and return segments...
```

### 2. Verification explicitly checks `transaction_polish` presence

After triggering `is_reload: 1`, regeneration temporarily clears `content_list`.
The retry loop now checks that `transaction_polish` has reappeared before verifying names:

```python
cl = (detail or {}).get("content_list", [])
types_present = [i.get("data_type") for i in cl]
if "transaction_polish" not in types_present:
    print("transaction_polish not yet in content_list — still regenerating")
    continue  # keep polling
```

### 3. Retry timing increased

Old: 12s × 4 attempts = 48s maximum wait.
New: 20s × 6 attempts = 120s maximum wait.

Observed regeneration time in production: 15-30s, but can be longer under load.

## How It Works Now

```
rename_and_refetch() flow:

1. Get trans_result from /file/list (DB layer)
2. Extract voice embeddings
3. Apply renames via PATCH /file/{file_id}  ← updates DB layer only
4. Register speakers for auto-labeling
5. Re-fetch detail, extract from transaction_polish (web UI layer)
6. CHECK: Are new names in transaction_polish?
   ├─ YES: ✓ Proceed to save
   └─ NO:  Trigger is_reload=1 regeneration
           ├─ POST /ai/transsumm with is_reload: 1
           ├─ Poll every 20s for transaction_polish to reappear
           │  (content_list is transiently cleared during rebuild)
           ├─ When transaction_polish is back, re-extract and CHECK again
           ├─ YES: ✓ Proceed to save
           └─ NO after 120s: ⚠ Warn, save with whatever is available
```

## Changes Made

### Scripts
- `skills/plaud-transcripts/scripts/fetch_plaud.py`
  - `extract_transcript()`: reads `transaction_polish` first, falls back to `transaction`
  - `rename_and_refetch()`: polls for `transaction_polish` presence, 20s×6 retry timing
  - `check_speaker_names_in_transcript()`: unchanged, still checks markdown text
  - `trigger_transcript_regeneration()`: unchanged

### Documentation
- `skills/plaud-transcripts/SKILL.md`: API docs section updated with three-layer model
- `systems/plaud-speaker-sync-fix.md` (this file): corrected root cause and solution

## Testing

1. Run `--rename` on a recording with generic speaker labels
2. Observe output:
   - "REGENERATION NEEDED: Speaker names not in transaction_polish layer"
   - "transaction_polish not yet in content_list — still regenerating" (during rebuild)
   - "✓ Speaker names now confirmed in transaction_polish" (after rebuild)
3. Verify in Plaud web UI — speakers should show real names, not "Speaker 1"

## Edge Cases & Fallbacks

| Scenario | Behavior |
|----------|----------|
| transaction_polish already has real names | ✓ Saves immediately, no regeneration needed |
| Regeneration trigger fails (HTTP error) | ⚠ Script warns, saves with transaction layer (may differ from web UI) |
| transaction_polish never reappears in 120s | ⚠ Warns, saves best available. Re-run --rename to retry. |
| S3 presigned URL expires during polling | ✓ Fresh /file/detail is fetched each poll attempt |
| trans_result returns null during regen | Expected — transient. Don't treat as data loss. |

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

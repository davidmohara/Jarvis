---
name: plaud-speaker-id
model: sonnet
description: >
  Identify generic speaker labels (Speaker 1, Speaker 2, etc.) in Plaud recordings
  by cross-referencing recording timestamps against calendar attendees. Auto-resolves
  when confidence is high; surfaces a consolidated question to the controller when it
  cannot. Use during the plaud-ingest workflow step-03, or standalone when a recording
  has unidentified speakers. Also triggered by "who is Speaker 1", "identify the
  speakers in this recording", or "I need to label the speakers".
---

# Plaud Speaker Identification

Resolve generic speaker labels in Plaud recordings to real names, using calendar
data as the primary signal and controller input as the fallback.

## How this works

The Plaud fetch script detects when a transcript contains generic speaker labels
("Speaker 1", "Speaker 2", etc.) and writes a `_speakers.json` file to staging
alongside the transcript markdown. This skill reads those files, attempts to match
speakers to calendar attendees automatically, and surfaces any that can't be
auto-resolved to the controller as a single consolidated prompt.

## Prerequisites

- `_speakers.json` file(s) in `~/Downloads/transcript-staging/`
- M365 calendar access (via MCP) for the recording's date
- (Optional) Clay contact data for additional name context

## Input: Speaker mapping file structure

```json
{
  "file_id": "abc123",
  "recording_name": "Meeting with Todd Wynne",
  "all_speakers": [
    {"name": "Speaker 1", "segments_count": 42, "sample_text": "I think we should look at the AI maturity..."},
    {"name": "Speaker 2", "segments_count": 31, "sample_text": "The timeline for the POC is..."}
  ],
  "untagged_speakers": ["Speaker 1", "Speaker 2"],
  "known_speakers": [
    {"speaker_id": "...", "speaker_name": "David O'Hara", "speaker_type": 1, ...}
  ],
  "status": "needs_mapping"
}
```

## Execution

### 1. Load all `_speakers.json` files from staging

Enumerate `~/Downloads/transcript-staging/plaud_*_speakers.json`. Load each.
Group by recording (one JSON file per recording that has generic speakers).

### 2. For each recording: attempt calendar auto-resolution

**a. Extract recording time window**

The recording's date is in the `_speakers.json` metadata. Use it to query:
```
mcp__claude_ai_Microsoft_365__outlook_calendar_search(
  query="",
  start: "<recording-date>T00:00:00",
  end: "<recording-date>T23:59:59"
)
```

Find calendar events that overlap the recording's time (compare by start/end if
available in the recording metadata, or search by recording date and title similarity).

**b. Get attendee list from matching calendar event**

From the matched event, extract all attendee display names.
Remove David O'Hara from the attendee list — he is always present, his voice is
registered as `speaker_type: 1` in the known_speakers list.

**c. Auto-resolve using heuristics (apply in order)**

1. **Known speakers match**: If a speaker in `known_speakers` (already registered in Plaud)
   maps to a generic label via the recording's `embeddingKey`, use that name directly.

2. **David is the owner**: David (`speaker_type: 1`) is always the highest-segment-count
   speaker in internal meetings. In external meetings (David as the only Improving person),
   David is still typically highest segment count. Assign David to highest `segments_count`.

3. **Single external attendee**: If calendar shows exactly 2 attendees (David + one other),
   and transcript has 2 speakers, the assignment is unambiguous regardless of segment counts.

4. **Sample text name drops**: Scan `sample_text` for name mentions. If Speaker 1's sample
   says "...as Todd mentioned..." then Speaker 1 is likely David talking about Todd, not Todd.

5. **Recording title contains attendee name**: If the recording is named "Meeting with
   Sarah Chen" and there is a Sarah Chen in the attendee list, she is the non-David speaker.

6. **Clay lookup**: If attendee names from calendar are ambiguous, look them up in Clay
   for role/company context that might disambiguate ("VP of Sales" vs "Principal Consultant").

**d. Confidence threshold**

Mark a resolution as auto-confirmed if:
- It satisfies heuristic 1, 2, or 3 (deterministic)
- OR it satisfies heuristics 4 or 5 with calendar confirmation (attendee in list)

Mark as needing controller input if:
- 3+ unresolved speakers remain after all heuristics
- Calendar had no matching event
- Attendee count doesn't match speaker count
- Heuristics produce conflicting signals

### 3. Compile unresolved speakers for controller prompt

If any recordings have unresolved speakers, build a single consolidated message.
All recordings in one message — never send multiple separate prompts.

**Message format:**
```
I need your help identifying speakers in [N] recording(s) before I can finish ingesting them.

---

**"[Recording Name]"** — [Date, HH:MM]
Calendar attendees: [Name], [Name]

  Speaker 1 ([N] segments): "[sample text]"
  Speaker 2 ([N] segments): "[sample text]"

Who is Speaker 1 and Speaker 2?
*(e.g., "Speaker 1 = David, Speaker 2 = Todd")*

---

**"[Another Recording]"** — [Date, HH:MM]
...
```

Update `state.yaml status: awaiting-input` before surfacing the prompt.
Do not surface auto-resolved recordings in this prompt — only the unresolved ones.

### 4. Parse controller response

When the controller responds, parse the speaker assignments. Accept flexible formats:
- `"Speaker 1 = David, Speaker 2 = Todd"`
- `"1 is me, 2 is Todd"`
- `"top one is David, second is Todd Wynne"`

Normalize to: `{"Speaker 1": "David O'Hara", "Speaker 2": "Todd Wynne"}`

Merge with auto-resolved mappings. Update `state.yaml`:
- `accumulated-context.speaker-mappings` = full resolved set
- `accumulated-context.pending-speaker-mappings: []`
- `status: in-progress`

### 5. Return final mappings

```yaml
speaker_mappings:
  abc123:
    Speaker 1: "David O'Hara"
    Speaker 2: "Todd Wynne"
  def456:
    Speaker 1: "David O'Hara"
    Speaker 2: "Sarah Chen"

resolution_method:
  abc123: auto (calendar + segment count)
  def456: controller-confirmed
```

## Standalone invocation

This skill can be invoked directly (outside the plaud-ingest workflow) when the
controller asks about speaker identification for a specific recording. In that case:
1. Load the relevant `_speakers.json` from staging (or reconstruct from the staged markdown)
2. Run steps 2-5 above
3. Apply the mappings via `fetch_plaud.py --rename` immediately (no workflow state to update)

## Error handling

| Error | Action |
|-------|--------|
| Calendar unavailable | Skip auto-resolution for all. Put all recordings in `pending-speaker-mappings`. |
| No `_speakers.json` found | No generic speakers in this recording — mark all speakers as resolved. |
| Controller response is ambiguous | Ask for clarification on only the ambiguous recording, not the whole set. |
| More speakers in transcript than attendees | Include all unknown speakers in the prompt with a note: "There are more speakers than calendar attendees — this may have been a group call." |

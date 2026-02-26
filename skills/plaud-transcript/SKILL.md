---
name: plaud-transcript
description: Extract meeting transcripts and AI summaries from Plaud AI (web.plaud.ai) and save them as formatted markdown to the Obsidian zzPlaud folder. Extracts action items and routes them to OmniFocus. Use this skill whenever the user mentions Plaud, meeting transcripts, or recording exports. Also trigger proactively during /boot — check Chrome for a Plaud tab and the Plaud API for any new recordings not yet in zzPlaud. This is a core operational workflow — new transcripts should be extracted, converted, and filed automatically without being asked.
evolution: personal
---

# Plaud Transcript Extraction

Extract meeting transcripts and AI-generated summaries from Plaud AI's web interface. Save as clean, timestamped markdown to the Obsidian vault. Route action items to OmniFocus.

## When to Run

- **During `/boot`**: Always. Open a Chrome tab to `web.plaud.ai`, hit the file list API, and compare against existing files in `zzPlaud/`. Process any new recordings automatically.
- **On demand**: When the user mentions a new recording or asks to process transcripts
- **Proactively**: When detecting unprocessed Plaud recordings during any session

## Architecture

Plaud is a meeting recording device. Transcripts live in their web app at `web.plaud.ai`. The web app is a Vue SPA with a virtual scroller — you cannot scrape the DOM for full transcripts.

**Key design principle:** Chrome is only used for auth token capture (a small, reliable operation). ALL data transfer happens via `curl` on the command line — no Chrome JS execution for API calls, no DOM bridges, no chunked AppleScript string transfers.

### Data Flow

```
Chrome (auth only) → token → curl (all API calls) → filesystem → markdown assembly
```

## API Reference

### Authentication
The JWT bearer token is stored in Chrome's localStorage:
```javascript
localStorage.getItem('tokenstr')
// Returns: "bearer eyJhbG..."
```

Capture it once via osascript (small string, reliable), then use it in all subsequent `curl` calls.

### Endpoints

**File List** — Get all recordings:
```
GET https://api.plaud.ai/file/simple/web?skip=0&limit=99999&is_trash=2&sort_by=start_time&is_desc=true
Authorization: {token}
```
Response shape:
```json
{
  "data_file_list": [
    {
      "id": "file_id_hex",
      "filename": "02-24 Meeting: Title Here",
      "duration": 2301000,
      "start_time": 1771945911000,
      "is_trans": true,
      "is_summary": true
    }
  ]
}
```

**File Detail** — Get signed S3 URLs for a recording's assets:
```
GET https://api.plaud.ai/file/detail/{file_id}
Authorization: {token}
```
Response includes `content_list` array. Each item has:
- `data_type`: One of the types below
- `data_link`: Signed S3 URL (expires in ~300 seconds)

### Content Types in `content_list`

| data_type | Contains | Use |
|-----------|----------|-----|
| `transaction` | Full transcript JSON array | Primary transcript — speaker-labeled utterances with timestamps |
| `outline` | Topic outline JSON array | Section headers with start/end times — used for topic structure |
| `auto_sum_note` | AI meeting summary JSON | Structured meeting notes with topics, conclusions — goes into Summary section |
| `sum_multi_note` (first) | Action items + key decisions JSON | **Critical** — action items with @mentions, key decisions with rationale |
| `sum_multi_note` (second) | Meeting highlights JSON | Strategic highlights, categorized themes — goes into AI Highlights section |
| `high_light` | Key insights + action items | Hardware-generated highlights with expanded context |
| `mark_memo` | User-marked moments | Bookmarks created during recording |

### Data Formats

**Transcript** (`transaction`):
```json
[
  {
    "content": "The spoken text here.",
    "start_time": 960,
    "end_time": 22620,
    "speaker": "O'Hara",
    "original_speaker": "Speaker 1",
    "embeddingKey": "uuid-or-null"
  }
]
```
Times are in milliseconds from recording start.

**Summary** (`auto_sum_note`): JSON with `ai_content` field containing markdown-formatted meeting notes with topic headers, bullet points, and conclusions.

**Action Items** (`sum_multi_note` first instance): JSON with `ai_content` field containing:
- `## Action Items` — with `@[Name]` mentions and descriptions
- `## Key Decisions` — with rationale
- `## Detailed Minutes` — timestamped narrative

**Meeting Highlights** (`sum_multi_note` second instance): JSON with `ai_content` field containing categorized strategic highlights with bullet points. The `category` field will say `"Meeting Highlights"`.

## Extraction Workflow

### Step 1: Open Plaud and Capture Auth Token

During `/boot`, open a Chrome tab to `web.plaud.ai` so the auth session is active:
```applescript
tell application "Google Chrome"
    tell front window
        set newTab to make new tab with properties {URL:"https://web.plaud.ai"}
    end tell
end tell
```

Wait 5 seconds for page load and auth initialization, then capture the token (one small osascript read — reliable):
```bash
TOKEN=$(osascript -e 'tell application "Google Chrome"
    execute active tab of front window javascript "localStorage.getItem(\"tokenstr\")"
end tell')
```

The token is a small string (`"bearer eyJhbG..."`). This is the ONLY osascript-to-Chrome interaction needed. Everything else uses `curl`.

### Step 2: Detect New Recordings via curl

Fetch the file list directly via `curl` (no Chrome JS execution):
```bash
curl -s -H "Authorization: $TOKEN" \
  "https://api.plaud.ai/file/simple/web?skip=0&limit=99999&is_trash=2&sort_by=start_time&is_desc=true" \
  -o /tmp/plaud_filelist.json
```

List existing files in zzPlaud:
```bash
ls '/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/zzPlaud/'
```

Compare by date prefix (YYYY-MM-DD) to identify unprocessed recordings. Parse the file list with python3:
```bash
python3 -c "
import json
data = json.load(open('/tmp/plaud_filelist.json'))
for f in data['data_file_list']:
    if f.get('is_trans'):
        from datetime import datetime
        dt = datetime.fromtimestamp(f['start_time']/1000).strftime('%Y-%m-%d')
        print(f'{dt}|{f[\"id\"]}|{f[\"filename\"]}|{f[\"duration\"]}')
"
```

### Step 3: Fetch Content for Each New Recording via curl

For each unprocessed recording, fetch the file detail:
```bash
curl -s -H "Authorization: $TOKEN" \
  "https://api.plaud.ai/file/detail/$FILE_ID" \
  -o /tmp/plaud_detail.json
```

Parse `content_list` to get S3 signed URLs, then fetch each content type directly to filesystem:

```bash
# Transcript (can be 40-60K+ — curl handles any size natively)
curl -s "$TRANSCRIPT_S3_URL" -o /tmp/plaud_transcript.json

# Summary
curl -s "$SUMMARY_S3_URL" -o /tmp/plaud_summary.json

# Action items (first sum_multi_note)
curl -s "$ACTIONS_S3_URL" -o /tmp/plaud_actions.json

# Highlights (second sum_multi_note, category: "Meeting Highlights")
curl -s "$HIGHLIGHTS_S3_URL" -o /tmp/plaud_highlights.json
```

Validate all JSON files:
```bash
python3 -c "import json; data=json.load(open('/tmp/plaud_transcript.json')); print('Transcript valid, entries:', len(data))"
python3 -c "import json; data=json.load(open('/tmp/plaud_summary.json')); print('Summary valid')"
```

**Why this is better**: curl writes directly to filesystem — no DOM bridges, no chunked AppleScript string transfers, no blind delays for async operations. A 60K transcript that previously required 6+ chunked osascript round-trips now downloads in one call.

**S3 URL expiration**: Signed URLs expire in ~300 seconds. Fetch all content promptly after getting the file detail response.

### Step 4: Build the complete markdown document

The output file has four sections above the transcript:

1. **Header**: Title, date, duration, source, participants
2. **Summary**: Extracted from `auto_sum_note` — clean up the `ai_content` markdown. Remove Plaud boilerplate (`## Meeting Information`, `> Date:`, `> Location:`, `> Participants:` block) since we have our own header. Keep the `## Meeting Notes` content.
3. **Action Items**: Extracted from the first `sum_multi_note`. Parse the `## Action Items` and `## Key Decisions` sections.
4. **AI Highlights**: Extracted from the second `sum_multi_note` (Meeting Highlights). Reformat the categorized bullets.
5. **Transcript**: Full speaker-labeled, timestamped transcript

### Step 5: Route Action Items

After saving the markdown file, parse the action items section and route David's items:

**For items assigned to O'Hara / David:**
- Create OmniFocus tasks via osascript:
```applescript
tell application "OmniFocus"
    tell default document
        set newTask to make new inbox task with properties {name:"[Meeting Title] Action item description", note:"From Plaud transcript YYYY-MM-DD"}
    end tell
end tell
```

**For items assigned to others:**
- Flag them in the briefing output so David can delegate or follow up
- Format: "Action items for others from [Meeting]: @Name — description"

### Step 6: Save to Obsidian

Write the markdown file to:
```
/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/zzPlaud/
```

Naming convention: `YYYY-MM-DD <Short Meeting Title>.md`

Examples:
- `2026-02-23 FUB AI Training Program.md`
- `2026-02-24 DRC Event Strategy.md`
- `2026-02-20 Vistage Speaker Opportunity.md`

### Step 7: Clean up

Remove temporary JSON files from `/tmp/`.

## Output Format

```markdown
# MM-DD Meeting: Full Title

**Date**: YYYY-MM-DD
**Duration**: XXm XXs
**Source**: Plaud AI Recording
**Participants**: Speaker 1, Speaker 2, Speaker 3

---

## Summary

[Cleaned AI meeting summary — topic notes with conclusions]

## Action Items

- **@Name**: Action description
- **@Name**: Action description

## Key Decisions

- Decision description — Rationale: reasoning
- Decision description — Rationale: reasoning

## AI Highlights

- **Category**: Bullet point insight
- **Category**: Bullet point insight

---

**Speaker Name** [MM:SS]:
Transcribed text here. Consecutive utterances from the same speaker are merged.

**Other Speaker** [MM:SS]:
Their response text here.
```

## Assigned Agent

**Chief** owns this workflow as part of daily operations. During morning boot, Chief checks for new Plaud recordings and processes them automatically. After extraction:
- O'Hara's action items → OmniFocus inbox
- Others' action items → flagged in briefing for delegation
- Content-rich transcripts → flagged for **Harper** (talking points, follow-up drafts)
- Client meeting transcripts → flagged for **Chase** (deal context, account intelligence)

## Dependencies

- Google Chrome must be open with Plaud Web logged in (for auth token only)
- osascript access (Mac host) — used only for Chrome tab open + token read
- `curl` on the Mac host — all API calls and data transfer
- Python 3 on the Mac host — JSON parsing and validation
- Write access to the Obsidian vault iCloud directory
- OmniFocus for action item routing

## What Changed (v2 — Playwright/curl rewrite)

Previous approach used Chrome's JS context for ALL API calls, requiring:
- A hidden DOM element (`div#jarvis-data`) as a data bridge
- Chunked 10K AppleScript string transfers for large transcripts
- Blind `delay N` calls for async operation timing
- Multiple osascript round-trips per recording

New approach uses Chrome for ONE thing (auth token capture) and `curl` for everything else:
- Direct HTTP calls — no DOM bridges
- Full-size downloads — no chunking
- Synchronous operations — no blind delays
- One osascript call total — not dozens

**Future**: When Playwright MCP is configured with Chrome profile access and JS execution capability, the osascript token capture can be replaced with Playwright's `browser_evaluate`. The curl-based data extraction stays the same regardless.

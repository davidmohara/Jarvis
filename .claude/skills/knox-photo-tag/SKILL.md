---
name: knox-photo-tag
description: "Tag photos with person, place, and event keywords. Use when the user says 'tag my photos', 'photo tagging', 'label my photos', 'photo pipeline', or any request to organize/tag photos from Apple Photos with people, places, and events."
model: haiku
---

<!-- system:start -->
# Photo Tagging Pipeline

Analyze photos from Apple Photos, identify people/places/events, and write keyword tags back via macOS Shortcuts. Designed for batch processing with resumable state.

## Dispatch: Run as Sub-Agent

**Do NOT run this skill inline.** When triggered, dispatch the workflow to a general-purpose sub-agent using the Agent tool. This keeps the heavy vision calls and batch processing out of the main conversation context.

```
Agent(
  subagent_type: "general-purpose",
  description: "Tag photos — batch analysis",
  prompt: "<paste the relevant phase workflow>"
)
```

The sub-agent writes progress to `data/photo-pipeline/manifest.json` and a final report to `data/photo-pipeline/photo_tag_report.md`. When it returns, read the report and give the controller a summary.

---

## Architecture

```
Skill:     .claude/skills/knox-photo-tag/SKILL.md
Data dir:  data/photo-pipeline/  (gitignored)
State:     data/photo-pipeline/manifest.json (resumable across sessions)
Output:    Keywords written to Photos.app via Shortcuts + summary report
```

## Key Constraint

Apple Photos AppleScript is read-heavy but **cannot write keywords**. All tag write-back goes through the macOS Shortcut "Tag Photo".

---

## Prerequisites (One-Time Setup)

### macOS Shortcut: "Tag Photo"

The controller must create this Shortcut manually in Shortcuts.app:

1. **Input**: Receives text in format `UUID|keyword1,keyword2,...`
2. **Actions**:
   - Split Text by `|` → get Item 1 (UUID) and Item 2 (keywords)
   - Split Item 2 by `,` → keyword list
   - Find Photos Where Media Unique Identifier is Item 1
   - Set Keywords of Photos to keyword list
3. **Test**: `shortcuts run "Tag Photo" --input-type text --input "test-uuid|test-tag"`

**Fallback**: If Shortcuts can't write keywords, create Albums per tag category instead (e.g., "person:Sarah", "place:Dallas TX", "event:YPO Forum").

---

## Phase 1: Validate Shortcut (5 min)

Before anything else, confirm the Shortcut works:

```bash
# Get a test photo UUID via AppleScript
osascript -e 'tell application "Photos" to get id of media item 1 of every media item whose date is greater than (current date) - 30 * days'
```

```bash
# Test write-back
shortcuts run "Tag Photo" --input-type text --input "UUID_HERE|pipeline-test"
```

Then verify in Photos.app that the keyword "pipeline-test" appears on the photo. If it doesn't work, stop and report — the whole pipeline depends on this.

---

## Phase 2: Calendar Pull (via M365 MCP)

Calendar data provides event tags. Pull 12 months of Outlook calendar events directly via M365 MCP (`mcp__claude_ai_Microsoft_365__outlook_calendar_search`).

**Structure** of `calendar-events.json`:
```json
[
  {
    "date": "2025-06-15",
    "start": "09:00",
    "end": "10:00",
    "title": "YPO Forum",
    "location": "The Ritz-Carlton, Dallas",
    "attendees": ["John Smith", "Jane Doe"]
  }
]
```

**Matching logic** (used in Phase 5):
- Photo timestamp falls within event window (±30 min buffer)
- Same-day fallback: pick longest or most-attended event
- No match: leave event tag empty (flagged in review queue)

---

## Phase 3: Known Faces Reference (Semi-Manual)

The controller picks 2-3 clear photos per key person (~20 people: family, direct reports, key contacts).

### Building the reference set:

1. Controller identifies reference photos (by album, name, or visual selection)
2. Export reference photos as thumbnails to `/tmp/photo-pipeline/faces/`
3. For each person, use Claude vision to build a text description:
   - Hair color/style, glasses, facial hair, build, distinguishing features
   - Context clues (often seen with specific people, common settings)

4. Save to `known-faces.json`:

```json
{
  "people": [
    {
      "name": "Jane Smith",
      "relationship": "colleague",
      "descriptions": [
        "Description from reference photo 1...",
        "Description from reference photo 2..."
      ],
      "clay_id": "clay_abc123",
      "confidence_notes": "High confidence — many clear reference photos"
    }
  ]
}
```

### During analysis (Phase 5):
- Claude compares each photo against all known-face descriptions
- Match confidence: **high** (clearly matches), **medium** (likely match), **low** (possible)
- Low-confidence matches go to the review queue
- Unknown faces get tagged `person:Unknown` and added to review queue

---

## Phase 4: Manifest Build (Automated)

### POC Scope
Pick the most recent full month to validate end-to-end before scaling.

### AppleScript enumeration

```applescript
tell application "Photos"
  set startDate to date "February 1, 2026 12:00:00 AM"
  set endDate to date "February 28, 2026 11:59:59 PM"
  set targetPhotos to every media item whose date >= startDate and date <= endDate

  repeat with p in targetPhotos
    set photoId to id of p
    set photoDate to date of p
    set photoLat to latitude of p
    set photoLon to longitude of p
    set photoKeywords to keywords of p
    set photoWidth to width of p
    set photoHeight to height of p
    log photoId & "|" & (photoDate as string) & "|" & photoLat & "|" & photoLon & "|" & photoWidth & "|" & photoHeight
  end repeat
end tell
```

**Important**: Run via `osascript` from Bash. If AppleScript is too slow (>5 min for enumeration), fall back to querying the Photos SQLite database directly:

```bash
sqlite3 ~/Pictures/Photos\ Library.photoslibrary/database/Photos.sqlite \
  "SELECT ZUUID, ZDATECREATED, ZLATITUDE, ZLONGITUDE FROM ZASSET WHERE ZDATECREATED BETWEEN ... LIMIT 100"
```

### Manifest structure (`manifest.json`):

```json
{
  "version": 1,
  "scope": "poc",
  "date_range": {"start": "2026-02-01", "end": "2026-02-28"},
  "created": "2026-03-07T10:00:00Z",
  "updated": "2026-03-07T10:00:00Z",
  "stats": {
    "total": 450,
    "analyzed": 0,
    "tagged": 0,
    "errors": 0
  },
  "batches": [
    {
      "id": "batch-001",
      "status": "pending",
      "photos": [
        {
          "uuid": "ABC123",
          "date": "2026-02-01T14:30:00Z",
          "lat": 32.7767,
          "lon": -96.7970,
          "existing_keywords": [],
          "width": 4032,
          "height": 3024,
          "status": "pending",
          "tags": {
            "people": [],
            "place": null,
            "event": null,
            "scene": null
          },
          "confidence": {},
          "review": false
        }
      ]
    }
  ]
}
```

- Batch size: 100 photos per batch
- After POC validates: expand `date_range` to full 12 months and rebuild

---

## Phase 5: Batch Analysis (Long Pole)

For each batch of 100 photos:

### 5a. Export thumbnails

```applescript
tell application "Photos"
  set targetPhoto to media item id "UUID_HERE"
  export {targetPhoto} to POSIX file "/tmp/photo-pipeline/batch-001/" with using originals false
end tell
```

Export at reduced resolution (~1024px longest edge) to keep vision fast. If AppleScript export is slow, use `sips` to resize after export:

```bash
sips --resampleHeightWidthMax 1024 /tmp/photo-pipeline/batch-001/*.jpg
```

### 5b. Vision analysis

For each photo, use Claude's vision to identify:

- **People**: Match against known-faces descriptions. Report name + confidence level.
- **Scene type**: meeting, conference, dinner, outdoor, family, travel, office, stage/presentation, group photo, selfie, etc.
- **Text in image**: any visible signs, banners, name badges, or event branding

Read each photo:
```
Read /tmp/photo-pipeline/batch-001/photo_001.jpg
```

Prompt pattern for vision:
```
Look at this photo and identify:
1. People present — compare against these known face descriptions: [insert from known-faces.json]
2. Scene type (meeting, dinner, conference, outdoor, family, etc.)
3. Any visible text (signs, banners, name badges, event branding)
Report as structured JSON.
```

### 5c. Geocode (lat/lon → place name)

Use Nominatim reverse geocoding (free, no API key):

```bash
curl -s "https://nominatim.openstreetmap.org/reverse?lat=32.7767&lon=-96.7970&format=json" \
  -H "User-Agent: IES-PhotoPipeline/1.0"
```

**Rate limit**: 1 request per second. **Cache aggressively** — most photos cluster at ~20 locations. Round coordinates to 3 decimal places for cache keys.

Save to `geocode-cache.json`:
```json
{
  "32.777,-96.797": "Dallas, TX",
  "30.267,-97.743": "Austin, TX"
}
```

Tag format: `place:Dallas TX`

### 5d. Calendar match

Look up photo timestamp in `calendar-events.json`:
- Find events where photo time is within event start/end (±30 min buffer)
- If multiple matches, prefer the one with the closest time overlap
- Same-day fallback: pick the longest or most-attended event
- Tag format: `event:YPO Forum`

### 5e. Update manifest

After each batch completes:
1. Update each photo's `tags`, `confidence`, and `status` in the manifest
2. Update batch `status` to `analyzed`
3. Write manifest to disk (resume point)
4. Keep a `.bak` copy: `cp manifest.json manifest.json.bak`
5. Clean up batch thumbnails: `rm -rf /tmp/photo-pipeline/batch-NNN/`

---

## Phase 6: Write Tags (Automated)

For each analyzed photo with status `analyzed`:

### Build keyword string

Combine all tags into a flat keyword list:
- People: `person:Sarah O'Hara`, `person:John Smith`
- Place: `place:Dallas TX`
- Event: `event:YPO Forum`
- Scene: `scene:dinner`

### Write via Shortcut

```bash
shortcuts run "Tag Photo" --input-type text --input "UUID|person:Sarah O'Hara,place:Dallas TX,event:YPO Forum,scene:dinner"
```

### Error handling
- If Shortcut fails, add to retry queue
- After all photos attempted, retry failed ones once
- Still failing → log in manifest as `error` status with error message

### Update manifest
- Set photo status to `written`
- Update `stats.tagged` counter

---

## Phase 7: Report

Generate `data/photo-pipeline/photo_tag_report.md`:

```markdown
## Photo Tagging Report — YYYY-MM-DD

**Scope**: Month Year (POC)
**Total photos**: N
**Tagged**: N | **Errors**: N | **Review queue**: N

### People Frequency

| Person | Count |
|--------|-------|

### Top Locations

| Place | Count |
|-------|-------|

### Events Matched

| Event | Photos | Date |
|-------|--------|------|

### Review Queue

| Photo UUID | Date | Issue |
|------------|------|-------|
```

---

## Execution Sequence (POC)

1. **Phase 1**: Test Shortcuts write-back (5 min, validates the whole approach)
2. **Phase 2 + 3 in parallel**: Calendar pull (M365 MCP) + Reference face set (controller picks photos)
3. **Phase 4**: Manifest build for POC month
4. **Phase 5**: Batch analysis (~30-60 min for one month)
5. **Phase 6**: Write tags
6. **Phase 7**: Generate report
7. **Review with controller** before scaling to full 12 months

## Scaling to Full Year

Once controller reviews POC results and confirms quality:
1. Expand `date_range` in manifest to 12 months
2. Rebuild manifest (Phase 4) — expect 3,000-10,000 photos
3. Re-run Phases 5-7 (3-7 hours, run overnight)

---

## Error Handling

| Error | Action |
|-------|--------|
| Shortcut fails to write keywords | Stop pipeline, report to controller. Test fallback (Albums). |
| AppleScript enumeration too slow | Switch to Photos.sqlite direct query |
| Vision misidentifies person | Confidence threshold — low confidence → review queue |
| Nominatim rate limit hit | Sleep 1s between requests, use cache aggressively |
| Manifest corruption | Restore from `.bak` file |
| Photo export fails | Skip photo, log error, continue batch |
| No GPS data on photo | Tag as `place:Unknown`, add to review queue |
| No calendar match | Leave event tag empty, not flagged unless photo is during business hours |

## What This Skill Does NOT Do

- It does not delete or modify photos in Apple Photos (only adds keywords)
- It does not upload photos anywhere — all processing is local
- It does not train or fine-tune any model — uses Claude's built-in vision
- It does not access iCloud Photo Library directly — works through Photos.app APIs
<!-- system:end -->

<!-- personal:start -->
## Paths

| What | Path |
|------|------|
| Data directory | `data/photo-pipeline/` |
| Manifest | `data/photo-pipeline/manifest.json` |
| Calendar cache | `data/photo-pipeline/calendar-events.json` |
| Known faces | `data/photo-pipeline/known-faces.json` |
| Geocode cache | `data/photo-pipeline/geocode-cache.json` |
| Batch thumbnails | `/tmp/photo-pipeline/batch-NNN/` |
| Final report | `data/photo-pipeline/photo_tag_report.md` |
| IES root | `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/` |

## Calendar Pull

Use `mcp__claude_ai_Microsoft_365__outlook_calendar_search` to pull all Outlook calendar events from the last 12 months. For each event capture: date (YYYY-MM-DD), start time (HH:MM), end time (HH:MM), title, location (if any), and attendees (names only). Format as JSON array and save to `data/photo-pipeline/calendar-events.json`.
<!-- personal:end -->

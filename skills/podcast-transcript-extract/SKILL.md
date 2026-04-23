---
name: podcast-transcript-extract
owning_agent: knox
model: haiku
trigger_keywords: [podcast, transcript, episode, save transcript, save podcast, youtube podcast, podcast episode]
trigger_agents: [knox, chief]
description: >
  Extract and save a full transcript from a public podcast episode to Obsidian. Supports
  YouTube (via Chrome transcript panel) and Apple Podcasts (via Chrome + episode webpage
  link). Trigger on "save this podcast", "get the transcript for this episode", "save this
  episode", or any request to capture a podcast episode URL to the vault. NOT for Plaud
  device recordings or Teams meeting transcripts — use plaud-transcripts or teams-transcripts
  for those.
---

<!-- system:start -->
# Podcast Transcript Extract

Extract the full transcript from a podcast episode and save it as a structured
Obsidian note with timestamps, key quotes, and summary sections.

## Supported Sources

| Source | Method |
|--------|--------|
| YouTube | Open in Chrome → click "Show transcript" → scrape panel |
| Apple Podcasts | Open in Chrome → find episode webpage link → follow to RSS/show site |
| RSS / Show website | Open in Chrome → scrape episode page |

## File Naming Convention

**All saved transcripts use this exact format:**

```
{YY-MM-DD} - {Podcast Name}.md
```

Examples:
- `26-04-23 - YPO Tech AI Brief - The Campfire Protocol.md`
- `26-03-15 - Lenny's Podcast - How to Build a Growth Team.md`

**Podcast Name** = Show name + Episode title, abbreviated naturally. No dates in the title
portion. Use the publish date from the episode metadata for `YY-MM-DD`.

**Vault location:** `Podcasts/`

---

## Execution

### Step 1: Get the URL into Chrome

If the URL is an Apple Podcasts link (`podcasts.apple.com`) or any URL that fails
to load via web fetch:

```
mcp__Control_Chrome__open_url(url=<url>, new_tab=true)
```

Never tell the user the domain is blocked. Always open in Chrome first.

### Step 2: Identify the source type

```javascript
document.URL
```

- Contains `youtube.com/watch` → **YouTube path** (Step 3a)
- Contains `podcasts.apple.com` → **Apple Podcasts path** (Step 3b)
- Other → try scraping directly (Step 3c)

---

### Step 3a: YouTube Transcript Extraction

YouTube renders transcripts in a side panel that must be explicitly triggered.

#### Open transcript panel

```javascript
// Expand description section first
var expandBtn = document.querySelector('tp-yt-paper-button#expand, ytd-text-inline-expander tp-yt-paper-button');
if (expandBtn) expandBtn.click();

// Find and click the Show Transcript button inside the description transcript section
var transcriptSection = document.querySelector('ytd-video-description-transcript-section-renderer');
if (transcriptSection) {
  var btn = transcriptSection.querySelector('button');
  if (btn) { btn.click(); 'clicked: ' + btn.textContent.trim(); }
  else { 'section found, no button yet'; }
} else {
  'section not found';
}
```

**Important:** Do NOT click at raw coordinates — this triggers playlist navigation instead
of the transcript. Always target the `ytd-video-description-transcript-section-renderer`
button specifically.

#### Read the transcript panel

The transcript loads in `[target-id="PAmodern_transcript_view"]`. Read in chunks to
avoid `missing value` from large string returns:

```javascript
var p = document.querySelector('[target-id="PAmodern_transcript_view"]');
p ? p.innerText.slice(0, 5000) : 'none';
```

```javascript
var p = document.querySelector('[target-id="PAmodern_transcript_view"]');
p ? p.innerText.slice(5000, 10000) : 'none';
```

Continue slicing in 5,000-character chunks until the slice returns an empty string or
repeats content. Typical 14-minute episode = ~15,000–18,000 characters.

#### Extract episode metadata from page

```javascript
var title = document.querySelector('h1.ytd-watch-metadata, yt-formatted-string.ytd-watch-metadata');
var channel = document.querySelector('#channel-name a, ytd-channel-name a');
var dateEl = document.querySelector('#info-strings yt-formatted-string, #info .ytd-video-primary-info-renderer');
JSON.stringify({
  title: title ? title.textContent.trim() : null,
  channel: channel ? channel.textContent.trim() : null,
  date: dateEl ? dateEl.textContent.trim() : null,
  url: document.URL
});
```

Also check video duration from the player:

```javascript
var video = document.querySelector('video');
video ? Math.floor(video.duration / 60) + 'm ' + Math.floor(video.duration % 60) + 's' : 'not found';
```

---

### Step 3b: Apple Podcasts Extraction

Apple Podcasts renders client-side. The page contains show notes but not a full transcript.

#### Get show notes from Apple Podcasts page

```javascript
document.body.innerText.substring(0, 5000);
```

This captures the episode description/show notes.

#### Find the Episode Webpage link

```javascript
var links = Array.from(document.querySelectorAll('a'));
var epLink = links.find(l => l.textContent.includes('Episode Webpage') || l.href.includes('episode'));
epLink ? epLink.href : 'not found';
```

If found, open the episode webpage in Chrome and try Step 3c. The episode page often
has a full transcript or richer show notes.

#### Get total duration from Apple Podcasts page

```javascript
// Duration is typically visible in page text near the episode header
document.body.innerText.match(/(\d+)\s*min/i);
```

---

### Step 3c: RSS / Show Website Extraction

```javascript
document.body.innerText.substring(0, 10000);
```

If the show notes contain a full transcript, extract it. If not, capture whatever
structured content is available (description, chapter markers, key quotes).

---

### Step 4: Build the Obsidian note

Structure the note as follows:

```markdown
# {Episode Title}

**Show**: {Podcast Name} (by {Host})
**Season/Episode**: S{N} E{N}
**Published**: {YYYY-MM-DD}
**Length**: {N} min
**Source URL(s)**: {url(s)}

---

## Summary

{2–4 sentence summary of the episode's thesis}

---

## Key Points

{Bulleted or structured breakdown of main content — frameworks, stats, arguments}

---

## Key Quotes

> "{quote}"

---

## Full Transcript

{Timestamped transcript with **[M:SS]** format}

---

#{tag1} #{tag2} #{tag3}
```

Tags: derive 2–4 from episode content. Use lowercase hyphenated format. Follow tag
taxonomy in `references/vault-conventions.md` where applicable.

---

### Step 5: Determine filename and save

1. Get publish date in `YY-MM-DD` format (e.g., `26-04-23`)
2. Build filename: `{YY-MM-DD} - {Show Name} - {Short Episode Title}.md`
3. Save to vault:

```
mcp__obsidian-local__create_vault_file(
  filename="Podcasts/{YY-MM-DD} - {Show Name} - {Short Episode Title}.md",
  content=<note content>
)
```

---

### Step 6: Verification ✓

After saving, run verification before reporting complete:

#### 6a: Confirm file was written

```
mcp__obsidian-local__get_vault_file(
  filename="Podcasts/{filename}.md"
)
```

Confirm file exists and content is non-empty.

#### 6b: Verify transcript duration matches podcast length

1. **Get stated episode length** from the source page (Apple Podcasts page text, YouTube
   player duration, or episode metadata). Convert to total seconds.

2. **Get last timestamp from saved transcript.** Read the saved file and extract the
   final timestamp (format `[M:SS]` or `M minutes, N seconds`).

3. **Compare:**
   - Convert last timestamp to seconds
   - Convert stated length to seconds
   - Calculate delta: `|stated_seconds - last_timestamp_seconds|`
   - **Pass**: delta ≤ 30 seconds
   - **Warn**: delta 31–120 seconds — note in report but don't fail
   - **Fail**: delta > 120 seconds — transcript is likely incomplete, report gap and
     attempt to re-extract missing portion

4. **Report verification result:**

```
✓ File saved: Podcasts/{filename}.md
✓ Duration check: stated {N}m {N}s | transcript ends at {M:SS} | delta {N}s — PASS
```

or:

```
✓ File saved: Podcasts/{filename}.md
⚠ Duration check: stated {N}m {N}s | transcript ends at {M:SS} | delta {N}s — WARNING
  Transcript may be missing ~{N}s from the end. Consider re-extracting.
```

or:

```
✓ File saved: Podcasts/{filename}.md
✗ Duration check: stated {N}m {N}s | transcript ends at {M:SS} | delta {N}s — FAIL
  Transcript appears incomplete. Re-extracting...
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| YouTube transcript panel won't open | Check if `ytd-video-description-transcript-section-renderer` exists — if not, video may not have captions. Report and fall back to description only. |
| `missing value` from JS execution | String operations on large innerText fail silently. Always use `.slice(start, end)` with explicit bounds. Never use `.length` or template literals on large strings in a single call. |
| Playlist auto-advances | Clicking at raw coordinates triggers playlist navigation. Always use DOM element targeting, never `document.elementFromPoint`. |
| Apple Podcasts no episode webpage link | Use show notes content only. Note in report that full transcript unavailable. |
| Transcript ends significantly before stated duration | Re-extract: re-open transcript panel, re-read from the timestamp where extraction stopped, append to saved note. |
| File already exists in vault | Append ` (2)` to filename. Do not overwrite without confirmation. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

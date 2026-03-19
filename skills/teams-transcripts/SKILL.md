---
name: teams-transcripts
description: >
  Pull meeting transcripts from Microsoft Teams and convert them into tagged Obsidian
  markdown notes filed into the user's vault. Use this skill whenever the user mentions
  Teams transcripts, Teams meeting notes, importing meetings from Teams, or wants to
  process yesterday's Teams calls into Obsidian. Also trigger on "get my Teams meetings",
  "pull yesterday's transcripts", "import meeting notes", "process my calls from Teams",
  or any variation where Teams meetings need to become vault notes. This handles the full
  pipeline: calendar search → transcript fetch → markdown transform → tag → file → report.
---

# Teams Transcripts → Obsidian

Fetch meeting transcripts from Microsoft Teams via the MS 365 MCP connector, transform
them into properly tagged Obsidian markdown notes, and file them into the vault.

## Why this skill exists

Meeting transcripts are high-value raw material that decays fast. A week after a call,
the insights are already fuzzy. This skill captures them the same day, summarizes them,
extracts action items, applies the vault's tag taxonomy, and routes them to the right
folder — so meetings become searchable, cross-referenced knowledge instead of forgotten
conversations.

## Prerequisites

- **Microsoft 365 MCP connector** — provides `outlook_calendar_search`, `read_resource`
  (for transcript URIs), and calendar event details
- **Write access to the Obsidian vault** — the vault lives at the path the user has
  selected as their working folder. Look for it in the mounted directories. The vault
  root typically contains folders like `Improving/`, `Personal/`, `_System/`, etc.

If the MS 365 connector isn't available, tell the user to connect it through their
MCP settings. Don't attempt browser-based workarounds — that's what the separate
Plaud skill handles.

## Execution

### 1. Figure out the date range

Default is yesterday. Verify user location and time zone with Chief agent. Convert to UTC for the API calls.

If the user says "last week" or "Monday's meetings" or a specific date, adjust
accordingly. When in doubt, confirm the date before fetching.

### 2. Search the calendar

Use `outlook_calendar_search` with:
- `query: "*"` (all events)
- `afterDateTime`: start of target date in ISO format
- `beforeDateTime`: end of target date in ISO format
- `limit: 50`

This returns all calendar events — Teams meetings, blocks, reminders, everything.

### 3. Attempt transcript retrieval for each meeting

For each event that has a Teams meeting link (visible in the location or body),
use `read_resource` with the event's calendar URI to get the full event details,
which includes a `meetingTranscriptUrl` field.

Then fetch the transcript using `read_resource` with that transcript URL.

**Expect most meetings to have no transcript.** Teams only records transcripts when
someone explicitly enables transcription or recording. External-org meetings often
block transcript access. When a transcript isn't available, create a skeleton note
instead — the metadata alone (who was there, when, what it was about) is still valuable.

### 4. Parse the transcript

Teams transcripts come back in WebVTT format:

```
WEBVTT

00:00:25.117 --> 00:00:28.117
<v Speaker Name>What they said</v>

00:01:02.557 --> 00:01:03.637
<v Another Speaker>Their response</v>
```

Parse this into speaker-labeled text. Group consecutive lines by the same speaker
into paragraphs. Preserve timestamps for reference but format them cleanly.

### 5. Transform into Obsidian notes

Read `references/vault-conventions.md` for the exact format. The key points:

**Filename:** `YYYY-MM-DD <Meeting Title>.md`
Clean the title — letters, numbers, spaces, hyphens only.

**Frontmatter tags (2-4 total):**
- `content/meeting` (always)
- `meta/timeline/YYYY/MM/DD` (always)
- 1-2 contextual tags based on content analysis (see tag routing table in references)

**Note structure:**
- Meeting Details (date, time in CST, platform, organizer)
- Attendees (names and emails from calendar event)
- Summary (2-4 sentences — synthesize, don't just describe)
- Key Discussion Points (### subheadings, prose, not bullets)
- Action Items (checkboxes with owners)
- Full Transcript (inside `<details>` collapse block)

**For meetings without transcripts:** still create the note, but use "No transcript
available — summary to be added manually." for the summary, leave Key Discussion Points
and Action Items as empty placeholders. The metadata and attendee list alone make
the note worth creating.

### 6. Route to the correct folder

| Meeting type | Folder |
|---|---|

Before writing, check if a file with the same name already exists. If so, ask the
user whether to overwrite or skip.

### 7. Link from the daily calendar note

Every meeting note gets a wikilink in the daily calendar note for that date. See
`references/vault-conventions.md` under "Daily Note Cross-Linking" for the full spec.

The short version:
1. Determine the daily note path: `Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md`
2. If the daily note doesn't exist, create it from the template (including the
   year and month folders if needed)
3. Find the `# Big meetings` heading in the daily note
4. Append `- [[<relative-path-to-meeting-note>]]` below it
5. Don't duplicate — check if the link already exists

The wikilink path is relative to vault root, without `.md` extension. For example:
`- [[Improving/Meeting Notes/2026-03-18 AI Leaders Weekly]]`

### 8. Report what happened

Present a clean summary:

```
Processed X meetings from YYYY-MM-DD:

✓ Meeting Title → Improving/Meeting Notes/YYYY-MM-DD Meeting Title.md (work/client)
✓ Another Meeting → Personal/YYYY-MM-DD Another Meeting.md (personal/development)
⊘ No Transcript Meeting (skeleton note created)

Tags applied: content/meeting, work/client, work/practice/ai-ml, meta/timeline/...
```

## Tag routing logic

The tag taxonomy is documented in `references/vault-conventions.md`. The short version:

Scan the meeting title, attendee list (especially external domains), and transcript
content for signals. Known client names get `work/client`. Strategy and planning get `work/strategy`.

When signals are ambiguous, default to the broader tag. When nothing specific matches,
`content/meeting` alone is fine — the user can refine later.

## Error handling

- MS 365 not connected → tell the user, link to MCP settings
- Transcript fetch fails for one meeting → log it, continue with the rest
- Vault folder doesn't exist → create it
- Ambiguous tags → default to `content/meeting` only
- Rate limiting on transcript fetches → add brief pauses between requests

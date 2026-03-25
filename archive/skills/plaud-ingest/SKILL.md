---
name: plaud-ingest
description: Ingest new Plaud meeting transcripts via MCP, format as markdown, save to Obsidian vault, and route action items to OmniFocus. Replaces the legacy Chrome-based plaud-transcript skill. Trigger on "plaud", "pull transcripts", "sync plaud", "process recordings", or automatically during /boot and /review-daily.
evolution: personal
---

# Plaud Ingest (MCP-Powered)

Ingest meeting transcripts from Plaud AI via the `plaud_*` MCP tools. Format as markdown, route to the correct Obsidian vault folder, and push action items into OmniFocus.

**This skill replaces the legacy `plaud-transcript` skill** which used Chrome automation and osascript. The MCP-powered version is faster, more reliable, works from Cowork (VM), and doesn't require Chrome to be open.

## Prerequisites

- Plaud MCP server registered and running (`plaud-mcp-ies`)
- Obsidian MCP server connected
- OmniFocus MCP or osascript available
- Plaud Private Cloud Sync enabled on David's device

## When to Run

- **During `/boot`**: Check for new recordings from the last 24 hours. Process automatically.
- **During `/review-daily`**: Check for any unprocessed recordings from today.
- **On demand**: When the user says "plaud", "pull transcripts", "sync plaud", or "new recordings".
- **After known meetings**: If a calendar event just ended and Plaud was likely recording, check proactively.

## Workflow

### Step 1: Check for New Recordings

```
plaud_get_recent(days=1)   # for /boot — last 24 hours
plaud_get_recent(days=7)   # for weekly review — last 7 days
plaud_list_recordings()    # for full sync
```

Compare returned recording IDs against what's already in the Obsidian vault.

To check existing vault files:
```
obsidian: search_vault_simple("path:zzPlaud/")
```

Match by date + title prefix to detect already-processed recordings. A recording is "new" if no vault file exists with a matching date and similar title.

### Step 2: Fetch Full Content

For each new recording:

```
plaud_get_recording_detail(recording_id)
```

This returns:
- `id` — recording ID
- `title` — recording filename/title
- `date` — ISO date string
- `duration_minutes` — length in minutes
- `transcript` — full speaker-diarized text
- `summary` — AI-generated summary (if available)
- `keywords` — extracted keywords

If the transcript is empty or missing (`has_transcript: false`), the recording hasn't been transcribed yet. Flag it for the user:
> "Recording '{title}' from {date} hasn't been transcribed yet. Open web.plaud.ai and click Generate on this recording, then re-run /plaud-ingest."

Do NOT silently skip untranscribed recordings — the user needs to know.

### Step 3: Apply Routing Rules

Load routing rules from `projects/plaud-mcp/plaud-mcp-ies/routing-rules.json`.

For each recording, test the title and transcript text against each rule's `match` pattern (case-insensitive regex). First match wins. If no match, use the `default` destination (`zzPlaud/`).

```
Rules:
  "Steve Hall|Bud Marrical" → Projects/Steve Hall/meetings/
  "AT&T|ATT" → Projects/AT&T/meetings/
  "podcast|Improving Edge" → Projects/Podcast/meetings/
  "1:1|one-on-one" → People/
  ... (see routing-rules.json for full list)

Default → zzPlaud/
```

### Step 4: Format as Markdown

Build the output file using this template:

```markdown
---
date: YYYY-MM-DD
source: plaud
recording_id: {id}
duration: {duration_minutes}m
participants: [{speaker names from transcript}]
tags: [{routing tag}, plaud, meeting]
---

# MM-DD Meeting: {Title}

**Date**: YYYY-MM-DD
**Duration**: {duration}m
**Source**: Plaud AI Recording
**Participants**: {comma-separated speaker names}

---

## Summary

{AI-generated summary from Plaud, cleaned up}
{If no summary available, generate a brief summary from the transcript}

## Action Items

{Parse action items from the summary or extract from transcript}
- **@{Assignee}**: {Action description}

## Key Decisions

{Extract from summary or transcript}
- {Decision} — Rationale: {reasoning if available}

---

## Transcript

**{Speaker Name}** [{MM:SS}]:
{Spoken text}

**{Other Speaker}** [{MM:SS}]:
{Spoken text}
```

**Formatting rules:**
- Merge consecutive utterances from the same speaker
- Convert millisecond timestamps to MM:SS format
- Strip Plaud boilerplate from summaries (Meeting Information blocks, date/location/participants headers)
- Keep the actual meeting notes content

**File naming**: `YYYY-MM-DD {Short Title}.md`
- Strip "Meeting:" prefix if present
- Keep it under 60 characters
- Examples: `2026-03-16 Steve Hall IES Kickoff.md`, `2026-03-14 Nexben Discovery Call.md`

### Step 5: Save to Obsidian

Use the Obsidian MCP to create the file:

```
obsidian: create_vault_file(
  path: "{routed_destination}/YYYY-MM-DD {Title}.md",
  content: {formatted markdown}
)
```

If the destination folder doesn't exist in the vault, create it.

### Step 6: Route Action Items

After saving each transcript, extract action items and route them:

**For items assigned to David / O'Hara:**
Create OmniFocus tasks:
```
omnifocus: create inbox task
  name: "[Meeting Title] {action description}"
  note: "From Plaud transcript {date}. Recording: {recording_id}"
```

**For items assigned to others:**
Include in the report output so David can delegate. Format:
```
Delegation needed:
  @{Name}: {action} (from {meeting title})
```

### Step 7: Report

After processing all recordings, output a summary:

```
Plaud Ingest Complete:
  {N} recordings processed
  {N} saved to vault ({list destinations})
  {N} action items → OmniFocus
  {N} delegation items flagged
  {N} recordings skipped (untranscribed — need Generate clicked)
```

## Handoff to Other Agents

After ingestion, flag content for other agents based on content:

- **Client meeting transcript** (matches account names in routing rules) → Flag for **Chase**: "New transcript from {account} meeting — review for deal context"
- **Content-rich transcript** (workshop, presentation, keynote) → Flag for **Harper**: "New event transcript — check for talking points and content"
- **1:1 or team meeting** → Flag for **Shep**: "1:1 notes captured — review for coaching signals"
- **Strategy discussion** (mentions rocks, initiatives, quarterly goals) → Flag for **Quinn**: "Strategic content in transcript — check alignment"

## Error Handling

| Error | Response |
|-------|----------|
| Plaud MCP not connected | "Plaud MCP server not available. Check that plaud-mcp-ies is registered in MCP config." |
| Auth token expired | "Plaud auth expired. Run `plaud login` or update PLAUD_EMAIL/PLAUD_PASSWORD env vars." |
| Recording has no transcript | Flag for user — needs Generate clicked in web.plaud.ai |
| Obsidian MCP not connected | Fall back to saving markdown to local filesystem, flag for manual move |
| OmniFocus not available | Collect action items in output, flag for manual entry |

## Migration from Legacy Skill

The legacy `plaud-transcript` skill (`skills/plaud-transcript/`) used:
- Chrome automation (osascript → open web.plaud.ai)
- JWT token extraction from Chrome localStorage
- curl for API calls
- Direct filesystem writes to Obsidian vault path

This skill replaces all of that with:
- Plaud MCP tools (no browser needed)
- Obsidian MCP (no direct filesystem access needed)
- Works from Cowork VM, Claude Code, or any MCP-connected context

**The legacy skill should be archived but kept as fallback** in case the MCP server is unavailable and Chrome automation is the only option (e.g., running on the Mac directly without MCP).

## Assigned Agent

**Knox** owns transcript ingestion. **Chief** triggers Knox during /boot and /review-daily.

## Dependencies

| Dependency | Required | Fallback |
|------------|----------|----------|
| Plaud MCP (`plaud_*` tools) | Yes | Legacy Chrome skill |
| Obsidian MCP | Yes | Direct filesystem write (Mac only) |
| OmniFocus MCP | Preferred | osascript (Mac only) |
| Routing rules JSON | Preferred | Default all to zzPlaud/ |

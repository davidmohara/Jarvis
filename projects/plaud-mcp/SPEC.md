# Plaud MCP Server — Specification

**Status**: Spec
**Date**: 2026-03-16
**Owner**: David O'Hara / Jarvis

---

## Goal

Replace Knox's browser-based Plaud scraping with a native MCP server so Jarvis can access transcripts, summaries, and recording metadata in any conversation — instantly, reliably, and without Chrome automation.

---

## Architecture

Two paths evaluated:

### Option A: Adopt `sergivalverde/plaud-toolkit` (Recommended)

**Repository**: https://github.com/sergivalverde/plaud-toolkit
**Language**: TypeScript (monorepo)
**License**: TBD — verify before adoption

**Components**:
- `@plaud/core` — Auth + API client
- `@plaud/cli` — Command-line interface
- `@plaud/mcp` — MCP server (ready to use)

**Existing MCP Tools**:

| Tool | Description |
|------|-------------|
| `plaud_list_recordings` | List all recordings with metadata |
| `plaud_get_transcript` | Get full transcript by recording ID |
| `plaud_get_recording_detail` | Full metadata for a recording |
| `plaud_user_info` | Account info |
| `plaud_get_mp3_url` | Temporary download URL for audio |

**Auth**: JWT Bearer token from Plaud web app. Auto-refreshes within 30 days of expiry. Credentials stored in `~/.plaud/config.json`.

**Pros**: Already built, tested, auto-token-refresh, TypeScript
**Cons**: Third-party dependency, may not cover all IES needs, license unclear

### Option B: Build from Scratch (Fallback)

Use the reverse-engineered API endpoints directly:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/file/simple/web` | GET | List all files |
| `/file/detail/{file_id}` | GET | File details with transcript + metadata |
| `/file/download/{file_id}` | GET | Download MP3 audio |
| `/filetag/` | GET | Get tags/folders |

**Base URL**: `https://api.plaud.ai` (US) or `https://api-euc1.plaud.ai` (EU)
**Auth**: `Authorization: Bearer {JWT_TOKEN}` — obtained from browser DevTools or Plaud desktop app

**Pros**: Full control, no external dependency
**Cons**: Unofficial API, may break, no auto-token-refresh without building it

### Recommendation

**Start with Option A.** Clone `sergivalverde/plaud-toolkit`, verify it works with David's account, then extend with IES-specific tools. Fall back to Option B only if the toolkit is abandoned, incompatible, or restrictively licensed.

---

## Plaud API — Data Model

### Recording Object

```
Recording {
  id: string
  title: string
  created_at: timestamp
  duration: number (seconds)
  language: string
  speakers: [
    { name: string, segments_count: number }
  ]
  transcript: {
    trans_result: {
      segments: [
        { text: string, speaker?: string, start?: number, end?: number }
      ]
    }
  }
  summary: string (AI-generated)
  tags: string[]
  file_type: string
}
```

### Transcript Output

- JSON with speaker diarization
- Plain text with optional timestamps and speaker labels
- AI-generated summaries (action items, key points, etc.)

---

## MCP Tools — Phase 1 (Core)

Inherit from `plaud-toolkit` or build equivalent:

### `plaud_list_recordings`
List recordings with optional filters.

**Parameters**:
- `limit` (number, optional) — max results (default: 50)
- `offset` (number, optional) — pagination
- `tag` (string, optional) — filter by tag/folder

**Returns**: Recording[] with id, title, created_at, duration, speaker count

### `plaud_get_transcript`
Get full transcript for a recording.

**Parameters**:
- `recording_id` (string, required) — recording ID
- `format` (string, optional) — "json" | "text" (default: "json")
- `include_speakers` (boolean, optional) — include speaker labels (default: true)
- `include_timestamps` (boolean, optional) — include timestamps (default: false)

**Returns**: Full transcript with speaker diarization

### `plaud_get_summary`
Get AI-generated summary for a recording.

**Parameters**:
- `recording_id` (string, required) — recording ID

**Returns**: Summary text (action items, key points, decisions)

### `plaud_get_recording_detail`
Get full metadata for a recording.

**Parameters**:
- `recording_id` (string, required) — recording ID

**Returns**: Full recording object including title, duration, speakers, tags, created_at

### `plaud_search_recordings`
Search recordings by keyword across transcripts and titles.

**Parameters**:
- `query` (string, required) — search term
- `limit` (number, optional) — max results

**Returns**: Recording[] matching the query

---

## MCP Tools — Phase 2 (IES Extensions)

These go beyond what `plaud-toolkit` offers and are specific to the IES workflow:

### `plaud_get_action_items`
Extract action items from a transcript using Claude.

**Parameters**:
- `recording_id` (string, required)

**Returns**: Structured action items with assignee, description, due date (if mentioned)

### `plaud_route_transcript`
Route a transcript to the appropriate Obsidian vault location based on content/participants.

**Parameters**:
- `recording_id` (string, required)
- `destination` (string, optional) — override auto-routing

**Returns**: Vault path where transcript was saved

### `plaud_get_recent`
Get recordings from the last N days (convenience tool for morning briefings).

**Parameters**:
- `days` (number, optional) — default: 7

**Returns**: Recording[] from the specified period

---

## Authentication Flow

### Initial Setup

1. Log into https://web.plaud.ai in browser
2. Open DevTools → Network tab → refresh
3. Find any request to `api.plaud.ai` → copy `Authorization` header
4. Store in config:
   ```json
   // ~/.plaud/config.json
   {
     "token": "Bearer eyJ...",
     "region": "us"
   }
   ```

If using `plaud-toolkit`:
```bash
npx @plaud/cli login
# Opens browser auth flow, stores token automatically
```

### Token Refresh

- JWT tokens last ~300 days
- `plaud-toolkit` handles auto-refresh within 30 days of expiry
- If building from scratch: implement refresh logic or accept manual re-auth twice/year

---

## Integration with IES

### Knox Agent Updates

Knox currently scrapes Plaud via Chrome. With the MCP:

| Before (Chrome) | After (MCP) |
|-----------------|-------------|
| Open web.plaud.ai in browser | `plaud_list_recordings` |
| Navigate to recording, scrape text | `plaud_get_transcript` |
| Copy/paste into Obsidian | `plaud_route_transcript` → Obsidian MCP |
| Manual action item extraction | `plaud_get_action_items` |

### Morning Briefing Integration

Chief agent can pull yesterday's recordings:
```
plaud_get_recent(days=1) → for each recording:
  plaud_get_summary() → include in briefing
  plaud_get_action_items() → add to OmniFocus inbox
```

### Steve Hall Deployment

Steve uses Plaud for Zoom/Teams capture. Same MCP server works — different Plaud account, same tools. His IES gets:
- Auto-transcription routing (business vs. foundation vs. personal)
- Action item extraction for Shelley/Emberleigh delegation
- Meeting content feeding into his "Second Brain"

---

## Registration in Claude Config

```json
// ~/.claude/mcp.json (Claude Code)
// or Cowork MCP settings
{
  "plaud": {
    "command": "node",
    "args": ["/path/to/plaud-mcp/dist/index.js"],
    "env": {
      "PLAUD_TOKEN": "Bearer eyJ...",
      "PLAUD_REGION": "us"
    }
  }
}
```

Or if using `plaud-toolkit` directly:
```json
{
  "plaud": {
    "command": "npx",
    "args": ["@plaud/mcp"]
  }
}
```

---

## Decisions

1. **Adopt vs. Build** — Start with `sergivalverde/plaud-toolkit`. Fork only if needed.
2. **Unofficial API risk** — Accepted. Plaud's official API is "coming soon" but gated behind enterprise onboarding. The unofficial endpoints are stable and used by multiple community projects.
3. **Token storage** — Use `plaud-toolkit`'s `~/.plaud/config.json` pattern. No tokens in git.
4. **Phase 2 tools** — IES-specific extensions (action items, routing, recent) built as a wrapper around the core MCP, not modifications to the upstream.
5. **Steve Hall reuse** — Same server binary, different config/credentials. No code changes needed.

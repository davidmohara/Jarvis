# Plaud MCP Server — Full Implementation Plan

**Date**: 2026-03-16
**Owner**: David O'Hara / Jarvis
**Status**: Planned — no blockers

---

## Why

Knox currently pulls Plaud transcripts via Chrome automation (`osascript` → open web.plaud.ai → scrape). This is:

- **Fragile** — breaks on any Plaud UI change
- **Slow** — full browser spin-up per transcript
- **Offline-only** — can't run from Cowork (VM), only from Claude Code on the Mac
- **One-at-a-time** — no batch operations, no search, no filtering

A native MCP replaces all of that with direct API calls. Transcripts become as accessible as calendar events or OmniFocus tasks — available to every agent, in every context, instantly.

---

## Strategic Context

This isn't just a David tool. It's an **IES platform component**.

- **David's IES**: Replaces Knox browser automation. Feeds morning briefings, post-meeting capture, and vault curation.
- **Steve Hall's IES**: Steve uses Plaud for Zoom/Teams recording. His system needs transcript routing (business vs. foundation vs. personal), action item extraction for Shelley/Emberleigh, and "Second Brain" ingestion.
- **Future IES clients**: Any client using Plaud gets this connector out of the box.

---

## Decision: Build vs. Adopt

Two community Plaud MCPs already exist:

| Project | Language | Tools | Auth | Maturity |
|---------|----------|-------|------|----------|
| `sergivalverde/plaud-toolkit` | TypeScript monorepo | 5 tools, CLI, auto-token-refresh | JWT via browser or CLI login | Most complete |
| `davidlinjiahao-plaud-mcp` | Python | 6 tools, no caching | Requires Plaud Desktop app | Thinner, simpler |

**Decision: Evaluate `plaud-toolkit` first.** If it works, adopt it as the core and build IES extensions on top. If it doesn't, build from scratch using the reverse-engineered API (documented in SPEC.md Option B). The reverse-engineered endpoints are well-understood — multiple community projects use them, and the API surface is small (4 endpoints).

---

## Phase 1: Evaluate & Deploy (1-2 hours)

### Prerequisites

Before touching code:

- [ ] Verify David's Plaud account has **Private Cloud Sync** enabled (Settings → Privacy → Private Cloud Sync). Without this, transcripts aren't available via the web API — they stay on-device only.
- [ ] Confirm David has recordings in his Plaud account that are visible at web.plaud.ai

### 1.1 Clone and build `plaud-toolkit`

```bash
cd ~/develop
git clone https://github.com/sergivalverde/plaud-toolkit.git
cd plaud-toolkit
npm install
npm run build
```

**Checkpoint**: Build succeeds with no errors.

### 1.2 Authenticate

**Option A — CLI login (preferred)**:
```bash
npx @plaud/cli login
```
This should open a browser auth flow and store the JWT in `~/.plaud/config.json`.

**Option B — Manual token extraction (fallback)**:
1. Open https://web.plaud.ai in Chrome
2. Log in
3. Open DevTools → Network tab → refresh page
4. Find any request to `api.plaud.ai`
5. Copy the `Authorization` header value (starts with `Bearer eyJ...`)
6. Create `~/.plaud/config.json`:
```json
{
  "token": "Bearer eyJ...",
  "region": "us"
}
```

**Checkpoint**: Config file exists with valid token.

### 1.3 Test via CLI

```bash
npx @plaud/cli list                        # Should return recording list
npx @plaud/cli transcript <recording_id>   # Should return full transcript text
```

**Checkpoint**: Both commands return real data from David's account.

### 1.4 Register as MCP server

Add to Claude Code config (`~/.claude/mcp.json`):
```json
{
  "plaud": {
    "command": "npx",
    "args": ["@plaud/mcp"],
    "cwd": "/Users/davidohara/develop/plaud-toolkit"
  }
}
```

For Cowork, add via MCP settings in the Claude Desktop app (same command/args).

**Checkpoint**: MCP server appears in Claude's tool list on next launch.

### 1.5 Smoke test in Claude

Run these in a Claude conversation:

1. `plaud_list_recordings` — returns a list of recordings with IDs, titles, dates
2. `plaud_get_transcript` with a known recording ID — returns full transcript with speaker labels
3. `plaud_get_recording_detail` — returns metadata (duration, speakers, tags)
4. `plaud_user_info` — returns account info
5. `plaud_get_mp3_url` — returns a temporary download link

**Checkpoint**: All 5 tools return valid data.

### 1.6 Go / No-Go

| Result | Action |
|--------|--------|
| All 5 tools work | **Go** → Proceed to Phase 2 |
| Tools work but are missing features | **Go** → Fork, extend in Phase 2 |
| Auth issues only | Fix auth, re-test |
| Fundamental incompatibility | **No-Go** → Fall back to Option B (build from scratch per SPEC.md) |

---

## Phase 1B: Build from Scratch (only if Phase 1 = No-Go)

If `plaud-toolkit` doesn't work out, build a minimal MCP using the reverse-engineered API.

### Architecture

```
plaud-mcp/
├── package.json
├── tsconfig.json
├── .env.example          # PLAUD_TOKEN, PLAUD_REGION
├── src/
│   ├── index.ts          # MCP server entry point (~40 lines)
│   ├── client.ts         # Plaud API client (~80 lines)
│   ├── tools.ts          # Tool definitions + dispatch (~120 lines)
│   └── types.ts          # TypeScript interfaces
└── README.md
```

### `client.ts` — API Client

```typescript
// Core methods:
class PlaudClient {
  constructor(token: string, region: string = 'us')

  async listFiles(limit?: number, offset?: number): Promise<Recording[]>
  async getFileDetail(fileId: string): Promise<RecordingDetail>
  async downloadMp3(fileId: string): Promise<string>  // returns temp URL
  async getTags(): Promise<Tag[]>
}
```

**API Endpoints**:
- `GET https://api.plaud.ai/file/simple/web` — List files
- `GET https://api.plaud.ai/file/detail/{file_id}` — File detail with transcript
- `GET https://api.plaud.ai/file/download/{file_id}` — MP3 download URL
- `GET https://api.plaud.ai/filetag/` — Tags/folders

All requests use `Authorization: Bearer {JWT_TOKEN}` header.

### `tools.ts` — MCP Tool Definitions

| Tool | Input Schema | Maps to |
|------|-------------|---------|
| `plaud_list_recordings` | `{ limit?: number, offset?: number, tag?: string }` | `listFiles()` |
| `plaud_get_transcript` | `{ recording_id: string, include_speakers?: bool }` | `getFileDetail()` → extract transcript |
| `plaud_get_summary` | `{ recording_id: string }` | `getFileDetail()` → extract summary |
| `plaud_get_recording_detail` | `{ recording_id: string }` | `getFileDetail()` |
| `plaud_get_mp3_url` | `{ recording_id: string }` | `downloadMp3()` |

### `index.ts` — Server Entry

Standard MCP server pattern (matches TripIt and OmniFocus MCP structure):
- `Server` class from `@modelcontextprotocol/sdk`
- `ListToolsRequestSchema` → returns tool definitions
- `CallToolRequestSchema` → dispatches to `executeTool()`
- Stdio transport

### Dependencies

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "latest",
    "node-fetch": "^3.x"
  },
  "devDependencies": {
    "typescript": "^5.x"
  }
}
```

### Build & Register

```bash
npm install && npm run build
```

Register in `~/.claude/mcp.json`:
```json
{
  "plaud": {
    "command": "node",
    "args": ["/Users/davidohara/develop/plaud-mcp/dist/index.js"],
    "env": {
      "PLAUD_TOKEN": "Bearer eyJ...",
      "PLAUD_REGION": "us"
    }
  }
}
```

### Estimated effort for Option B: 3-4 hours

---

## Phase 2: IES Extensions (2-4 hours)

Whether we adopt `plaud-toolkit` or build from scratch, these extensions are IES-specific and get layered on top.

### 2.1 `plaud_search_recordings`

**Problem**: Neither the Plaud API nor `plaud-toolkit` offers server-side search. You can only list files.

**Solution**: Client-side search — pull all recordings (or a cached list), filter by keyword match against title and transcript text.

```typescript
// Pseudocode
async function searchRecordings(query: string, limit: number = 10) {
  const all = await client.listFiles(200);  // grab a large batch
  return all
    .filter(r =>
      r.title.toLowerCase().includes(query.toLowerCase()) ||
      r.transcript_preview?.toLowerCase().includes(query.toLowerCase())
    )
    .slice(0, limit);
}
```

**Optimization**: Cache the recording list in memory with a 5-minute TTL to avoid hammering the API on repeated searches.

### 2.2 `plaud_get_recent`

**Problem**: Morning briefings need "what meetings happened yesterday?" — there's no date-range filter in the API.

**Solution**: Pull list, filter by `created_at` within the last N days.

```typescript
async function getRecent(days: number = 7) {
  const cutoff = Date.now() - (days * 86400000);
  const all = await client.listFiles(100);
  return all.filter(r => new Date(r.created_at).getTime() > cutoff);
}
```

**Used by**: Chief morning briefing, daily review, weekly review.

### 2.3 `plaud_get_action_items`

**Problem**: Plaud's built-in summaries are generic. IES needs structured action items with assignee, description, and routing.

**Two approaches**:

**Approach A — Use Plaud's summary** (simpler):
Pull the AI-generated summary from `getFileDetail()`. It often includes action items but in unstructured prose.

**Approach B — Claude-powered extraction** (better):
Pull the raw transcript, then use Claude to extract structured action items. This is a tool-calls-tool pattern — the MCP tool returns the transcript, and the calling agent (Chief/Knox) processes it through its own prompt.

**Recommendation**: Approach B. The MCP tool just returns the transcript; the extraction logic lives in the agent prompts (Chief for OmniFocus routing, Shep for delegation tracking). This keeps the MCP server stateless and dumb.

**Actually**: This means `plaud_get_action_items` might not need to be an MCP tool at all — it's better as a prompt pattern in Chief/Knox. The MCP just needs to serve the transcript reliably. Keep this as a **"nice to have"** — skip for now, let the agents do the extraction.

### 2.4 `plaud_route_transcript`

**Problem**: After a meeting, the transcript needs to land in the right Obsidian vault folder. Currently manual.

**Solution**: MCP tool that:
1. Pulls transcript via `plaud_get_transcript`
2. Applies routing rules:
   - Meeting title contains client name → `Projects/{client}/meetings/`
   - Title contains "1:1" → `People/{person}/`
   - Title contains "workshop" or "presentation" → `Events/`
   - Default → `Inbox/` for manual filing
3. Calls Obsidian MCP (`create_vault_file`) to save

**Routing rules config** — stored in a simple JSON file:
```json
// plaud-mcp/routing-rules.json
{
  "rules": [
    { "match": "Steve Hall|Bud|Generosity", "destination": "Projects/Steve Hall/meetings/" },
    { "match": "AT&T|Derek", "destination": "Projects/AT&T/meetings/" },
    { "match": "1:1|one-on-one", "destination": "People/" },
    { "match": "podcast|episode", "destination": "Projects/Podcast/" }
  ],
  "default": "Inbox/Plaud/"
}
```

**Note**: This tool crosses MCP boundaries (Plaud MCP → Obsidian MCP). It may be better implemented as a Claude skill or agent workflow rather than an MCP tool. Decision: **build as a skill** (`/plaud-ingest`), not an MCP tool. The MCP stays focused on Plaud data access; the skill handles the orchestration.

### 2.5 Revised Phase 2 Tool List

After analysis, the MCP server should stay lean:

| Tool | Build? | Rationale |
|------|--------|-----------|
| `plaud_search_recordings` | Yes | Client-side search, useful across all agents |
| `plaud_get_recent` | Yes | Date filtering for briefings |
| `plaud_get_action_items` | No | Better as agent prompt logic, not MCP tool |
| `plaud_route_transcript` | No | Better as a skill (`/plaud-ingest`) that orchestrates Plaud MCP + Obsidian MCP |

---

## Phase 3: `/plaud-ingest` Skill (1-2 hours)

This replaces Knox's current `knox-plaud` browser automation skill.

### Skill Structure

```
skills/plaud-ingest/
├── SKILL.md              # Skill instructions
└── routing-rules.json    # Configurable routing rules
```

### Trigger

`/plaud-ingest` or `plaud` or `pull transcripts` or `sync plaud`

### Workflow

```
/plaud-ingest
    │
    ├── plaud_get_recent(days=N)
    │   └── Returns list of new recordings since last ingest
    │
    ├── For each recording:
    │   ├── plaud_get_transcript(recording_id)
    │   ├── plaud_get_recording_detail(recording_id)
    │   │
    │   ├── Apply routing rules (routing-rules.json)
    │   │   └── Determine Obsidian destination folder
    │   │
    │   ├── Format as markdown:
    │   │   ├── YAML frontmatter (date, duration, speakers, source: plaud)
    │   │   ├── Summary (from Plaud or Claude-generated)
    │   │   ├── Action items (Claude-extracted)
    │   │   └── Full transcript with speaker labels
    │   │
    │   ├── obsidian_create_vault_file(path, content)
    │   │   └── Save to determined vault location
    │   │
    │   └── Route action items:
    │       └── Chief → OmniFocus inbox (with meeting context)
    │
    └── Report: "3 transcripts ingested. 2 routed. 1 to inbox. 5 action items captured."
```

### Markdown Output Template

```markdown
---
date: 2026-03-16
source: plaud
recording_id: abc123
duration: 45m
speakers: [David O'Hara, Steve Hall, Bud Marrical]
tags: [meeting, steve-hall, ies]
---

# Meeting: Steve Hall IES Kickoff — 2026-03-16

## Summary
[AI-generated or Claude-extracted summary]

## Action Items
- [ ] @David: Follow up on Penzu API access
- [ ] @Bud: Configure Plaud desktop for Zoom capture
- [ ] @Steve: Provide brand standards and logos

## Transcript

**David O'Hara**: [transcript text...]

**Steve Hall**: [transcript text...]
```

---

## Phase 4: Knox Agent Migration (30 min)

### 4.1 Update `agents/knox.md`

In the Data Requirements table, change:

| Before | After |
|--------|-------|
| Plaud AI: Chrome automation via osascript | Plaud AI: MCP server (`plaud_*` tools) |

In the Task Portfolio table, update the `knox-plaud` skill reference to point to the new `/plaud-ingest` skill.

### 4.2 Update `identity/INTEGRATIONS.md`

Add to Primary Tools table:

```
| Plaud AI | Meeting transcripts, summaries, speaker diarization | MCP server (plaud_*) |
```

Remove or note as deprecated: "Chrome automation via osascript" for Plaud.

### 4.3 Remove old Chrome automation

Delete or archive any osascript-based Plaud scraping code/skills that Knox currently uses.

---

## Phase 5: Steve Hall Deployment (30 min, after his Phase 1)

### 5.1 Separate credentials

Steve gets his own Plaud auth. Two options:

**Option A — Separate config file**:
```json
// Steve's ~/.plaud/config.json (on his machine)
{
  "token": "Bearer eyJ...",
  "region": "us"
}
```

**Option B — Env var override** (for Cowork):
```json
{
  "plaud": {
    "command": "node",
    "args": ["/path/to/plaud-mcp/dist/index.js"],
    "env": {
      "PLAUD_TOKEN": "Bearer eyJ..."
    }
  }
}
```

### 5.2 Custom routing rules

Steve's routing is different from David's:

```json
// Steve's routing-rules.json
{
  "rules": [
    { "match": "Bentley|Honda|auto finance", "destination": "Business/Automotive/" },
    { "match": "Generosity|foundation|stewardship", "destination": "Foundation/" },
    { "match": "Emberleigh|Shelley", "destination": "Assistants/" },
    { "match": "wisdom dinner|Jeffersonian|conclave", "destination": "Convening/" }
  ],
  "default": "Inbox/"
}
```

### 5.3 Route to Google Drive (not Obsidian)

Steve doesn't use Obsidian. His knowledge layer destination is Google Drive. The `/plaud-ingest` skill needs a configurable output target — either Obsidian MCP or Google Drive MCP. This is a skill config option, not a code change.

---

## Testing Plan

### Unit tests (if building from scratch)

| Test | What it validates |
|------|-------------------|
| `client.listFiles()` returns array | API connectivity + auth |
| `client.getFileDetail(id)` returns transcript | Transcript parsing |
| `client.getFileDetail(id)` has speaker data | Speaker diarization |
| Search filters by keyword | Client-side search logic |
| Recent filters by date | Date range logic |
| Invalid token returns clear error | Error handling |
| Missing env vars exits with message | Startup validation |

### Integration tests (both paths)

| Test | What it validates |
|------|-------------------|
| `plaud_list_recordings` in Claude returns data | End-to-end MCP registration |
| `plaud_get_transcript` returns readable text | Transcript quality |
| `/plaud-ingest` creates Obsidian note | Full pipeline (Plaud → Obsidian) |
| `/plaud-ingest` extracts action items | AI extraction quality |
| `/plaud-ingest` routes correctly | Routing rules engine |
| Run twice — no duplicates | Idempotency |

### Acceptance criteria

- [ ] Can pull any transcript from Claude conversation without opening a browser
- [ ] Morning briefing includes yesterday's meeting summaries automatically
- [ ] Post-meeting action items land in OmniFocus inbox within one command
- [ ] Steve Hall's IES can use the same MCP server with different credentials

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Unofficial API breaks | Low | High | Monitor Plaud changelog; official API is "coming soon" — switch when available |
| `plaud-toolkit` abandoned | Medium | Low | Fork and maintain; codebase is small (~500 lines) |
| JWT token expires without warning | Low | Medium | Toolkit auto-refreshes; add token expiry check to morning briefing |
| Plaud rate-limits aggressive pulls | Low | Low | Cache recording list (5-min TTL); batch morning briefing pulls |
| Plaud official API launches with different schema | Medium | Medium | Adapter pattern — swap client layer, keep tool definitions stable |
| Private Cloud Sync not enabled | Low | Blocker | Check in Phase 1 prerequisites before writing any code |

---

## Dependencies

| Dependency | Status | Blocker? | Owner |
|------------|--------|----------|-------|
| Plaud Private Cloud Sync enabled | Verify | Yes | David |
| `plaud-toolkit` repo accessible | Verify | Yes (Phase 1 only) | Open source |
| Node.js + npm on dev machine | Installed | No | — |
| Obsidian MCP deployed | Done | No | — |
| OmniFocus MCP deployed | Done | No | — |
| Google Drive MCP (for Steve) | Not yet | No (Phase 5 only) | Steve's IES Phase 1 |

---

## Effort Summary

| Phase | Description | Hours | Depends On |
|-------|-------------|-------|------------|
| **Phase 1** | Evaluate & deploy `plaud-toolkit` | 1-2 | Private Cloud Sync verified |
| **Phase 1B** | Build from scratch (only if 1 fails) | 3-4 | Phase 1 No-Go |
| **Phase 2** | IES extensions (search, recent) | 1-2 | Phase 1 Go |
| **Phase 3** | `/plaud-ingest` skill | 1-2 | Phase 2 |
| **Phase 4** | Knox migration + docs | 0.5 | Phase 3 |
| **Phase 5** | Steve Hall deployment | 0.5 | Steve's IES Phase 1 |
| **Total (happy path)** | Phases 1+2+3+4 | **4-7 hours** | |
| **Total (build from scratch)** | Phases 1B+2+3+4 | **6-9 hours** | |

---

## Implementation Order

```
[Verify Private Cloud Sync] ─── prerequisite
         │
         v
[Phase 1: Evaluate plaud-toolkit] ──── 1-2 hrs
         │
    Go? ─┤
    │     └─ No ──> [Phase 1B: Build from scratch] ──── 3-4 hrs
    │                        │
    v                        v
[Phase 2: Add search + recent tools] ──── 1-2 hrs
         │
         v
[Phase 3: Build /plaud-ingest skill] ──── 1-2 hrs
         │
         v
[Phase 4: Update Knox + INTEGRATIONS.md] ──── 30 min
         │
         v
[Phase 5: Steve Hall config] ──── 30 min (deferred)
```

---

## Next Actions

1. **David**: Verify Private Cloud Sync is enabled in Plaud app settings
2. **Jarvis**: Clone `plaud-toolkit`, test auth, smoke-test tools (Phase 1)
3. **Jarvis**: Build extensions + skill (Phases 2-3)
4. **David**: Confirm end-to-end by pulling a real transcript from a Claude conversation

---

*Last updated: 2026-03-16*

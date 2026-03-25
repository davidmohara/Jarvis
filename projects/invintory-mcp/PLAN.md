# Invintory MCP Server — Implementation Plan

**Date**: 2026-03-17 (initial), 2026-03-25 (updated)
**Owner**: David O'Hara / Jarvis
**Status**: Phase 1 COMPLETE — MCP server built and tested
**Type**: Personal (David's wine collection)

---

## Why

David has 912 bottles across 294+ labels in Invintory. Right now, answering "what should I pull for dinner tonight?" or "am I past window on anything?" requires opening the app and scrolling. A native MCP makes the cellar queryable from any conversation — morning briefings, event prep, dinner planning, purchase decisions.

This is a personal-life MCP, not a platform component like Plaud. Single user, single collection, read-only.

---

## Auth Discovery Results (2026-03-21)

### What We Found

1. **Firebase Auth is real** — API key `AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA`, project ID `invintory`
2. **Firebase config is NOT in frontend JS** — hidden behind SolidStart SSR proxy
3. **Token found in sessionStorage** — `firebase:authUser:{apiKey}:[DEFAULT]`
4. **David signs in via Apple OAuth** — not email/password, so `signInWithPassword` is not viable
5. **Direct API calls fail** — Cloudflare + CORS block all browser-side and curl calls to `api.invintorywines.com`
6. **Firebase refresh token works** — `securetoken.googleapis.com/v1/token` returns fresh ID tokens
7. **But the API rejects the token** — "AuthTokenMalformedError" for both original and refreshed tokens when called directly (Cloudflare/CORS interference)

### Architecture Confirmed

```
Browser → _server RPC → SolidStart SSR → api.invintorywines.com
                              ↑
                    Server-side only (Cloudflare whitelisted)
```

### Decision: Automated CSV Export → JSON Cache → MCP

Direct API access is blocked by Cloudflare + server-side-only auth proxy. Instead:

1. **Playwright automated export** — logs in, clicks Export CSV, downloads
2. **CSV → JSON parser** — transforms structured data with type enrichment
3. **MCP server** — serves from local JSON cache
4. **Refresh on demand** — re-run Playwright export when data feels stale

This is robust, simple, and gives us everything we need without fighting infrastructure.

---

## Phase 1: Core MCP Server — COMPLETE ✅

### Architecture

```
invintory-mcp-ies/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # MCP server (10 tools)
│   ├── cache.ts          # CSV parser + JSON cache manager
│   └── types.ts          # TypeScript interfaces
└── dist/                 # Compiled JS (ready to run)
```

### 10 MCP Tools

| Tool | Description |
|------|-------------|
| `invintory_summary` | Collection overview: bottles, value, breakdown by type/country/storage |
| `invintory_search` | Search by name, producer, grape, region, tag |
| `invintory_ready` | Wines ready to drink or expiring soon |
| `invintory_recommend` | Recommendations for occasion/type/price/grape |
| `invintory_storage` | View cellar/fridge contents |
| `invintory_value` | Portfolio analysis: top bottles, best ROI |
| `invintory_cache_status` | Cache age and freshness |
| `invintory_import` | Import CSV export into cache |
| `invintory_grapes` | Grape variety breakdown |
| `invintory_tags` | Tag listing and filtering |

### Data Flow

```
Playwright → Export CSV (294 labels, 912 bottles)
         → CSV saved to ~/.config/invintory/
         → invintory_import parses → collection.json + cache-meta.json
         → MCP tools query from memory
```

### Validated Results

- 314 label rows parsed (some labels have multiple sizes)
- 912 total bottles
- $477,403 market value / $88,009 purchase value
- 236 Cabernet matches in search
- All 10 tools tested and working

---

## Phase 2: IES Registration — NEXT

### 2.1 Register in Claude MCP Config

Add to `~/.claude/mcp.json`:
```json
{
  "invintory": {
    "command": "node",
    "args": ["/Users/davidohara/develop/jarvis/projects/invintory-mcp/invintory-mcp-ies/dist/index.js"]
  }
}
```

### 2.2 Agent Integration

- **Chief morning briefing**: Check wines entering/leaving optimal window
- **Event prep**: Recommend wines from cellar matching occasion
- **Purchase check**: "Do I already own this?" via search

### 2.3 Refresh Workflow

Options for keeping data fresh:
1. **Manual**: David says "refresh my wine data" → Jarvis runs Playwright export + import
2. **Scheduled**: Cron-style Playwright refresh (weekly)
3. **On-demand**: MCP reports cache age; Jarvis suggests refresh when stale

---

## Phase 3: Future Enhancements

- Tasting notes integration (from Obsidian vault)
- Market price alerts (external enrichment)
- Cellar organization recommendations
- Wine journal / consumption tracking

---

## Known IDs

- **Firebase API Key**: `AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA`
- **Firebase Project ID**: `invintory`
- **Profile ID**: `FDi9sqylzBXcnR5Dk6vlPjanNC22`
- **Collection ID**: `63421`
- **Auth Provider**: Apple OAuth (sign_in_provider: apple.com)

---

*Last updated: 2026-03-25 — Phase 1 complete, MCP built and tested*

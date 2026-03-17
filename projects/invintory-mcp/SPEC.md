# Invintory MCP Server — Specification

**Status**: Spec — API discovered, auth mechanism pending
**Date**: 2026-03-16
**Owner**: David O'Hara / Jarvis
**Type**: Personal (David's wine collection)

---

## Goal

Give Jarvis native access to David's wine collection so it can answer collection questions, suggest wines for events, track drinking windows, and surface collection insights — all without opening the Invintory app.

---

## Platform Overview

**Invintory** (invintory.com) is a wine collection management platform.

| Feature | Detail |
|---------|--------|
| **Platforms** | iOS app + web app (app.invintory.com) |
| **Database** | 2M+ sommelier-curated wines |
| **Storage** | Cloud-based, synced across devices |
| **Auth** | Email/password login |
| **Export** | CSV only (group by bottle or group by label) |
| **Integrations** | CellarTracker import, Vivino import, Wine-Searcher market prices, Govee temperature sensors |
| **Public API** | None documented |

---

## Architecture

### Path A: Reverse-Engineer Web App API (Recommended) ✅ DISCOVERY COMPLETE

The web app at `app.invintory.com` is a **SolidStart SSR** application (SolidJS). Unlike a typical SPA, all authenticated API calls are proxied server-side — the browser never directly calls the backend API with auth tokens. The server-side RPC happens via a `_server` POST endpoint.

**Backend API**: `https://api.invintorywines.com/v3/`
**Images**: `https://images.invintorywines.com`
**Real-time**: Pusher websockets for live updates

**Confirmed Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v3/config` | GET | App configuration |
| `/v3/profiles/{profile_id}` | GET | User profile |
| `/v3/profiles/{profile_id}/collections` | GET | List user's collections |
| `/v3/collections/{collection_id}/fields` | GET | Collection field definitions |
| `/v3/collections/{collection_id}/details` | GET | Collection details/stats |
| `/pusher/auth` | POST | Websocket auth |

**Known IDs**:
- Profile ID: `FDi9sqylzBXcnR5Dk6vlPjanNC22` (Firebase UID format)
- Collection ID: `63421`

**Inferred Endpoints** (from UI behavior):
- `/v3/collections/{id}/bottles` or `/labels` — paginated wine list
- `/v3/labels/{label_id}` — wine detail (UI uses `labelId` param)
- Search, filter, analytics, activity, storage endpoints

**Auth**: Bearer token required. Likely **Firebase Auth** based on profile ID format. Server-side proxy handles auth — tokens not exposed client-side. See PLAN.md Phase 0 for auth resolution strategy.

**Risks**: Internal API can change without notice. No SLA or stability guarantee.

### Path B: CSV Export Pipeline (Fallback)

If the internal API is too locked down or changes frequently:
1. Export collection as CSV from Invintory
2. Parse CSV into structured data
3. Serve via MCP as a static dataset
4. Re-export periodically to refresh

**Pros**: Stable, no auth issues
**Cons**: Read-only, stale data, no real-time queries, no market valuations

### Path C: Contact Invintory for API Access

Invintory has a partner program (invintory.com/partners). They work with cellar makers and sensor companies. A developer/integration partner request may yield official API access.

**Contact**: support@invintory.com or partner form on website.

### Recommendation

**Start with Path A** — open Chrome, intercept the API, document endpoints. Fall back to Path B (CSV) if the API is too complex or unstable. Pursue Path C in parallel as a long-term play.

---

## Data Model (Observed from UI — 2026-03-17)

### Wine Label (one entry per unique wine)

```
Label {
  label_id: string                // e.g. "495251" (used in URL params)
  name: string                    // "2021 Alpha Omega Napa Valley Cabernet Sauvignon"
  producer: string                // "Alpha Omega"
  vintage: number                 // 2021
  region: string                  // "Napa Valley, California, United States"
  country: string                 // "United States" (with flag icon)
  type: string                    // "Cabernet Sauvignon" (displayed as tag)
  quantity: number                // bottles in collection (e.g. 1, 2, 3, 4)
  market_price: number            // e.g. $146.89 (Wine-Searcher)
  purchase_price: number          // e.g. $39.00
  drinking_window: {
    start: number                 // year (e.g. 2028)
    end: number                   // year (e.g. 2045)
  }
  drink_status: string            // "Hold", "Ready to drink", "Expiring soon"
  tasting_profile: {
    body: string                  // "Very full", "Full", "Medium"
    sweetness: string             // "Dry", "Bone dry"
    tannin: string                // "High", "Medium", "Very high"
    acidity: string               // "High", "Medium", "Very high"
  }
  critic_score: number            // sortable field (confirmed)
  photo_url: string               // served from images.invintorywines.com
}
```

### Bottle (individual physical bottle within a label)

```
Bottle {
  bottle_id: string
  label_id: string                // parent label
  size: string                    // "750ml"
  barcode: string                 // e.g. "431158"
  purchase_price: number          // per-bottle price
  date_added: string              // e.g. "Mar 26, 2025"
  storage_location: {
    zone: string                  // "Classic"
    rack: string                  // "Tubes"
    position: string              // "R10, C6, D2" (row, column, depth)
  }
}
```

### Collection Summary

```
Collection {
  total_bottles: number
  total_value: number
  wines_by_type: { red: n, white: n, rosé: n, sparkling: n }
  wines_by_region: { [region]: n }
  ready_to_drink: Wine[]           // within drinking window now
  past_window: Wine[]              // past optimal drinking window
  recent_additions: Wine[]
}
```

### Tasting / Consumption Log

```
TastingEntry {
  wine_id: string
  date: string
  rating: number
  notes: string
  occasion: string
}
```

---

## MCP Tools — Phase 1 (Core Collection Access)

### `invintory_list_wines`
List wines in the collection with optional filters.

**Parameters**:
- `type` (string, optional) — "red", "white", "rosé", "sparkling"
- `region` (string, optional) — filter by region
- `status` (string, optional) — "in_cellar", "consumed", "wishlist"
- `limit` (number, optional) — max results
- `sort` (string, optional) — "name", "vintage", "value", "rating", "added"

**Returns**: Wine[] with core fields

### `invintory_get_wine`
Get full details for a specific wine.

**Parameters**:
- `wine_id` (string, required)

**Returns**: Full Wine object including tasting notes, market value, cellar location

### `invintory_search`
Search wines by keyword across name, producer, region, vintage, notes.

**Parameters**:
- `query` (string, required)
- `limit` (number, optional)

**Returns**: Wine[] matching the query

### `invintory_collection_summary`
Get collection-level statistics.

**Returns**: Total bottles, total value, breakdown by type/region, ready-to-drink count

### `invintory_ready_to_drink`
List wines currently within their optimal drinking window.

**Parameters**:
- `limit` (number, optional)

**Returns**: Wine[] where current year is within drinking_window.start and drinking_window.end

### `invintory_past_window`
List wines past their optimal drinking window — needs attention.

**Returns**: Wine[] where current year > drinking_window.end

---

## MCP Tools — Phase 2 (Intelligence & Events)

### `invintory_suggest_for_dinner`
Suggest wines for a specific occasion.

**Parameters**:
- `guests` (number, required) — number of guests
- `courses` (string[], optional) — ["appetizer", "main", "dessert"]
- `preferences` (string, optional) — "bold reds", "light whites", etc.
- `budget_max` (number, optional) — max value per bottle to pull

**Returns**: Suggested wines with pairing rationale

### `invintory_value_trend`
Collection value over time (if historical data is available).

**Returns**: Value snapshots, top appreciating wines, total portfolio performance

### `invintory_duplicate_check`
Check if a wine/vintage already exists in the collection before purchasing.

**Parameters**:
- `producer` (string, required)
- `vintage` (number, optional)

**Returns**: Existing wines matching producer/vintage

---

## Authentication

**API Base URL**: `https://api.invintorywines.com/v3/`
**Auth Header**: `Authorization: Bearer {token}`
**Error on missing auth**: `{"error":{"type":"InvalidTokenError","message":"No auth token was sent"}}`

### Option A — Firebase Auth (Most Likely) ⭐

Profile ID format (`FDi9sqylzBXcnR5Dk6vlPjanNC22`) is classic Firebase UID. If confirmed:

1. Extract Firebase project config (API key) from app's JS bundle
2. Authenticate via Firebase REST API:
   ```
   POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}
   { "email": "...", "password": "...", "returnSecureToken": true }
   ```
3. Use returned `idToken` as Bearer token (1-hour expiry)
4. Auto-refresh via `refreshToken` (long-lived, months)

### Option B — Session Cookie Extraction (Fallback)

Extract cookies from authenticated Chrome session. Replay with API requests.

### Option C — Contact Invintory for API Access (Long-term)

Email support@invintory.com or use partner form. Invintory works with cellar makers and sensor companies — a developer/integration partner request may yield official API access.

### Config Storage

```json
// ~/.invintory/config.json
{
  "email": "david@...",
  "password": "...",
  "firebase_api_key": "AIza...",
  "collection_id": "63421",
  "profile_id": "FDi9sqylzBXcnR5Dk6vlPjanNC22"
}
```

Or env vars: `INVINTORY_EMAIL`, `INVINTORY_PASSWORD`, `INVINTORY_FIREBASE_KEY`, `INVINTORY_COLLECTION_ID`

---

## Registration in Claude Config

```json
// ~/.claude/mcp.json
{
  "invintory": {
    "command": "node",
    "args": ["/path/to/invintory-mcp/dist/index.js"],
    "env": {
      "INVINTORY_TOKEN": "...",
      "INVINTORY_BASE_URL": "..."
    }
  }
}
```

---

## IES Integration

### Morning Briefing
- "You have a dinner tonight with 6 guests. You have 3 bottles of [wine] ready to drink — want me to suggest a selection?"

### Event Prep
- Wisdom dinners, client dinners, entertaining → Jarvis suggests wines from the cellar based on guest count, menu, and preferences

### Collection Health
- Weekly review: "2 wines are past their drinking window. 5 are entering optimal window this month."

### Purchase Intelligence
- Before buying: "You already own 3 bottles of this producer. Current market value is $X per bottle."

---

## Decisions

1. **API discovery first** — Cannot build without knowing the endpoints. Chrome DevTools session is step zero.
2. **Personal MCP** — This is David's personal collection, not an IES platform component (unlike Plaud). No multi-tenant requirement.
3. **Read-only first** — Phase 1 is query-only. No writes (adding wines, logging tastings) until the API is well understood.
4. **CSV fallback** — If API discovery fails, export CSV and serve as static MCP. Refresh manually.
5. **Partner inquiry** — Email support@invintory.com in parallel to ask about API/developer access.

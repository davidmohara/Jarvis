# Invintory MCP Server — Full Implementation Plan

**Date**: 2026-03-17
**Owner**: David O'Hara / Jarvis
**Status**: Planned — API auth mechanism pending
**Type**: Personal (David's wine collection)

---

## Why

David has 914 bottles across 294 labels in Invintory. Right now, answering "what should I pull for dinner tonight?" or "am I past window on anything?" requires opening the app and scrolling. A native MCP makes the cellar queryable from any conversation — morning briefings, event prep, dinner planning, purchase decisions.

This is a personal-life MCP, not a platform component like Plaud. Single user, single collection, read-only to start.

---

## What We Know (API Discovery — 2026-03-17)

### Architecture

Invintory's web app (`app.invintory.com`) is built on **SolidStart** (SolidJS SSR framework). All authenticated API calls are proxied through the server — the browser never directly calls the API with a token. The actual backend lives at `api.invintorywines.com/v3/`.

**Key discovery**: The SolidStart `_server` POST endpoint is the client→server RPC mechanism. The server holds the auth session and proxies requests to the real API. This means:

1. We **cannot** capture Bearer tokens from Chrome DevTools (they're server-side only)
2. The real API requires `Authorization: Bearer {token}` headers
3. Auth is likely **Firebase Auth** (profile ID format `FDi9sqylzBXcnR5Dk6vlPjanNC22` is classic Firebase UID)

### Confirmed API Surface

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v3/config` | GET | App configuration |
| `/v3/profiles/{profile_id}` | GET | User profile |
| `/v3/profiles/{profile_id}/collections` | GET | List user's collections |
| `/v3/collections/{collection_id}/fields` | GET | Collection field definitions |
| `/v3/collections/{collection_id}/details` | GET | Collection details/stats |
| `/pusher/auth` | POST | Websocket auth for real-time updates |

### Known IDs

- **Profile ID**: `FDi9sqylzBXcnR5Dk6vlPjanNC22`
- **Collection ID**: `63421`
- **Collection**: 294 labels, 914 bottles

### Inferred Endpoints (from UI behavior)

The app shows wine lists with pagination, sorting, filtering, and detail views. These must map to API endpoints:

| Likely Endpoint | Evidence |
|----------------|----------|
| `/v3/collections/{id}/bottles` or `/v3/collections/{id}/labels` | Collection list with `page=1&limit=50` pagination |
| `/v3/labels/{label_id}` | Wine detail panel (triggered by `labelId=495251` URL param) |
| `/v3/collections/{id}/bottles?search={query}` | Search collection textbox |
| `/v3/collections/{id}/analytics` | Analytics page at `/analytics` |
| `/v3/collections/{id}/activity` | Activity feed at `/activity` |
| `/v3/collections/{id}/storage` | Storage/cellar view |

### Data Model (from UI)

Each wine/label shows:
- Name, vintage, producer, region, country
- Grape variety (tags: "Cabernet Sauvignon")
- Market price (`$146.89`) and purchase price (`$39.00`)
- Drinking window (`2028-2045`, status: "Hold", "Ready to drink", "Expiring soon")
- Quantity (bottle count per label)
- Bottle size (750ml)
- Storage location (`Classic > Tubes > R10, C6, D2` — zone > rack > position)
- Barcode/ID (`431158`)
- Date added (`Mar 26, 2025`)
- Tasting profile: body (Very full/Full/Medium), sweetness (Dry/Bone dry), tannin (High/Medium), acidity (High/Very high)

### Sort Fields (confirmed from UI combobox)
- `name,asc/desc`
- `added,asc/desc`
- `vintage,asc/desc`
- `quantity,asc/desc`
- `purchase_price,asc/desc`
- `market_price,asc/desc`
- `drink_window_start,asc/desc`
- `drink_window_end,asc/desc`
- `critic_score,asc/desc`

### Filter Dimensions (from UI)
- Wine Type
- Storage location
- Tags
- Drink Status

---

## Authentication Strategy

The biggest unknown. Three paths to resolve:

### Path 1: Firebase Auth Direct Login (Most Likely)

If Invintory uses Firebase Authentication (strong evidence from UID format):

1. Find the Firebase project config (API key, project ID) from the app's JavaScript bundle
2. Use Firebase Auth REST API to get an ID token:
   ```
   POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}
   { "email": "...", "password": "...", "returnSecureToken": true }
   ```
3. Use the returned `idToken` as the Bearer token for API calls
4. Refresh via `refreshToken` when expired (1-hour expiry typical for Firebase)

**Effort to validate**: 30 min
**Confidence**: High — profile ID format is unmistakably Firebase

### Path 2: Session Cookie Extraction

If Firebase isn't the auth layer:

1. Log into `app.invintory.com` in Chrome
2. Extract session cookies from Chrome's cookie store (via Desktop Commander or osascript)
3. Replay cookies with API requests
4. Re-extract when session expires

**Effort**: 15 min to test
**Confidence**: Medium — may work but cookies could be HttpOnly/SameSite restricted

### Path 3: Contact Invintory

Email `support@invintory.com` or use the partner form at `invintory.com/partners` to request developer/API access.

**Effort**: 5 min to send email, unknown response time
**Confidence**: Low for timeline, high for long-term stability

### Recommendation

**Try Path 1 first** (Firebase Auth). If the Firebase project config is in the app's JS bundle, we can authenticate directly and have a stable, renewable token flow. Path 3 in parallel as a long-term play.

---

## Phase 0: Auth Discovery (1-2 hours)

This is the gating phase. Can't build anything without API access.

### 0.1 Extract Firebase Config

Navigate to `app.invintory.com` in Chrome. Examine the JavaScript bundle for Firebase configuration:

```javascript
// Looking for something like:
{
  apiKey: "AIza...",
  authDomain: "invintory-xxx.firebaseapp.com",
  projectId: "invintory-xxx"
}
```

Search strategies:
- View page source for inline config
- Check `__SOLID_DATA__` or hydration payloads
- Examine JS bundle files for `firebase` or `apiKey`
- Check `window.__firebase_config` or similar globals

**Checkpoint**: Firebase API key and project ID captured.

### 0.2 Test Firebase Auth

```bash
curl -X POST \
  "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email":"david@...", "password":"...", "returnSecureToken":true}'
```

**Checkpoint**: Receive `idToken` and `refreshToken`.

### 0.3 Test API Call with Token

```bash
curl -H "Authorization: Bearer {idToken}" \
  "https://api.invintorywines.com/v3/profiles/FDi9sqylzBXcnR5Dk6vlPjanNC22/collections"
```

**Checkpoint**: Receive collection data (not `InvalidTokenError`).

### 0.4 Map Remaining Endpoints

With a working token, systematically call:
- `/v3/collections/63421/bottles?page=1&limit=10` (or `/labels`)
- `/v3/labels/{label_id}` (wine detail)
- `/v3/collections/63421/analytics`
- Various filter/search combinations

**Checkpoint**: Full endpoint catalog with request/response shapes documented.

### 0.5 Go / No-Go

| Result | Action |
|--------|--------|
| Firebase auth works, API responds | **Go** → Phase 1 |
| Firebase auth works but API needs custom token | Investigate custom claims, then Go |
| Firebase auth doesn't exist | Try Path 2 (session cookies) |
| All auth paths fail | **Fall back to CSV export** (Path B in SPEC.md) |

---

## Phase 1: Core MCP Server (3-4 hours)

### Architecture

```
invintory-mcp/
├── package.json
├── tsconfig.json
├── .env.example          # INVINTORY_EMAIL, INVINTORY_PASSWORD, INVINTORY_API_KEY
├── src/
│   ├── index.ts          # MCP server entry point
│   ├── auth.ts           # Firebase Auth client (login + token refresh)
│   ├── client.ts         # Invintory API client
│   ├── types.ts          # TypeScript interfaces
│   └── config.ts         # Config management (~/.invintory/config.json or env vars)
└── README.md
```

### `auth.ts` — Firebase Auth

```typescript
class InvintoryAuth {
  constructor(apiKey: string)

  async login(email: string, password: string): Promise<AuthTokens>
  async refresh(refreshToken: string): Promise<string>  // returns new idToken
  async getToken(): Promise<string>  // auto-refreshes if expired

  // Firebase ID tokens expire after 1 hour
  // Refresh tokens are long-lived (months)
  // Store refresh token in config, auto-refresh on each MCP call
}
```

### `client.ts` — API Client

```typescript
class InvintoryClient {
  constructor(auth: InvintoryAuth, collectionId: string)

  // Core queries
  async listWines(options?: ListOptions): Promise<Wine[]>
  async getWine(labelId: string): Promise<WineDetail>
  async search(query: string, limit?: number): Promise<Wine[]>
  async getCollectionSummary(): Promise<CollectionSummary>

  // Filtered queries
  async getReadyToDrink(limit?: number): Promise<Wine[]>
  async getPastWindow(): Promise<Wine[]>
  async getByType(type: WineType): Promise<Wine[]>
  async getByStorage(zone: string): Promise<Wine[]>
}

interface ListOptions {
  page?: number
  limit?: number
  sort?: string        // "name,asc" | "vintage,desc" | etc.
  type?: string        // wine type filter
  storage?: string     // storage location filter
  drinkStatus?: string // "ready" | "hold" | "expiring" | "past"
  tags?: string[]
}
```

### MCP Tools — Phase 1

| Tool | Description | Parameters |
|------|-------------|------------|
| `invintory_list_wines` | List wines with filters/sorting | `type?`, `sort?`, `limit?`, `storage?`, `drink_status?` |
| `invintory_get_wine` | Full detail for one wine | `label_id` (required) |
| `invintory_search` | Keyword search | `query` (required), `limit?` |
| `invintory_collection_summary` | Collection stats | none |
| `invintory_ready_to_drink` | Wines in optimal window now | `limit?` |
| `invintory_past_window` | Wines past optimal window | none |

### Dependencies

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "latest",
    "zod": "^3.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "tsx": "^4.x",
    "@types/node": "^22.x"
  }
}
```

---

## Phase 2: IES Intelligence Layer (2-3 hours)

### 2.1 `invintory_suggest_for_dinner`

Smart wine selection for events:

```typescript
// Input: { guests: 6, courses: ["appetizer", "main", "dessert"], preferences: "bold reds" }
// Logic:
// 1. Filter collection for ready-to-drink wines
// 2. Match preferences to tasting profile (body, sweetness, tannin)
// 3. Consider value (don't suggest the $300 bottle for casual dinner)
// 4. Return suggestions with pairing rationale
```

**Note**: The "pairing rationale" is better generated by the calling agent (Jarvis/Chief), not the MCP tool. The tool returns candidate wines; the agent generates the recommendation prose.

### 2.2 `invintory_duplicate_check`

Before buying:

```typescript
// Input: { producer: "Ampère", vintage: 2019 }
// Returns: matching wines already in collection with quantities
```

### 2.3 `invintory_storage_map`

Cellar overview:

```typescript
// Returns: storage zones with bottle counts
// { "Classic > Tubes": 45, "Classic > Diamond": 30, ... }
```

### 2.4 Revised Phase 2 Tool List

| Tool | Build? | Rationale |
|------|--------|-----------|
| `invintory_suggest_for_dinner` | Yes | Core use case — event planning |
| `invintory_duplicate_check` | Yes | Purchase decision support |
| `invintory_storage_map` | Yes | Cellar overview for organization |
| `invintory_value_trend` | Maybe | Depends on API exposing historical data |

---

## Phase 3: IES Integration (1 hour)

### 3.1 Morning Briefing Hook

Add to Chief's morning briefing template:

```
Wine cellar check:
- {N} wines entering optimal window this month
- {N} wines past their window (need attention)
- Event tonight? Here are suggestions from your cellar.
```

### 3.2 Event Prep Integration

When calendar shows a dinner/event:
1. Chief detects event in calendar
2. Pulls guest count from event details
3. Calls `invintory_suggest_for_dinner` with context
4. Includes suggestions in event prep briefing

### 3.3 Update System Files

- `identity/INTEGRATIONS.md` — Add Invintory to Personal Tools table
- `agents/chief.md` — Add wine cellar check to morning briefing template (optional, low-key mention)

---

## Phase 4: CSV Fallback (only if API auth fails)

If all auth paths fail:

### 4.1 Export CSV from Invintory

The app has an "Export CSV" button (confirmed in UI). Two formats:
- Group by bottle (one row per physical bottle)
- Group by label (one row per wine, with quantity)

### 4.2 CSV-Based MCP Server

```
invintory-mcp/
├── src/
│   ├── index.ts       # MCP server
│   ├── csv-loader.ts  # Parse and index CSV
│   └── tools.ts       # Same tool definitions, backed by in-memory CSV data
├── data/
│   └── collection.csv # Exported from Invintory (refreshed manually)
└── refresh.sh         # Script to re-export (instructions for David)
```

**Pros**: No auth issues, stable, immediate
**Cons**: Stale data (manual refresh), no market prices (may not be in export), no real-time updates

### 4.3 Hybrid Approach

Start with CSV for collection data. Use web scraping (Chrome automation) for market prices and real-time data only when needed.

---

## Testing Plan

### Auth validation
| Test | Validates |
|------|-----------|
| Firebase login returns tokens | Auth mechanism works |
| API call with token returns data | Token is accepted by API |
| Token refresh after expiry | Long-running stability |
| Invalid credentials return clear error | Error handling |

### MCP tool tests
| Test | Validates |
|------|-----------|
| `invintory_list_wines` returns 294 labels | Full collection access |
| `invintory_get_wine` returns detail with tasting profile | Detail endpoint |
| `invintory_search("Ampère")` returns correct results | Search functionality |
| `invintory_ready_to_drink` filters correctly | Drink window logic |
| `invintory_collection_summary` matches app stats | Summary accuracy |
| `invintory_suggest_for_dinner` returns reasonable picks | Intelligence layer |

### Acceptance criteria

- [ ] "What wines should I open tonight?" returns actionable suggestions
- [ ] "Do I already have this wine?" answers in seconds
- [ ] "What's past its window?" surfaces wines needing attention
- [ ] Morning briefing includes cellar status when relevant
- [ ] No manual app opening required for collection queries

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Firebase Auth assumption wrong | Medium | Blocker | Path 2 (session cookies) and Path 3 (contact Invintory) as fallbacks |
| API rate limiting | Low | Low | Cache collection list (5-min TTL); personal use = low volume |
| API schema changes | Medium | Medium | Pin to v3; adapter pattern for version migration |
| Auth token expires during long session | Medium | Low | Auto-refresh in auth layer; Firebase refresh tokens last months |
| Invintory shuts down or pivots | Low | High | CSV export as permanent backup; data portability |
| Market price data not in API | Medium | Low | Wine-Searcher integration as separate enrichment (Phase 3+) |

---

## Dependencies

| Dependency | Status | Blocker? | Owner |
|------------|--------|----------|-------|
| Firebase Auth config discovery | Pending | Yes | Jarvis |
| David's Invintory credentials | Available | No | David |
| Node.js + npm on dev machine | Installed | No | — |
| Obsidian MCP (for cellar notes) | Deployed | No | — |
| OmniFocus MCP (for wine tasks) | Deployed | No | — |

---

## Effort Summary

| Phase | Description | Hours | Depends On |
|-------|-------------|-------|------------|
| **Phase 0** | Auth discovery (Firebase config + test) | 1-2 | Chrome access |
| **Phase 1** | Core MCP server (6 tools) | 3-4 | Phase 0 Go |
| **Phase 2** | Intelligence layer (3 tools) | 2-3 | Phase 1 |
| **Phase 3** | IES integration (briefing hooks) | 1 | Phase 2 |
| **Phase 4** | CSV fallback (only if auth fails) | 2-3 | Phase 0 No-Go |
| **Total (API path)** | Phases 0+1+2+3 | **7-10 hours** | |
| **Total (CSV fallback)** | Phases 4+partial 2+3 | **5-7 hours** | |

---

## Implementation Order

```
[Phase 0: Auth Discovery] ──── 1-2 hrs
         │
    Firebase works? ─┤
    │                 └─ No ──> [Try session cookies] ──> [Try CSV fallback]
    │                                                            │
    v                                                            v
[Phase 1: Core MCP Server] ──── 3-4 hrs              [Phase 4: CSV MCP] ──── 2-3 hrs
         │                                                       │
         v                                                       v
[Phase 2: Intelligence Layer] ──── 2-3 hrs            [Phase 2: Partial intelligence]
         │                                                       │
         v                                                       v
[Phase 3: IES Integration] ──── 1 hr                  [Phase 3: IES Integration]
```

---

## Next Actions

1. **Jarvis**: Extract Firebase config from app.invintory.com JavaScript bundle (Phase 0.1)
2. **David**: Confirm Invintory login credentials are available for API auth
3. **David (parallel)**: Email support@invintory.com to inquire about developer/API access
4. **Jarvis**: Build MCP server once auth is validated (Phase 1)

---

*Last updated: 2026-03-17*

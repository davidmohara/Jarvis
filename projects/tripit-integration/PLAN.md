# TripIt MCP Server — Implementation Plan

## Context

David has a fully specced TripIt integration project at `projects/tripit-integration/` with types, package.json, tsconfig, and a travel-brief skill already scaffolded. The MCP server source files don't exist yet. This plan builds the source files needed to make the server functional using Basic HTTP Auth (not OAuth).

## Auth Approach: Basic HTTP Auth

`Authorization: Basic <base64(email:password)>` header on every request. Two env vars:
- `TRIPIT_EMAIL`
- `TRIPIT_PASSWORD`

This eliminates the need for `auth.ts`, `oauth-1.0a` dependency, and the `scripts/authorize.ts` authorization flow.

## Files to Create

All under `projects/tripit-integration/tripit-mcp/src/`:

### 1. `client.ts` — TripIt API Client (~100 lines)
- Load `TRIPIT_EMAIL` + `TRIPIT_PASSWORD` from env, validate present
- Build Basic auth header: `Buffer.from(\`${email}:${password}\`).toString('base64')`
- `TripItClient` class with private `request(path)` method
- URL construction uses TripIt's path-based params (e.g., `/list/trip/past/true/page_num/1/format/json`)
- `ensureArray<T>()` utility to normalize TripIt's single-object-vs-array responses
- Public methods: `listTrips()`, `getTrip(id)`, `listObjects()`, `getProfile()`, `listPointsPrograms()`
- Error handling: non-200 → throw with status + body

### 2. `tools.ts` — Tool Definitions + Dispatch (~130 lines)
- `toolDefinitions[]` array with JSON Schema `inputSchema` for each tool
- 5 tools: `tripit_list_trips`, `tripit_get_trip`, `tripit_list_objects`, `tripit_get_profile`, `tripit_list_points_programs`
- `executeTool(name, args, client)` → switch dispatch → JSON-stringified results
- Error responses use `isError: true` pattern

### 3. `index.ts` — MCP Server Entry Point (~40 lines)
- Uses low-level `Server` class (matches omnifocus-mcp pattern)
- Registers `ListToolsRequestSchema` → returns `toolDefinitions`
- Registers `CallToolRequestSchema` → delegates to `executeTool()`
- Stdio transport, SIGINT/SIGTERM handlers

## Files to Update

### `package.json`
- Remove `oauth-1.0a` dependency (not needed with Basic auth)
- Remove `"auth"` script (no OAuth flow)

### `.env.example`
- Replace OAuth vars with `TRIPIT_EMAIL` and `TRIPIT_PASSWORD`

## No New Dependencies

With Basic auth, we only need:
- `@modelcontextprotocol/sdk` — Server, StdioServerTransport, request schemas
- `node-fetch` — HTTP requests

`oauth-1.0a` is removed.

## Implementation Order

1. Update `package.json` and `.env.example`
2. `client.ts` (API layer with Basic auth)
3. `tools.ts` (tool definitions + dispatch)
4. `index.ts` (server wiring)
5. `npm install && npm run build` to verify compilation

## Post-Build: Registration

1. Add `TRIPIT_EMAIL` and `TRIPIT_PASSWORD` to `.env`
2. Add MCP server to `~/.claude/mcp.json`:
```json
"tripit": {
  "command": "node",
  "args": [".../tripit-mcp/dist/index.js"],
  "env": { "TRIPIT_EMAIL": "...", "TRIPIT_PASSWORD": "..." }
}
```

## Verification

1. `npm run build` — TypeScript compiles with no errors
2. Without credentials: server exits with clear "missing env var" message
3. With credentials: `tripit_list_trips` returns upcoming trips
4. `tripit_get_trip` with a trip ID returns full itinerary

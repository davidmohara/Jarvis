---
name: rigby-evolution-poll
description: Check the web app for available evolution updates and cache the result locally
context: fork
agent: general-purpose
---

<!-- system:start -->
# Rigby — Evolution Poll

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Check the IES web app for available evolution updates. This runs non-blocking at system boot. The executive is never interrupted — any results are cached for the notification step.

## Process

### 1. Read Configuration

Read `config/settings.json` and extract:
- `ies_app_url` — base URL of the IES web application
- Authentication is via Microsoft Entra ID (OIDC) — no static API token needed
- `audience` — evolution audience for this instance (usually `internal`; defaults to `internal`)

If `ies_app_url` is not configured: log `[evolution-poll] ies_app_url not configured — skipping poll` and exit silently.

If OIDC authentication is not available: log `[evolution-poll] No auth session available — skipping poll` and exit silently.

### 2. Check Poll Cache

Read `evolutions/.poll-cache.json` if it exists.

If the cache exists and `polled_at` is within the current session (same calendar date), return the cached result without re-polling.

Cache schema:
```json
{
  "polled_at": "2026-03-01T08:00:00Z",
  "available": [
    {
      "id": "cuid...",
      "version": "550e8400-e29b-41d4-a716-446655440000",
      "name": "February Update",
      "description": "...",
      "releasedAt": "2026-02-01T00:00:00Z",
      "changelog": ["..."],
      "downloadUrl": "https://app.example.com/api/evolutions/cuid.../package"
    }
  ]
}
```

### 3. Read Applied Evolution History

Read `evolutions/history.md` and extract the list of evolution IDs that have already been applied to this instance. This is used to filter the poll response locally — the server returns all approved evolutions and the local instance skips any it has already applied.

### 4. Poll the Web App

Make a GET request:

```
GET {ies_app_url}/api/evolutions?audience={audience}
Authorization: Bearer {session_token}
```

**If the request fails for any reason** (timeout, DNS failure, HTTP error, no internet):
- Log: `[evolution-poll] Endpoint unreachable — continuing boot normally`
- Write an empty cache: `{ "polled_at": "{now}", "available": [] }`
- Exit silently — do NOT surface error to executive

**If HTTP 401 Unauthorized:**
- Log: `[evolution-poll] Auth token rejected — OIDC session may have expired`
- Write empty cache and exit silently

**If HTTP 200:**
- Parse response JSON
- Extract `available` array
- Proceed to step 5

### 5. Filter Already-Applied and Cache the Result

From the `available` array, remove any evolutions whose `id` appears in the applied history extracted in step 3.

Write `evolutions/.poll-cache.json` with:
- `polled_at` — current ISO timestamp
- `available` — filtered array (only not-yet-applied evolutions)

### 6. Return Result

Output the count of available evolutions:
- 0 available: output nothing (silent success)
- 1+ available: output `[evolution-poll] {count} evolution(s) available`

Do NOT notify the executive here — that is handled by the evolution-notify skill.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Config**: Read `config/settings.json`
- **Cache**: Read/Write `evolutions/.poll-cache.json`
- **HTTP**: Use Bash with `curl` or equivalent to call the web app endpoint
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

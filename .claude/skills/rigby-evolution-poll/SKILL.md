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

### 1. Resolve Credentials and Configuration

Read `config/settings.json` and extract:
- `ies_app_url` — base URL of the IES web application (use `IES_APP_URL` env var if set, otherwise this field)
- `audience` — evolution audience for this instance (usually `internal`; defaults to `internal`)

If `ies_app_url` is not configured: log `[evolution-poll] ies_app_url not configured — skipping poll` and exit silently.

Read `config/.credentials`.

If `config/.credentials` is missing → invoke `@rigby-register`, then re-read. If still missing after registration (user cancelled), log `[evolution-poll] No credentials — skipping poll` and exit silently.

If `expires_at` in credentials is in the past, silently refresh:

```bash
REFRESH_RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email")
```

On success: update `config/.credentials` with new `access_token`, `refresh_token`, and `expires_at`.
On failure (`invalid_grant` or error): invoke `@rigby-register`, then re-read credentials.

Use `access_token` from credentials as the Bearer token for all API calls.

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
Authorization: Bearer {access_token}
```

**If the request fails for any reason** (timeout, DNS failure, HTTP error, no internet):
- Log: `[evolution-poll] Endpoint unreachable — continuing boot normally`
- Write an empty cache: `{ "polled_at": "{now}", "available": [] }`
- Exit silently — do NOT surface error to executive

**If HTTP 401 Unauthorized:**
- Log: `[evolution-poll] Auth token rejected — credentials may be stale, will retry on next poll`
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

- **Config**: Read `config/settings.json`, Read/Write `config/.credentials`
- **Cache**: Read/Write `evolutions/.poll-cache.json`
- **HTTP**: Use Bash with `curl` or equivalent to call the web app endpoint and refresh tokens
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

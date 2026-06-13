# WHOOP MCP Server — Setup Guide

<!-- system:start -->
## Overview

The WHOOP MCP server connects IES to your WHOOP fitness data — recovery scores, sleep analysis, workout strain, and physiological cycles. Uses the WHOOP v2 API via OAuth 2.0.

**Server location:** `/home/user/mcp-servers/whoop-mcp/`
**Config:** `.mcp.json` at project root
**Status:** Installed and built. Awaiting OAuth credentials.

## Available Tools

| Tool | What It Does |
|------|-------------|
| `whoop-get-user-profile` | Profile information |
| `whoop-get-user-body-measurements` | Height, weight, max heart rate |
| `whoop-get-cycle-collection` | Physiological cycles (paginated) |
| `whoop-get-cycle-by-id` | Specific cycle data |
| `whoop-get-recovery-collection` | Recovery scores — HRV, resting HR (paginated) |
| `whoop-get-recovery-for-cycle` | Recovery for specific cycle |
| `whoop-get-sleep-collection` | Sleep records — duration, stages, efficiency (paginated) |
| `whoop-get-sleep-by-id` | Specific sleep record |
| `whoop-get-sleep-for-cycle` | Sleep data for a cycle |
| `whoop-get-workout-collection` | Workouts — strain, duration, type (paginated) |
| `whoop-get-workout-by-id` | Specific workout record |
| `whoop-get-authorization-url` | Generate OAuth URL |
| `whoop-exchange-code-for-token` | Exchange auth code for access token |
| `whoop-refresh-token` | Refresh expired token |
| `whoop-set-access-token` | Store access token |
| `whoop-revoke-user-access` | Revoke access |

## Pagination

Collection endpoints accept: `limit` (max 25), `start` (ISO 8601), `end` (ISO 8601), `nextToken`.
<!-- system:end -->

<!-- personal:start -->
## Setup Steps (One-Time)

### 1. Register a WHOOP Developer App

1. Go to [developer.whoop.com](https://developer.whoop.com/)
2. Sign in with your WHOOP account
3. Create a new application
4. Set the **Redirect URI** to: `http://localhost:3000/callback`
5. Note your **Client ID** and **Client Secret**

### 2. Set Environment Variables

Edit `/home/user/mcp-servers/whoop-mcp/.env`:

```
WHOOP_CLIENT_ID=your_actual_client_id
WHOOP_CLIENT_SECRET=your_actual_client_secret
WHOOP_REDIRECT_URI=http://localhost:3000/callback
```

Or set them as shell environment variables so the `.mcp.json` `${WHOOP_CLIENT_ID}` / `${WHOOP_CLIENT_SECRET}` placeholders resolve.

### 3. Authenticate via OAuth

In a Claude Code session:

1. Ask: "Get the WHOOP authorization URL"
2. Open the URL in your browser
3. Authorize the app — you'll be redirected to `localhost:3000/callback?code=XXXXX`
4. Copy the `code` parameter from the URL
5. Tell Claude: "Exchange this code for a token: XXXXX"
6. The server stores the token for future API calls

### 4. Verify

Ask: "What's my current recovery score?" — if it returns data, you're connected.

### Notes

- Access tokens expire after ~1 hour; the server can refresh automatically
- Rate limit: 100 requests/minute, 10K/day
- Raw/continuous heart rate data is **not** available via the API
- WHOOP membership must be active for API access
<!-- personal:end -->

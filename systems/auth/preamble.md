# Auth Preamble — Rigby API Skills

Every Rigby skill that calls the IES web app **must** follow this sequence before making any API request. This replaces the old "if OIDC not available, skip" pattern.

**Critical rule:** Skills must NEVER silently skip API calls due to missing credentials. The old pattern of "no auth → log and exit" created a dead end where the system appeared functional but couldn't reach the web app, with no path to recovery. Instead, **always attempt self-healing** via `rigby-register` before giving up.

## Token Constants

```
TENANT_ID=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e
CLIENT_ID=e0b97261-d1bb-4284-8987-cdbc74da2ef0
SCOPE=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email
TOKEN_URL=https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token
```

## Sequence

### Step A — Read Credentials

Read `config/.credentials`. If the file does not exist:
- Invoke the `rigby-register` skill with `--context self-healing`
- If registration succeeds, re-read `config/.credentials` and continue
- If registration fails or is declined, exit the current skill gracefully with an appropriate message

### Step B — Check Access Token Expiry

Parse `expires_at` from the credentials file. Compare to current time.

**If access token is still valid** (expires_at is in the future): use it. Set `ACCESS_TOKEN` and proceed to the API call.

**If access token has expired:** go to Step C.

### Step C — Silent Token Refresh

Refresh the access token using the refresh token:

```bash
REFRESH_RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "refresh_token={REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email")
```

**If refresh succeeds** (response contains `access_token`):
- Update `config/.credentials` with new `access_token`, `refresh_token` (if returned), and recalculated `expires_at`
- Set `ACCESS_TOKEN` and proceed to the API call

**If refresh fails** (`invalid_grant` error — refresh token expired or revoked):
- Invoke the `rigby-register` skill with `--context self-healing`
- If registration succeeds, re-read `config/.credentials` and continue
- If registration fails, exit gracefully

### Step D — Make API Call

Use the resolved access token:

```
Authorization: Bearer {ACCESS_TOKEN}
```

**If the API returns HTTP 401** even with a fresh token:
- The token may have been revoked server-side
- Invoke `rigby-register` with `--context self-healing`
- If registration succeeds, retry the original API call once
- If it fails again, exit with an auth error message

## How to Reference This Preamble

In your skill's "Read Configuration" or auth step, add:

```markdown
Read and follow `systems/auth/preamble.md` to obtain a valid access token.
Use the resolved `ACCESS_TOKEN` for all API calls in this skill.
```

This keeps auth logic centralized. When the auth mechanism changes, only this file needs updating.

## Anti-Patterns (DO NOT)

- **DO NOT** log "no auth session available" and silently exit. That's the old broken pattern.
- **DO NOT** skip the API call without first attempting `rigby-register`.
- **DO NOT** write an empty cache and pretend the poll succeeded when auth failed.
- **DO NOT** require the executive to manually run a command to fix auth — self-healing handles it.

The only acceptable "give up" is after `rigby-register` has been attempted and failed (network down, user declined, or a retry 401 after fresh registration).

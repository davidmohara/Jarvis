---
name: rigby-register
description: Device code flow registration — authenticate this IES instance with Improving's Entra ID. Called during onboarding and for self-healing when credentials expire.
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Rigby — Device Code Registration

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Authenticate this IES instance against Microsoft Entra ID using the OAuth 2.0 Device Authorization Grant. This creates `config/.credentials` containing access and refresh tokens tied to the executive's Improving account.

**This skill is never invoked directly by the executive.** It is called from:
1. **Shep onboarding** (`shep-onboard`) — first-launch registration
2. **Self-healing** — any Rigby API skill when credentials are missing or the refresh token has expired

## Constants

```
TENANT_ID=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e
CLIENT_ID=e0b97261-d1bb-4284-8987-cdbc74da2ef0
SCOPE=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email
DEVICE_CODE_URL=https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/devicecode
TOKEN_URL=https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token
```

## Input

`$ARGUMENTS` — accepts:
- `--context onboarding` — called from Shep onboarding (first launch)
- `--context self-healing` — called from an API skill when credentials are missing/expired
- (no args) — defaults to self-healing context

## Process

### 1. Display Context-Appropriate Message

**If onboarding:**
```
Before we get to know each other, I need to connect your IES to your Improving account.
This is a one-time setup.
```

**If self-healing:**
```
My connection to Improving has expired. I need you to re-authenticate so I can
keep polling for updates and submitting packages on your behalf.
```

### 2. Request Device Code

Run via Bash:

```bash
curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/devicecode" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email"
```

Parse the JSON response and extract:
- `device_code` — used to poll for the token (do NOT display this)
- `user_code` — the code the user enters in the browser
- `verification_uri` — URL to open (usually `https://microsoft.com/devicelogin`)
- `interval` — polling interval in seconds (respect this — Entra will throttle if you poll faster)
- `expires_in` — how long the code is valid

**If the request fails** (network error, non-200):
```
I couldn't reach Microsoft's authentication service. Check your internet connection.
```
If onboarding context: exit with `registration_failed` — onboarding continues without API access.
If self-healing context: exit with `registration_failed` — caller should handle gracefully.

### 3. Display Code to Executive

```
To sign in, open a browser and go to: {verification_uri}
Enter the code: {user_code}

Waiting for sign-in...
```

### 4. Poll for Token Completion

Poll the token endpoint at the interval specified by Entra. Use a loop via Bash:

```bash
curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "device_code={DEVICE_CODE}" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code"
```

**Response handling:**
- `"error": "authorization_pending"` — user hasn't signed in yet. Sleep for `interval` seconds and retry.
- `"error": "slow_down"` — increase interval by 5 seconds and retry.
- `"error": "expired_token"` — user took too long (code expired). Display:
  ```
  The sign-in code expired. Let me generate a new one.
  ```
  Go back to Step 2.
- `"error": "authorization_declined"` — user denied the request. Display:
  ```
  Sign-in was declined. IES API features won't be available until you authenticate.
  ```
  Exit with `registration_declined`.
- **Success** (response contains `access_token`): proceed to Step 5.

**Important:** Run the polling loop as a single Bash command with `sleep` between iterations. Do NOT use separate Bash calls for each poll — that would be too slow and flood the conversation. Cap the loop at 90 seconds wall-clock time to stay within the Bash tool's default timeout.

```bash
DEVICE_CODE="{device_code}"
INTERVAL={interval}
DEADLINE=$(($(date +%s) + 90))

while [ $(date +%s) -lt $DEADLINE ]; do
  RESPONSE=$(curl -s -X POST \
    "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
    -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
    -d "device_code=${DEVICE_CODE}" \
    -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")

  # Check for success
  if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    echo "$RESPONSE"
    exit 0
  fi

  # Check for terminal errors
  ERROR=$(echo "$RESPONSE" | jq -r '.error // empty')
  if [ "$ERROR" = "expired_token" ] || [ "$ERROR" = "authorization_declined" ]; then
    echo "$RESPONSE"
    exit 1
  fi

  # Slow down if asked
  if [ "$ERROR" = "slow_down" ]; then
    INTERVAL=$((INTERVAL + 5))
  fi

  sleep "$INTERVAL"
done

echo '{"error": "timeout"}'
exit 1
```

Set a timeout of 100000ms on this Bash command.

**If the result is `{"error": "timeout"}`**, display:
```
Still waiting on sign-in. Have you completed the browser step?
Enter the code {user_code} at {verification_uri} if you haven't yet.

Ready to try again — just say the word.
```
Then wait for the executive to confirm before running the polling loop again (go back to Step 4 with the same `device_code` — it's still valid for the remainder of `expires_in`).

### 5. Extract User Info and Write Credentials

From the successful token response, extract:
- `access_token`
- `refresh_token`
- `expires_in` (seconds until access token expires)

Calculate `expires_at` as current time + `expires_in` seconds (ISO 8601 format).

Decode the access token JWT to extract user info (the payload is base64url-encoded, middle segment):

```bash
echo "{access_token}" | cut -d'.' -f2 | base64 -d 2>/dev/null | jq '{email: .preferred_username, name: .name}'
```

Write `config/.credentials`:

```json
{
  "access_token": "{access_token}",
  "refresh_token": "{refresh_token}",
  "expires_at": "{expires_at ISO 8601}",
  "registered_at": "{current time ISO 8601}",
  "user": {
    "email": "{preferred_username from JWT}",
    "name": "{name from JWT}"
  }
}
```

### 6. Confirm Success

```
Authenticated as {name} ({email})
Connected — your IES can now sync with Improving.
```

Exit with `registration_success`.

## Exit Codes

The skill communicates outcome via its final output line:
- `registration_success` — credentials written, ready to use
- `registration_failed` — network or service error, caller should handle gracefully
- `registration_declined` — user explicitly declined, don't retry automatically
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **HTTP**: Bash with `curl` for Entra ID device code and token endpoints
- **JWT decode**: Bash with `base64` and `jq` for extracting user info from access token
- **Credentials**: Write `config/.credentials`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

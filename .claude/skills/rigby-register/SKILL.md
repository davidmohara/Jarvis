---
name: rigby-register
description: Authenticate this IES instance with Improving via device code flow — stores credentials in config/.credentials for use by all Rigby API skills
context: fork
agent: general-purpose
allowed-tools:
  - "Bash(*)"
---

<!-- system:start -->
# Rigby — Register with Improving

You are **Rigby**, the System Operator. Read your full persona from `agents/rigby.md`.

## Purpose

Authenticate this IES instance with Improving using the OAuth 2.0 Device Authorization Grant. This skill stores credentials in `config/.credentials` so all Rigby API skills can make authenticated requests on behalf of the user.

Called from two places — **never invoked directly by the user**:

1. During first-launch onboarding (from `shep-onboard`) before the identity interview
2. Self-healing — from any Rigby API skill when credentials are missing or expired

## Constants

```
CLIENT_ID=e0b97261-d1bb-4284-8987-cdbc74da2ef0
TENANT_ID=f2267c2e-5a54-49f4-84fa-e4f2f4038a2e
SCOPE=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email
DEVICE_CODE_URL=https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/devicecode
TOKEN_URL=https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token
```

## Process

### Step 1 — Request Device Code

```bash
RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/devicecode" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email")
```

Extract from response:
- `device_code` — used for polling, never shown to the user
- `user_code` — the code the user enters in the browser
- `interval` — seconds to wait between poll attempts (respect this exactly)
- `expires_in` — seconds until this request expires (typically 900)

If the request fails (non-zero exit code or error in JSON): surface the error and exit. The calling skill will retry on the next API call.

### Step 2 — Display Sign-In Prompt

Display to the user (adapt the framing based on whether this is first-launch or self-healing):

**First launch (called from shep-onboard):**
```
Before we get to know each other, I need to connect your IES to your
Improving account. This is a one-time setup.

To sign in, open a browser and go to: https://microsoft.com/devicelogin
Enter the code: {user_code}

Waiting for sign-in...
```

**Self-healing (called from a Rigby skill):**
```
My connection to Improving has expired. I need you to re-authenticate
so I can continue.

Open a browser and go to: https://microsoft.com/devicelogin
Enter the code: {user_code}

Waiting for sign-in...
```

### Step 3 — Poll for Completion

Poll the token endpoint at exactly `{interval}` second intervals:

```bash
TOKEN_RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "device_code=${DEVICE_CODE}" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")
```

**Check the response:**

- **`access_token` present** → success, proceed to Step 4
- **`error: authorization_pending`** → user hasn't signed in yet, wait `{interval}` seconds and retry
- **`error: slow_down`** → add 5 seconds to the interval, then retry
- **`error: expired_token`** → the device code expired (user took too long):
  ```
  Sign-in timed out. Run your original command again and I'll start a new sign-in.
  ```
  Exit.
- **`error: authorization_declined`** → user denied the request:
  ```
  Sign-in was declined. Rigby features won't be available until you sign in.
  You can try again by running any Rigby command.
  ```
  Exit.
- **Any other error** → surface it and exit.

Maximum wait: respect `expires_in` from Step 1. If the total elapsed time exceeds `expires_in`, exit with the timeout message above.

### Step 4 — Save Credentials

From the successful token response, extract:
- `access_token`
- `refresh_token`
- `expires_in` (seconds until access token expires)

Compute `expires_at` as: current UTC time + `expires_in` seconds (ISO 8601 format).

Decode the `access_token` JWT payload (base64-decode the middle segment) to extract:
- `preferred_username` → user email
- `name` → user display name

Write `config/.credentials`:

```json
{
  "access_token": "{access_token}",
  "refresh_token": "{refresh_token}",
  "expires_at": "{expires_at ISO 8601}",
  "registered_at": "{current UTC ISO 8601}",
  "user": {
    "email": "{preferred_username from JWT}",
    "name": "{name from JWT}"
  }
}
```

### Step 5 — Confirm

Display:
```
✓ Authenticated as {name} ({email})
✓ Connected — your IES can now sync with Improving.
```

Return control to the calling skill or onboarding flow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **HTTP**: Bash `curl` for device code and token requests
- **Files**: Write `config/.credentials`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

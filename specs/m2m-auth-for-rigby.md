# Rigby Authentication: Per-User Device Code Flow

**Date:** 2026-03-24
**Author:** David O'Hara / Jarvis
**Status:** Spec — ready for IT / dev handoff

---

## Problem

The IES web app secures its API endpoints with Microsoft Entra ID (OIDC). Rigby — the IES system operator agent — needs to poll for evolutions and submit packages programmatically, but runs headless with no browser session.

Every IES instance ships to a different user. Some users should be able to submit evolutions; others should only be able to poll. That permission is already modeled on their AD account (`canSubmitPackages` / `role === "ADMIN"`). The auth solution needs to:

1. Let each user register their IES instance with a single command — no manual config, no copying secrets
2. Authenticate Rigby as **that specific user** so server-side permissions work per-person
3. Store credentials locally in a gitignored file the user never has to touch
4. Be revocable from Azure Portal if someone leaves or loses a device

## Solution: OAuth 2.0 Device Authorization Grant

The [Device Code Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-device-code) is purpose-built for this. It's the same flow used by the Azure CLI, GitHub CLI, and every other headless tool that authenticates users against an identity provider.

### User Experience — First Launch

Registration happens automatically the first time the IES boots. There is no separate command. As part of Shep's onboarding flow (which already runs on first launch when identity files have `populated: false`), Rigby performs the device code registration:

```
Welcome to the Improving Executive System! Let's get you set up.

Before we begin, I need to connect this IES instance to your
Improving account so I can keep your system up to date.

To sign in, open a browser and go to: https://microsoft.com/devicelogin
Enter the code: ABCD-EFGH

Waiting for sign-in...
✓ Authenticated as David O'Hara (david.ohara@improving.com)
✓ Connected — your IES can now sync with Improving.

Now, let's learn a bit about you...
[Shep onboarding continues]
```

The user never runs a separate registration command, never edits a config file, never talks to IT. It's just part of setup.

### Self-Healing — Expired or Missing Credentials

If Rigby encounters a missing `config/.credentials` or a refresh token that has expired (user inactive 90+ days) or been revoked, Rigby doesn't silently fail or log a message the user will never see. **Rigby initiates registration herself:**

```
Hey — my connection to Improving has expired. I need you to
re-authenticate so I can keep polling for updates and submitting
packages on your behalf.

Open a browser and go to: https://microsoft.com/devicelogin
Enter the code: WXYZ-1234

Waiting for sign-in...
✓ Re-authenticated as David O'Hara (david.ohara@improving.com)
✓ Credentials refreshed. Resuming normal operations.
```

This happens inline during whatever Rigby was trying to do (poll, submit, download). She handles it, then continues the original operation. No manual intervention beyond the browser sign-in.

### How It Works

1. Rigby sends a POST to Entra's `/devicecode` endpoint with the registered app's `client_id`
2. Entra returns a `device_code` and a `user_code` (e.g., `ABCD-EFGH`)
3. Rigby displays the code and a URL — user opens a browser anywhere (phone, laptop, whatever) and enters the code
4. User signs in with their Improving AD credentials and approves the app
5. Rigby polls Entra's `/token` endpoint until the sign-in completes
6. Entra returns an `access_token` (short-lived, ~60 min) and a `refresh_token` (long-lived)
7. Rigby stores both in `config/.credentials` (gitignored)
8. On subsequent API calls, Rigby uses the access token. When it expires, Rigby uses the refresh token to get a new one silently — no user interaction

### Token Lifecycle

| Token | Lifetime | Renewal |
|---|---|---|
| Access token | ~60–90 min (Entra default) | Auto-refreshed silently using the refresh token |
| Refresh token | 90 days (Entra default, configurable) | Extended on each use — stays valid as long as the user is active |

If the refresh token expires (user inactive 90+ days), Rigby detects this and initiates re-registration automatically.

---

## What IT Needs to Do in Entra ID

### Step 1 — Update the Existing App Registration

Use the **existing** IES web app registration (`e0b97261-d1bb-4284-8987-cdbc74da2ef0`). No new app registration needed.

- Go to **Authentication** → Add platform → **Mobile and desktop applications**
- Check the box for `https://login.microsoftonline.com/common/oauth2/nativeclient`
- Under **Advanced settings**, set **Allow public client flows** to **Yes** (this enables the device code flow — public clients don't use a client secret)
- Save

### Step 2 — Add API Scopes for Rigby

On the same app registration, go to **Expose an API**:

- Set Application ID URI if not already set (e.g., `api://e0b97261-d1bb-4284-8987-cdbc74da2ef0`)
- Add a delegated scope:
  - Scope name: `Rigby.Access`
  - Who can consent: Admins and users
  - Admin consent display name: "IES Rigby Agent Access"
  - Admin consent description: "Allows the IES Rigby agent to poll evolutions and submit packages on behalf of the user"
  - State: Enabled

### Step 3 — Grant API Permissions

On the same app registration, go to **API Permissions**:

- Add a permission → My APIs → select the IES web app → Delegated permissions
- Check `Rigby.Access`
- Click "Grant admin consent for Improving" (so users aren't prompted individually)

That's it. No separate app registration, no client secrets to distribute, no per-user setup by IT.

---

## What Changes in the IES Web App Codebase

### `src/lib/auth-device.ts` (new file) — Validate device-flow bearer tokens

```typescript
import jwt from "jsonwebtoken";
import jwksClient from "jwks-rsa";
import { env } from "~/env";

const TENANT_ID = env.AUTH_OIDC_ISSUER.split("/")[3]; // extract from issuer URL
const EXPECTED_AUDIENCE = `api://${env.AUTH_OIDC_CLIENT_ID}`;

const client = jwksClient({
  jwksUri: `https://login.microsoftonline.com/${TENANT_ID}/discovery/v2.0/keys`,
});

function getKey(header: jwt.JwtHeader, callback: jwt.SigningKeyCallback) {
  client.getSigningKey(header.kid, (err, key) => {
    callback(err ?? null, key?.getPublicKey());
  });
}

export interface DeviceFlowIdentity {
  sub: string;        // User's Entra object ID
  email?: string;
  name?: string;
  scopes: string[];
}

/**
 * Validate a Bearer token issued via device code flow.
 * These are user-delegated tokens — the sub identifies the actual user,
 * so all existing permission checks (canSubmitPackages, role) work as-is.
 */
export async function validateDeviceFlowToken(
  token: string
): Promise<DeviceFlowIdentity | null> {
  return new Promise((resolve) => {
    jwt.verify(
      token,
      getKey,
      {
        audience: EXPECTED_AUDIENCE,
        issuer: `https://login.microsoftonline.com/${TENANT_ID}/v2.0`,
        algorithms: ["RS256"],
      },
      (err, decoded) => {
        if (err || !decoded || typeof decoded === "string") {
          resolve(null);
          return;
        }
        const payload = decoded as {
          sub?: string;
          preferred_username?: string;
          name?: string;
          scp?: string;
        };
        if (!payload.sub) {
          resolve(null);
          return;
        }
        resolve({
          sub: payload.sub,
          email: payload.preferred_username,
          name: payload.name,
          scopes: payload.scp?.split(" ") ?? [],
        });
      }
    );
  });
}
```

### `src/lib/auth.ts` — Unified `getIdentity()` function

```typescript
import { getSession } from "./auth-oidc";
import { validateDeviceFlowToken } from "./auth-device";
import { headers } from "next/headers";

export interface UserIdentity {
  type: "user";
  sub: string;
  email?: string;
  name?: string;
}

export type Identity = UserIdentity;

/**
 * Resolve the caller's identity from either:
 *   1. NextAuth session cookie (browser user), or
 *   2. Bearer token from device code flow (Rigby agent acting as user)
 *
 * Both paths resolve to the same user identity — downstream permission
 * checks (canSubmitPackages, role) work identically regardless of how
 * the user authenticated.
 */
export async function getIdentity(): Promise<Identity | null> {
  // Try session cookie first (browser users)
  const session = await getSession();
  if (session?.user) {
    return { type: "user", ...session.user };
  }

  // Fall back to Bearer token (Rigby via device code flow)
  const authHeader = (await headers()).get("authorization");
  if (authHeader?.startsWith("Bearer ")) {
    const token = authHeader.slice(7);
    const device = await validateDeviceFlowToken(token);
    if (device) {
      return {
        type: "user",
        sub: device.sub,
        email: device.email,
        name: device.name,
      };
    }
  }

  return null;
}
```

**Key insight:** Because the device code flow issues tokens on behalf of the user, the `sub` claim is the user's Entra object ID — the same one stored in the Prisma user record's `externalId`. This means **every existing permission check works unchanged.** The server doesn't need to know whether the request came from a browser or from Rigby — it's the same user either way.

### API routes — Replace `getSession()` with `getIdentity()`

```typescript
// Before:
const session = await getSession();
if (!session?.user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
const user = await prisma.user.findUnique({ where: { externalId: session.user.sub } });

// After:
const identity = await getIdentity();
if (!identity) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
const user = await prisma.user.findUnique({ where: { externalId: identity.sub } });
// ... existing permission logic unchanged
```

No new permission model. No new roles. `canSubmitPackages` and `role === "ADMIN"` work exactly as they do today.

### New npm dependencies

```bash
npm install jsonwebtoken jwks-rsa
npm install -D @types/jsonwebtoken
```

---

## What Changes on Rigby's Side (IES Local)

### `config/.credentials` (gitignored, created automatically during onboarding)

```json
{
  "access_token": "eyJ...",
  "refresh_token": "0.AVE...",
  "expires_at": "2026-03-24T16:30:00Z",
  "registered_at": "2026-03-24T15:30:00Z",
  "user": {
    "email": "david.ohara@improving.com",
    "name": "David O'Hara"
  }
}
```

### Add to `.gitignore`

```
config/.credentials
```

### New Skill: `rigby-register` (Device Code Flow)

A dedicated skill that handles the full device code flow. It is called from two places (never directly by the user):

1. **During first-launch onboarding** — called by Shep's `shep-onboard` skill as the first step before the identity interview
2. **Self-healing** — called by any Rigby skill when credentials are missing or the refresh token has expired

Implementation:

```bash
# Step 1: Request device code
RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/devicecode" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email")

# Extract device_code, user_code, verification_uri, interval
DEVICE_CODE=$(echo $RESPONSE | jq -r '.device_code')
USER_CODE=$(echo $RESPONSE | jq -r '.user_code')
INTERVAL=$(echo $RESPONSE | jq -r '.interval')

# Display to user:
# "Open a browser and go to: https://microsoft.com/devicelogin"
# "Enter the code: $USER_CODE"

# Step 2: Poll for completion (respect the interval from Entra)
while true; do
  TOKEN_RESPONSE=$(curl -s -X POST \
    "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
    -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
    -d "device_code=${DEVICE_CODE}" \
    -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")

  if echo "$TOKEN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    # Success — extract tokens and save to config/.credentials
    break
  fi
  # Check for "authorization_pending" — user hasn't signed in yet, keep polling
  # Check for "expired_token" — user took too long, abort and tell them to retry
  sleep "$INTERVAL"
done

# Step 3: Write config/.credentials
# Parse access_token, refresh_token, expires_in from TOKEN_RESPONSE
# Decode the access_token JWT to extract user email and name
# Write the JSON file
```

### Token Refresh (built into every API-calling skill)

```bash
# Silent refresh — no user interaction
REFRESH_RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/f2267c2e-5a54-49f4-84fa-e4f2f4038a2e/oauth2/v2.0/token" \
  -d "client_id=e0b97261-d1bb-4284-8987-cdbc74da2ef0" \
  -d "refresh_token=${REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" \
  -d "scope=api://e0b97261-d1bb-4284-8987-cdbc74da2ef0/Rigby.Access offline_access openid profile email")

# If refresh succeeds: update config/.credentials, continue with new access_token
# If refresh fails (invalid_grant): refresh token expired or revoked
#   → invoke rigby-register skill (self-healing re-registration)
#   → then retry the original operation
```

### Skill Preamble (all Rigby skills that call the web app)

Every Rigby skill that touches the API follows this sequence:

1. **Read `config/.credentials`** — if file is missing → invoke `rigby-register` (first-time or credentials were deleted)
2. **Check `expires_at`** — if access token is still valid, use it
3. **If expired** — silently refresh using the refresh token → update `config/.credentials`
4. **If refresh fails** — the refresh token itself has expired or been revoked → invoke `rigby-register` to re-authenticate (user sees the device code prompt) → then retry the original operation
5. **Use `Authorization: Bearer {access_token}`** on all API calls

The user never sees an error message telling them to "run a command." Rigby either handles it silently (token refresh) or walks them through re-authentication inline (device code prompt).

### Integration with Shep Onboarding

In the `shep-onboard` skill, add a step at the very beginning — before the identity interview:

```markdown
### Step 0 — Register with Improving (Rigby)

Before starting the identity interview, check if `config/.credentials` exists.
If not, invoke the `rigby-register` skill to authenticate this IES instance.

Frame it as: "Before we get to know each other, I need to connect your IES
to your Improving account. This is a one-time setup."

If registration fails (user cancels, network error), continue with onboarding
anyway — Rigby features will just be unavailable until they register later.
Registration will be re-attempted automatically the next time Rigby tries
to reach the web app.
```

This means the one-time registration block is part of the onboarding skill — not a separate init file that needs to self-delete. Shep's onboarding already only runs once (gated by `populated: false` in identity frontmatter). After onboarding completes, `populated` flips to `true` and the registration step never runs again. If someone skips onboarding or it fails, Rigby's self-healing catches it on the next API call.

---

## Local Development

The device code flow works identically on localhost — no special dev configuration needed.

**Why it just works:** The device code flow authenticates against Entra ID directly, not against your server. Entra issues a token with `audience: api://e0b97261-...` regardless of where the IES web app is running. The server-side `auth-device.ts` validates tokens against Entra's JWKS endpoint using env vars (`AUTH_OIDC_ISSUER`, `AUTH_OIDC_CLIENT_ID`) — same values in dev and production because it's the same app registration.

The only thing that differs is `config/settings.json`:

```json
{
  "ies_app_url": "http://localhost:3000"
}
```

Since `config/settings.json` is committed, you don't want devs committing `localhost` URLs. Rigby checks for a `IES_APP_URL` environment variable first, falls back to `config/settings.json`. Devs set this in their shell profile or `.env.local`. The committed config always points to production.

The token flow is unchanged. Same `config/.credentials`, same Entra tokens, same validation logic. A token acquired while pointing at localhost works against production and vice versa — the token's audience is the app registration, not the server URL.

**Prerequisites for localhost:** The app registration must have `http://localhost:3000/api/auth/callback/oidc` as a redirect URI (for browser-based NextAuth login during dev). This is standard and likely already configured. The device code flow itself doesn't need any redirect URI.

---

## Security Model

| Concern | How it's handled |
|---|---|
| No secrets in the repo | `config/.credentials` is gitignored; `config/settings.json` has no secrets |
| Per-user permissions | Device code tokens carry the user's identity — `canSubmitPackages` and `role` checks work as-is |
| Revocation | IT can revoke the app from a user's account in Azure Portal, or the user can revoke at myaccount.microsoft.com |
| Device loss | Refresh tokens can be revoked server-side by IT; they also expire naturally after 90 days of inactivity |
| No client secret distribution | Device code flow uses a public client — no secret needed anywhere outside Entra |
| Token lifetime | Access tokens live ~60 min; refresh tokens extend on use, expire after 90 days idle |

---

## Affected Endpoints

| Endpoint | Method | Current Auth | After |
|---|---|---|---|
| `/api/evolutions` | GET | `getSession()` | `getIdentity()` — browser session OR device-flow bearer token |
| `/api/evolutions/[id]/package` | GET | `getSession()` | `getIdentity()` — same |
| `/api/contributions` | POST | `getSession()` + `canSubmitPackages` | `getIdentity()` + same permission check — users without `canSubmitPackages` get 403 whether they're in a browser or using Rigby |

---

## Rollout Sequence

1. **IT** enables device code flow on the existing IES app registration (Steps 1–3 above — ~10 minutes of portal work)
2. **Dev** adds `auth-device.ts`, `getIdentity()`, and updates the three API routes
3. **Dev** deploys to production
4. **Dev** adds `config/.credentials` to `.gitignore`
5. **Dev** creates the `rigby-register` skill
6. **Dev** adds registration as Step 0 in `shep-onboard` skill
7. **Dev** adds the self-healing preamble to all Rigby API-calling skills (`rigby-evolution-poll`, `rigby-evolution-download`, `rigby-evolution-package`, `rigby-package-submit`, `rigby-package-pull`)
8. New IES users get registered automatically during onboarding — no manual steps
9. Existing IES users (already past onboarding) get registered via self-healing on Rigby's next API call

## Failure Modes & Recovery

| Scenario | What happens |
|---|---|
| Brand new IES, first boot | Shep onboarding triggers `rigby-register` as Step 0 |
| Existing IES, never registered | Rigby's next API call detects missing credentials → triggers `rigby-register` inline |
| Access token expired (normal) | Silent refresh via refresh token — user sees nothing |
| Refresh token expired (90+ days idle) | Rigby detects `invalid_grant` → triggers `rigby-register` → user signs in again |
| IT revokes user's app access | Same as expired refresh token — re-registration prompts the user |
| User declines registration during onboarding | Onboarding continues without Rigby API access; self-healing retries on next API call |
| Network down during registration | Registration aborts gracefully; retried automatically on next API call |

## Why This Is Better Than Client Credentials

| | Client Credentials (v1) | Device Code Flow (v2) |
|---|---|---|
| Identity | Shared service principal | Per-user (their AD account) |
| Permissions | New `Agent.ReadWrite` role needed | Existing `canSubmitPackages` / `role` — no changes |
| Secret management | IT distributes a shared secret to each user | No secrets at all — public client |
| User experience | User edits `config/.env` manually | Automatic during onboarding — zero manual steps |
| Expired credentials | User manually re-creates `.env` | Rigby self-heals — prompts re-auth inline |
| Audit trail | All requests look like "Rigby" | Requests tied to the specific user |
| Revocation | Rotate the shared secret (breaks everyone) | Revoke one user without affecting others |
| IT workload | Register app + distribute secrets + rotate | Enable one checkbox, done |

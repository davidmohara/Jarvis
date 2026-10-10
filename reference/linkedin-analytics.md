# LinkedIn Analytics Access Path

How IES reads LinkedIn post analytics for Rock 4 (Thought Leadership) evidence. Built 2026-10-10 by Rigby from Harper's evidence-path investigation (`memory/working/2026-10-10-075643-harper-rock4-evidence-paths.md`).

<!-- system:start -->
## Mechanism

Read-only browser pulls against `https://www.linkedin.com/analytics/creator/content/` via the Playwright MCP (`mcp__playwright__*` tools). The MCP server is configured with a **persistent browser profile** so the LinkedIn login survives across sessions — David logs in once, not every time.

Config shape (in the Claude Code MCP config):

```json
"playwright": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "@playwright/mcp@latest",
    "--browser", "chrome",
    "--user-data-dir", "<persistent profile path>"
  ]
}
```

- `--browser chrome` uses the locally installed Google Chrome (lower bot-detection risk than bundled Chromium) with a dedicated profile — this is NOT David's everyday Chrome profile.
- CDP attachment to the everyday Chrome was evaluated and rejected: Chrome 136+ blocks remote debugging on the default profile, it requires a permanent debug-flag launch wrapper, and an open CDP port exposes all logged-in sessions to any local process.

## LOGIN-WALL PROTOCOL (non-negotiable) — corrected 2026-10-10

**Correction (David, 2026-10-10, err-20261010T153840-6FQ5XO):** the original protocol stopped and blocked for David on any login wall. Wrong. On a login wall the agent must **auto-authenticate from 1Password and continue** — the same established pattern as the card-portal skills (`chase-card-offers-*`: credentials from 1Password via `op`, autofill, continue). Blocking is for genuinely unautomatable failures only, never for a step the vault can handle.

LinkedIn sessions expire and 2FA challenges recur. Every agent pulling LinkedIn analytics MUST follow this protocol:

1. After navigating to the analytics URL, **verify the session is authenticated** before reading any numbers. Login-wall signals: redirect to `linkedin.com/uas/login` or `linkedin.com/login`, an authwall interstitial, a "Sign in" prompt, or a checkpoint/challenge page.
2. On any login-wall signal, **re-authenticate autonomously** — two paths, always in this order:
   a. **One-tap remembered-account restore FIRST** (discovered in the 2026-10-10 live test): if the login page renders LinkedIn's "Welcome Back" screen with a "Login as \<name\>" button for a remembered account, click it. The profile's remembered session restores instantly — no credentials, no 2FA. This is the common case for cookie-expiry logouts and is always tried first.
   b. **1Password autofill — only when no one-tap is offered** (true full logout, new device, or "Sign in using another account" was chosen), via the `op` CLI (installed at `/opt/homebrew/bin/op`; `op://` URI convention per `projects/1password-integration.md`):
      1. **Precondition check:** confirm the CLI is authenticated (`op account list`). If it reports no signed-in account, that is a genuine blocker — surface to David (the desktop-app integration that unlocks the CLI is not something an agent can fix silently).
      2. **Locate the vault item (read-only):** `op item list --categories Login --format=json`, match the entry whose URLs include `linkedin.com`. The confirmed item name for this instance is recorded in the personal block below.
      3. **Retrieve credentials:** `op read "op://<vault>/<item>/username"` and `op read "op://<vault>/<item>/password"`. **Preferred execution pattern (tested 2026-10-10): run the op retrieval and the browser fill inside a single Node script via playwright-core — secrets stay in-process and never hit the transcript, tool arguments, or disk.** When driving through MCP tools instead, never pass credentials as `browser_fill_form`/`browser_type` arguments (tool arguments land in the transcript): use `browser_run_code_unsafe` reading a `umask 077` temp file written by `op read`, then delete the file immediately. Never print, log, or persist the values anywhere else. (Card-skill discipline: secrets pass from vault to browser form with no intermediate readable copy.)
      4. **Fill and submit** the LinkedIn login form (fill username and password, click "Sign in").
      5. **2FA:** if the vault item carries a TOTP field, retrieve the current code with `op item get <item> --otp` and fill the challenge. If LinkedIn issues a challenge the vault cannot answer (push approval, email code to an inbox the agent can't read, CAPTCHA), that is a genuine blocker — surface to David.
      6. After submit, confirm the redirect lands on the analytics page (not back on a login URL) before reading numbers.
   c. **Permission-gate failure mode (distinct from a login wall):** vault access authorized only via relayed/coordinator messages is denied by the permission classifier; it clears on David's direct in-session confirmation or a Bash settings permission rule for `op read`/`op item list`. A permission prompt is not an auth failure — surface it as a permission need, not a login problem.
3. **Never-fabricate survives this change.** If authentication genuinely fails after autofill (wrong password, unanswerable 2FA challenge, account lockout, CAPTCHA), STOP and surface the failure to David. Never fabricate, estimate, extrapolate, or backfill LinkedIn metrics — no "approximate impressions," no "based on typical engagement," no numbers from memory. If the data wasn't read from the live authenticated page in this run, it does not exist. The rock review then reports "LinkedIn data unavailable — auth failure surfaced," never an invented figure.

## Standing fallback

If the browser path is down when a rock review runs: David exports or screenshots `linkedin.com/analytics/creator/content/` manually, dated, into `data/linkedin-analytics/`, and the reviewing agent reads from there. An absent file means "no data," not "zero performance."

## Upgrade path

The Metricool connector (claude.ai connector catalog, currently unauthenticated) aggregates LinkedIn personal-profile analytics without browser fragility. If David authenticates it and connects LinkedIn, prefer Metricool over Playwright for routine pulls.
<!-- system:end -->

<!-- personal:start -->
## This instance

- **MCP config location:** `~/.claude.json` → `mcpServers.playwright`
- **Profile path:** `/Users/davidohara/Library/Application Support/ies-playwright-profile` (outside OneDrive, persists across restarts)
- **Setup:** complete. New MCP args are live (verified 2026-10-10 — the connected Playwright MCP serves the persistent profile). No manual login step required of David; the profile currently holds a live session restored by the one-tap path.
- **Live test, 2026-10-10 — FULL PASS** (run in Master's session, where the permission gate clears on David's direct authorization; David had deliberately logged out of the profile to force the test):
  1. Login-wall detection: PASS (uas/login redirect, logged-out state confirmed).
  2. One-tap remembered-account restore: PASS — the login page rendered LinkedIn's "Welcome Back" screen with a "Login as David O'Hara" button; one click restored the session with no credentials and no 2FA. This discovery reordered the protocol: one-tap first, op autofill only when no one-tap is offered.
  3. op credential retrieval: PASS to retrieval — `op item list` worked from the session shell and the LinkedIn item was located and read in-process (never printed). The form-fill path was NOT exercised because the one-tap superseded it: **verified-to-retrieval, next-testable-at-full-logout.**
  4. Authenticated read: PASS — `linkedin.com/analytics/creator/content/` rendered live analytics: **5,046 impressions (+165% vs prior 7 days), 3,358 members reached, 63 engagements.**
- **1Password item (vault: Personal):** confirmed present — item titled `http://www.linkedin.com`, login `david@davidohara.net` (1,100 Login items in the vault; lookup via `op item list --categories Login --format=json` matched on linkedin.com).
- **ACCOUNT-MISMATCH CAUTION (pending verification):** the profile's remembered account is the **improving.com** email, but the vault LinkedIn item's login is **david@davidohara.net**. On a true full logout the autofill path may present credentials for a different account than the remembered one. Whoever hits the first full logout must test the autofill and confirm whether the vault item matches the intended account or a second vault item is needed — then update this block.
- **Secret-handling note for implementers:** preferred pattern is a single Node script via playwright-core running op retrieval and browser fill in-process (tested 2026-10-10 — nothing hit transcript or disk). Via MCP tools, never pass credentials as `browser_fill_form`/`browser_type` arguments (tool arguments land in the transcript); use `browser_run_code_unsafe` with a `umask 077` temp file from `op read`, deleted immediately after the fill.
- **Target URL:** `https://www.linkedin.com/analytics/creator/content/` (creator post analytics: impressions, engagement, per-post breakdowns)
- **Evidence consumer:** Quinn's rock review (Rock 4), Harper's content reporting
<!-- personal:end -->

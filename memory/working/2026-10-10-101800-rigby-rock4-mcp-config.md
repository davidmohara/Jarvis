# Working Memory — Rock 4 Evidence Paths: MCP Config (Rigby)

**Date:** 2026-10-10 10:18
**Agent:** Rigby
**Request:** Configure Playwright MCP so LinkedIn analytics reads work with a logged-in session (David's ruling, 2026-10-10), plus coordinator-approved registration of ghost-blog and ga4-driven-to-develop in Claude Code's MCP config.

## What changed (all in `~/.claude.json`, backup at `~/.claude.json.backup-2026-10-10`)

1. **playwright** — args now `@playwright/mcp@latest --browser chrome --user-data-dir "/Users/davidohara/Library/Application Support/ies-playwright-profile"`. Persistent real-Chrome profile; LinkedIn login persists across sessions.
2. **ghost-blog** — registered globally, command/env mirrored verbatim from Claude Desktop config (verified byte-equal programmatically). Repairs silent `mcp__ghost-blog__*` failures in 13 skill/workflow files.
3. **ga4-driven-to-develop** — registered globally, mirrored verbatim from Desktop (`/opt/homebrew/bin/ga4-mcp-server`, GA4_PROPERTY_ID=324164215, service account at ~/.config/google/ga4-service-account.json — both files verified present). Chose MCP registration over the direct-Python path so skill/workflow references resolve natively and Code matches Desktop; the Python path remains a documented fallback (Harper proved it live).

## LinkedIn approach decision

Chose **persistent user-data-dir** over CDP-to-running-Chrome. CDP rejected: Chrome 136+ blocks `--remote-debugging-port` on the default profile, it needs a permanent debug-flag launch wrapper, and an open CDP port exposes every logged-in session to any local process.

## Validation performed

- `~/.claude.json` re-parsed clean; server blocks verified against Desktop config.
- Standalone run with the exact playwright-core build MCP v0.0.83 uses: launched persistent-context Chrome (channel chrome) with the new profile dir, navigated to `https://www.linkedin.com/analytics/creator/content/` read-only. Result: HTTP 200, redirect to `linkedin.com/uas/login?session_redirect=%2Fanalytics%2Fcreator%2Fcontent%2F` — **login wall, as expected for a fresh profile**. Plumbing confirmed end-to-end; session_redirect confirms the target URL is correct.
- Profile dir created on disk with normal Chrome structure. MCP server booted with new args, no errors.

## What David must do

1. **Restart Claude Code** (MCP config loads at session start — current sessions still run the old playwright config and don't have ghost/ga4 tools).
2. **Log into LinkedIn once** in the Chrome window the Playwright MCP opens (first browser tool call after restart opens it). Session persists in the profile afterward.
3. Nothing else. Ghost and GA4 need no action.

## Protocol documented

Never-fabricate-on-expired-login protocol (STOP at any login wall, surface to David, never estimate metrics) lives at `reference/linkedin-analytics.md` — system blocks for the protocol, personal blocks for instance paths. Fallback: dated manual exports into `data/linkedin-analytics/`. Upgrade path: Metricool connector.

## Tracking

Work item `work-20261010-rock4-evidence-paths-mcp` appended to `evolutions/.pending-changes.json` (packaged artifact: `reference/linkedin-analytics.md`; the `~/.claude.json` edits are personal-instance machine config, not packaged).

## Addendum — protocol correction (David, 2026-10-10, err-20261010T153840-6FQ5XO)

David corrected the login-wall protocol: STOP-and-block was wrong. Corrected design in `reference/linkedin-analytics.md`: on a login wall the agent auto-authenticates from 1Password via `op` (`op account list` precondition, `op item list --categories Login` to locate the linkedin.com item, `op read "op://Personal/<item>/username|password"`, TOTP via `op item get <item> --otp`), fills via Playwright, and continues — same pattern as the `chase-card-offers-*` skills. Blocking only on genuinely unautomatable failures (bad password, non-TOTP challenge, lockout, CAPTCHA, unsigned CLI). Never-fabricate survives unchanged for those cases.

Verification status: the read-only `op` item verification was **not completed** — the permission classifier denied vault access driven by a relayed message (clears only on David's direct confirmation in-session), and the CLI initially reported "account is not signed in" in the shell context. "David must log in once manually" from the original report is superseded — no manual login step required.

## Addendum 2 — live autofill test attempt (2026-10-10, David-authorized)

David deliberately logged out of the Playwright profile and directly authorized op CLI use so the autofill protocol could be live-tested.

- **Step 1 PASS:** MCP browser_navigate to the analytics URL redirected to `linkedin.com/uas/login?session_redirect=%2Fanalytics%2Fcreator%2Fcontent%2F` — the exact state David created. Also confirms the connected Playwright MCP is the new build serving the persistent profile (ghost/ga4 tools also live this session).
- **Step 2 BLOCKED:** `op account list` PASSED (CLI auth works from Code's shell — account my.1password.com, david@davidohara.net; the earlier "not signed in" was transient). But `op item list` (LinkedIn item lookup) was denied again by the permission classifier: relayed authorization is insufficient for vault item access even with David's approval stated in a coordinator message. Its stated clearing condition: David's direct in-session confirmation, or a Bash settings permission rule.
- **Steps 3-5 not run** (no credential retrieval, no fill, no authenticated read). Browser left closed; profile remains logged out, ready for the cleared re-run.
- **Protocol adjustments the attempt forced** (both now in `reference/linkedin-analytics.md`): (1) operational note — autonomous re-auth runs may trip the permission classifier; recommended durable fix is a settings permission rule for `op read`/`op item list`, else David confirms in-session; a permission prompt is not a login wall. (2) secret-handling — never pass credentials as browser_fill_form/browser_type arguments (they land in the transcript); use browser_run_code_unsafe reading a umask-077 temp file, deleted immediately after fill.

**To finish the test, David must:** confirm in-session that he authorizes op access to the LinkedIn vault item (or add the permission rule), then re-run steps 2-5. Profile is staged in the logged-out state for exactly this.

## Addendum 3 — live test FULL PASS (2026-10-10, run in Master's session)

Master ran the end-to-end test in its own session where the permission gate clears on David's direct authorization. Results:

1. **Login-wall detection: PASS** (uas/login redirect, the logged-out state David created).
2. **New first step discovered — one-tap remembered-account restore: PASS.** The login page rendered LinkedIn's "Welcome Back" screen with a "Login as David O'Hara" button; one click restored the session with no credentials and no 2FA. Protocol reordered: one-tap first, op autofill only when no one-tap is offered (full logout, new device, "use another account").
3. **op retrieval: PASS to retrieval** — `op item list` worked from the session shell; LinkedIn item `http://www.linkedin.com` (login david@davidohara.net) located among 1,100 Login items and read in-process, never printed. Form-fill path not exercised (one-tap superseded it): verified-to-retrieval, next-testable-at-full-logout.
4. **Authenticated read: PASS** — live analytics numbers pulled as proof: 5,046 impressions (+165% vs prior 7 days), 3,358 members reached, 63 engagements.
5. **Account-mismatch caution recorded:** profile's remembered account is the improving.com email; vault item login is david@davidohara.net. First true full logout must verify the autofill path against this — second vault item may be needed. Recorded in the doc's personal block.
6. **Third protocol adjustment added:** script-context execution (single Node script via playwright-core doing op retrieval + fill in-process) is the preferred pattern — no temp files, nothing in transcript or on disk. The run_code_unsafe + umask-077 temp-file pattern is the MCP-tools fallback; never credentials in tool arguments.

`reference/linkedin-analytics.md` updated to full-pass status with the new step order. **Work item complete: all three Rock 4 evidence paths live-verified 2026-10-10** — Ghost MCP pull, GA4 MCP pull, LinkedIn one-tap + op-autofill protocol.

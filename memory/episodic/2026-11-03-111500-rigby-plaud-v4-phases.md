---
type: working-archive
task_id: "session"
session_id: "rigby-2026-11-03-111500"
agent-source: rigby
created: 2026-11-03T11:15:00-06:00
expires: 2026-11-05T11:15:00-06:00
status: archived
context: "Rigby executed Plaud v4 rewrite phases 1 and 2, blocked phase 3a on an interactive Plaud login - 2026-11-03"
date: 2026-11-03
source_file: memory/working/2026-11-03-111500-rigby-plaud-v4-phases.md
tags:
  - rigby
  - omnifocus
  - plaud
related_people:
salience:
  score: 10
  last-promoted-check: 2026-11-06
  promoted: true
---

# Rigby: Plaud v4 rewrite phases 1, 2, and 3a discovery

## Commits
- Phase 1: `e8137f95f` fix(plaud): make rename verification honest and stop default regeneration
- Phase 2: `a3ae3082e` feat(plaud): add stdio MCP read adapter behind a read-source switch
- Phase 3a discovery recorded in `reference/plaud-v4-rewrite-plan.md`; no code commit.

## Phase 1
`fetch_plaud.py` short-term fixes were already in the working tree from the prior run. This pass added the doc corrections: step-04 rules 2 and 4 and the `--rename` sequence, the plaud-transcripts SKILL.md API section, and a superseded banner on `systems/plaud-speaker-sync-fix.md`. The plan itself was committed too.

## Phase 2
New `skills/plaud-transcripts/scripts/plaud_read.py`: a raw MCP stdio JSON-RPC client (initialize, tools/call), pinned to `@plaud-ai/mcp@0.3.14`, with normalization of MCP output onto the legacy recording/detail shapes so the staging contract is unchanged. `fetch_plaud.py` gains `--read-source api|mcp`, default api. MCP auth failures surface as `MCP_AUTH_REQUIRED` with the login command.

Tested live: MCP initialize handshake succeeds, `tools/list` returns login, list_files, get_file, get_note, get_transcript, get_current_user, logout. `get_current_user` fails closed as `McpAuthError` because there is no MCP OAuth token yet. Adapter normalization, transcript pagination, summary resolution, untrusted-wrapper stripping, and auth-error classification were tested offline with synthetic payloads. The api path still reads the live account.

MCP login is still pending. It opens a browser and blocks for the callback, so it is a supervised step.

## Phase 3a discovery (blocked)
All read-only:

1. Account `version_tag` is `v3` (`/user-app/profile/account/me`), not v4.
2. `file-app/v3` and `file-app/v4` detail, recordings/all, and update/content all return `-1800907`, so the path version is not the issue.
3. Header replay (edit-from, app-platform, App-Platform, app-language, timezone, X-Request-ID, x-device-id, x-pld-user, version_tag cookie v3/v4) never cleared it.
4. The v3 shell bundle has no `file-app` route strings. Workspace-scoped calls use a workspace token from `resolveWorkspaceToken(workspaceId)`; this account exposes no workspace.
5. Playwright has no Plaud session (empty localStorage/cookies), so no capture was possible.

Gate: David must sign in to web.plaud.ai in Playwright or Chrome DevTools and confirm whether the v3-tagged account ever calls a `file-app` route. If it does not, the private v4 write route is unavailable and Phase 3 needs a supervised rename plus a Plaud support ticket.

## Phase 3 result (browser capture plus live writes)
David signed in to the Playwright browser. Capture findings:

- Zero `file-app` requests on dashboard load and on recording-detail load. The v3 app uses `/file/simple/web` and `/file/detail/{id}`.
- The browser's `/file/detail` token is a workspace JWT with `ver: 2`; the token the script can mint at `/user-app/auth/workspace/token/{wid}` is `ver: 1` and file-app v3/v4 both reject it with `-1800907`. Account `version_tag` is v3. Minting a ver 2 token needs the web session's `frill` exchange; credential escalation was stopped there.
- The v3 web client's transcript write helper is `PATCH /file/{id}` with `{trans_result, support_mul_summ: true}` plus `POST /ai/update_source_info` with `{file_id, source_id: <transaction_polish full data_id>, source_type: "transaction_polish", source_content: JSON.stringify(trans_result)}`. The second call is what the script has been missing.

Live tests:
- Same-value on 3f30d76f (167 segments): both calls status 0, trans_result identical, polish identical, speakers unchanged, file_version advanced.
- Single rename on 900d3853c0a06d570942db021be3853d: Speaker 1 -> "Speaker 1 TEST" on 22 segments. Verified in legacy trans_result, the polish source, and the web UI after reload. file_version 1793725121 -> 1793728494. Backup at ~/Downloads/transcript-staging/plaud_3c-single-rename_v3-backup-20261103T115453.json.

Verdict: file-app v4 unavailable for this account. The v3 two-write path is the route to implement in 3d, pending the 24h durability gate (due 2026-11-04 around 11:55 CT). Re-read all three places and force an app refresh and web reload.

## Phase 2 verification (2026-11-03)
David completed the MCP OAuth login. Ran fetch_plaud.py with --read-source api and --read-source mcp into separate staging directories for 2026-11-02 and 2026-11-03 and compared bytes.

Result: 5/5 staged markdown notes identical, 5/5 speaker sidecars identical, both plaud_all_recordings.json at 161 items. Raw per-recording JSON differs by design.

Fixes needed for equality, all committed: strip/add the `of_` partner id prefix; prefer transaction_polish (with transaction fallback); use start_at instead of created_at and parse naive ISO as UTC; one shared MCP server process per run to stop refresh-token races; auth heuristic no longer scans data payloads for "401" (a transcript mentioning 401(k) caused false auth failures); extract_summary handles raw markdown; strip ![PLAUD NOTE](permanent/...) and summaryCard references; repair Latin-1 mojibake.

Gate: day 1 of 5 passed (2026-11-03). Days 2-5 are 2026-11-04 through 2026-11-07.

Decision 2026-11-03: David chose to flip the default read source to mcp for the gate window, accepting the risk of a failed 6am ingest if the token refresh fails. Implemented: argparse and function defaults are mcp; api remains via --read-source api as the rollback. The run now preflights get_current_user, and on failure prints a PLAUD READ FAILED banner, writes ~/Downloads/transcript-staging/plaud_read_failure.json, prints PLAUD_READ_STATUS=failed, and exits 2. Success clears the marker and prints PLAUD_READ_STATUS=ok. Step-04 checks both and aborts on failure.

Unverified: token refresh across an unattended 6am run. First unattended run is the test.

Future capability noted in the plan: get_transcript(block="mark_memo") exposes device highlight moments under `marks`; the api path has no equivalent.

## Phase 3c test recording
David named the 2026-11-03 10:55 AM CST recording. Resolved to file_id `900d3853c0a06d570942db021be3853d` ("11-03 Meeting: Extension Incentives and AI SOW Eligibility", start 10:53:00, 279s, transcript and summary ready). It is the only recording on 2026-11-03.

## Side effects and notes
- `npx @plaud-ai/cli me` created `~/.plaud/anonymous_id` and `~/.plaud/device_id`. Left in place; the MCP login will use that directory.
- Pre-existing, untouched: `extract_summary()` in the api path returns "" when `pre_download_content_list[].data_content` is raw markdown rather than JSON with `ai_content`. The 2026-11-03 recording is in that shape. The MCP `get_note` path resolves it correctly. Worth a one-line fix on the api path, but it would change current staging output, so it was left for the Phase 2 acceptance decision.
- `contributions/plaud-connector-1.0.0/.../fetch_plaud.py` still refreshes at the next evolution package.

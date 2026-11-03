# Plaud v4 Rewrite Plan

Status: plan only. No implementation beyond the short-term fixes listed in Phase 1.
Owner: Rigby. Written 2026-11-03.

## Why this exists

Speaker renames stopped persisting on 2026-10-09. The account is on Plaud 4.0. The
legacy `PATCH /file/{file_id}` the pipeline uses writes a store that 4.0 does not
treat as authoritative: it returns HTTP 200 with `status: 0`, then the 4.0
transcript pipeline rebuilds and resets `speaker` back to `original_speaker`. Eleven
consecutive recordings, four runs, zero persisted renames.

Live evidence from 2026-11-03, re-confirmed during this work:

| Route | Result |
|---|---|
| `GET /file-app/v4/recordings/all` | HTTP 200, body `{"status":-1800907,"msg":"Please re-align version"}` |
| `GET /file-app/v4/files/detail/{id}` | HTTP 200, body `{"status":-1800907,"msg":"Please re-align version"}` |
| `POST /file/list` | HTTP 200, `status: 0`, full `trans_result` with `speaker`, `original_speaker`, `segment_uid` |
| `PATCH /file/{id}` | HTTP 200, `status: 0`, write is not durable |

The pipeline's whole rename path is built on the legacy route, so a full rewrite of
the write side is required. The read side also deserves a supported footing, because
the private web routes are what Plaud keeps moving.

## Target architecture

Three phases, in this order. Each phase is independently useful and independently
reversible.

1. **Phase 1 (landed 2026-11-03): short-term fixes to `fetch_plaud.py`.** Stop making
   things worse, verify honestly, stop regenerating by default.
2. **Phase 2: move the read path to the official Plaud MCP.** Supported, documented,
   read-only.
3. **Phase 3: move the rename write to the 4.0 content endpoint.** Requires an auth
   discovery step first. This is the only phase that restores the original feature.

---

## Phase 1: short-term fixes (landed)

Implemented in `skills/plaud-transcripts/scripts/fetch_plaud.py` on 2026-11-03,
uncommitted, working tree only:

- `check_api_response()` helper treats any HTTP 200 with `status != 0` as a failure
  and logs `msg`. Applied to the rename PATCH, the regeneration trigger,
  `sync_speaker()`, `list_speakers()`, and the `POST /file/list` read.
- `rename_speakers()` replaces the per-speaker loop and sends one PATCH per
  recording with the full segment array.
- `verify_speaker_renames()` replaced the free-text substring heuristic. It re-reads
  `trans_result` through `POST /file/list` and asserts that every segment whose
  `original_speaker` was mapped now carries the mapped name in `speaker`.
- `trigger_transcript_regeneration()` now fires only on a genuine database
  verification failure, never because the `transaction_polish` render looks stale.
- The fake "retrying" block is gone. Verification is bounded (2 attempts, one
  confirming re-read after a 5 second settle) and reports failure honestly.
- The staged markdown for a renamed recording is built from the database
  `trans_result`, not from `transaction_polish`, so the vault gets the verified
  names even though the web UI may not.

Known gaps left open deliberately:

- `workflows/plaud-ingest/steps/step-04-fetch-staging.md` still says the script
  "automatically triggers regeneration if needed" and that it verifies names appear
  in the transcript. Both statements are now wrong. Update the step file.
- `contributions/plaud-connector-1.0.0/skills/plaud-transcripts/scripts/fetch_plaud.py`
  is a packaging snapshot from before these fixes. It refreshes at the next
  evolution package, not by hand.
- `trigger_transcription()` still checks only the HTTP status on both of its calls.
  Same class of bug, outside the approved fix list.
- `rename_and_refetch()` writes `detail["duration"]` (milliseconds) into the staged
  note's `Duration` field. Pre-existing, cosmetic, worth a one-line fix later.
- `get_speaker_embeddings()` returned no embeddings on 2026-11-03, so auto-labeling
  is effectively dead. The speaker registry holds one profile ("O'Hara", last
  updated 2026-10-09). Treat as a separate track from the write path.

Phase 1 does not restore the feature. It makes every failure visible and removes the
self-inflicted regeneration.

---

## Phase 2: move the read path to the official Plaud MCP

### What it is

Plaud ships an official MCP server, generally available since 2026-05-12:

```
npx -y @plaud-ai/mcp@latest install
```

Docs: https://docs.plaud.ai/documentation/plaud_app/mcp
Package: `@plaud-ai/mcp`, latest 0.3.14 at the time of writing.

Tools exposed: `login`, `logout`, `get_current_user`, `list_files` (filters:
`query`, `date_from`, `date_to`, `page`, `page_size`), `get_file`, `get_note`,
`get_transcript`. All read-only. There is no write tool, so the rename cannot move
here.

Under the hood the MCP talks to Plaud's partner OAuth API at
`https://platform.plaud.ai/developer/api/open/third-party/files/` and
`.../files/{id}`. That is a different, supported surface from the private
`api.plaud.ai` web routes the script scrapes today, which is the main argument for
using it.

### Transport and data residency

- **Local stdio form** (the installer's default for Claude Code, Claude Desktop,
  Codex, Cursor and friends): `{"command": "npx", "args": ["-y", "@plaud-ai/mcp@latest"]}`.
  The transport stays on the machine. API calls still go to Plaud, exactly as the
  script's calls do today.
- **HTTP / connector form** (Claude Web, ChatGPT Web): recording data passes through
  Plaud's hosted MCP server in the US. Plaud states it is processed in transit and
  not stored, but it is still a third-party hop.

David's recordings include client work. **Use the stdio form only.** Do not enable
the hosted connector for this account.

Operational notes: tokens live in `~/.plaud/tokens-mcp.json`, sign-in is a browser
OAuth flow, and a broken token is fixed by deleting that file and signing in again.
Refresh behavior under an unattended scheduled run is unverified and must be tested
before Phase 2 is depended on for the 6am pipeline.

### Scope of the swap

| Function | Current source | After Phase 2 |
|---|---|---|
| Recording discovery for a date | `GET /file/simple/web` pagination | `list_files` with `date_from` / `date_to` |
| Recording name, duration, start | legacy list fields | `list_files` / `get_file` |
| AI summary | `pre_download_content_list` auto_sum | `get_note` |
| Transcript text | `GET /file/detail` plus S3 presigned URLs | `get_transcript` |
| Speaker read for rename (`original_speaker`, `segment_uid`) | `POST /file/list` | **stays on the legacy API** |
| Rename write | `PATCH /file/{id}` | **stays in the script, moves in Phase 3** |
| Share link creation | `POST /share/public/create` | **stays on the legacy API** |
| Speaker registry sync | `POST /speaker/sync` | **stays on the legacy API** |

Discovery and transcript pull are the two reads that break most often when Plaud
changes its web client. Moving them to a documented server removes most of the
fragility for the least risk.

### Implementation shape

- Add a thin adapter module, `skills/plaud-transcripts/scripts/plaud_read.py`, with
  two functions: `list_recordings_for_date()` and `fetch_transcript_and_summary()`.
  It shells out to the MCP through the client, or calls `@plaud-ai/cli`
  (`npm install -g @plaud-ai/cli`, commands `plaud files`, `plaud transcript <id> -o`,
  `plaud summary <id> -o`) if an MCP client is not available in the execution
  context. The CLI is the same data, also read-only, and is simpler to call from a
  scheduled shell step.
- Keep `fetch_plaud.py` as the orchestrator and the only writer. Add a
  `--read-source mcp|api` switch, defaulting to `api` until Phase 2 is accepted,
  then flipping the default.
- Preserve the staging file contract exactly: same filenames, same headings, same
  `plaud_all_recordings.json`, `plaud_pending.json`, `plaud_<name>_speakers.json`
  shapes. Knox and step-05 must not notice the change.

### Questions Phase 2 must answer before merging

1. Does `get_transcript` return segment-level `speaker` **and** `original_speaker`
   **and** `segment_uid`? Without `original_speaker` the verification design in
   Phase 1 cannot move, and the rename read must stay on `POST /file/list`.
2. Does the MCP transcript reflect the 4.0 authoritative content, or the legacy
   `transaction_polish` render? If it reflects the 4.0 content, a rename written by
   Phase 3 becomes visible through the MCP even while the legacy routes lag. That
   would give us a clean verification channel.
3. Timestamp units: `start_time` in `trans_result` is milliseconds, MCP docs describe
   `source_list` as timestamps with no unit stated. Confirm and normalize in the
   adapter, not in the renderer.
4. `list_files` date filtering: docs say `date_from` / `date_to` are `YYYY-MM-DD`.
   Confirm the boundary is in the recording's local timezone, matching the current
   `filter_by_date()` behavior.
5. Duration: MCP documents milliseconds, legacy list returns seconds in some fields.
   Normalize once.
6. Pagination limits: `list_files` ignores `page` / `page_size` when filters are set.
   Confirm a single filtered call returns every recording for a date, or add a
   follow-up unfiltered pass.

---

## Phase 3: move the rename write to the 4.0 content endpoint

### 3a. Endpoint shape (third-party sourced, unverified)

Public clients describe a durable write as:

```
PATCH /file-app/v4/files/update/content/{file_id}
{
  "object_id": "<file_id>",
  "content_id": "<content object id for the transcript>",
  "content": [ <full segment array, same shape as trans_result> ],
  "origin_version": <version_ms of the content object>,
  "has_replaced_speaker": true
}
```

This shape comes from third-party GitHub clients, not from Plaud's changelog or
developer docs. It has **not** been verified against this account, and the routes
currently reject our token with `-1800907`. Treat it as a hypothesis until 3b and 3c
prove it.

### 3b. Auth re-alignment discovery (do this before any v4 write)

The v4 routes answer HTTP 200 with `{"status":-1800907,"msg":"Please re-align version"}`
for a token minted by `POST /auth/access-token`. That message reads like a scope or
client-version mismatch, not a permission denial.

Discovery steps:

1. Open `https://web.plaud.ai` in Chrome with DevTools open, signed in as David, and
   filter Network for `file-app/v4`.
2. Record, for one detail request and one content request: the full request header
   set (`authorization`, `x-scope-id`, `app-platform`, `app-version`, `edit-from`,
   `origin`, `referer`, and every other `x-*` header), the token issuance route the
   page used, and the response shape for `GET /file-app/v4/files/detail/{id}`.
3. Decode both JWTs (the page's and `~/.config/plaud/token.json`) and diff the claims.
   Look for workspace, scope, tenant or client identifiers.
4. Replay the v4 detail request with the script's token plus each candidate header,
   one at a time, until `-1800907` clears. That identifies the minimum needed set.
5. Decide where the workspace-scoped token is stored. It is session material:
   `~/.config/plaud/`, mode 0600, never in the repo, never printed in logs or working
   memory.
6. If the workspace token cannot be minted headlessly (for example it only exists in
   a browser session), that changes the design: the write becomes a supervised
   operation, or the pipeline waits for a supported write API.

Capture the detail response in the same pass. It must reveal `object_id`,
`content_id`, and `version_ms` (or whichever field carries the revision), because
those three values are the entire safety mechanism for the write.

#### Discovery result, 2026-11-03 (blocked on a human gate)

Non-interactive work was done first. Findings, all read-only:

1. `GET /user-app/profile/account/me` with the script's token returns
   `data.version_tag = "v3"`. The account is tagged for the v3 web shell, not v4.
2. Every `file-app` route tried returns HTTP 200 with `-1800907`, for **both**
   versions: `/file-app/v3/files/detail/{id}`, `/file-app/v4/files/detail/{id}`,
   `/file-app/v3/recordings/all`, `/file-app/v4/recordings/all`, and both
   `/files/update/content/{id}` paths. It is not a v3-vs-v4 path problem.
3. Header replay did not clear it. Tried, one at a time and combined:
   `edit-from: web`, `app-platform: web`, `App-Platform: web`, `app-language`,
   `timezone`, `X-Request-ID`, `x-device-id`, `x-pld-user: <jwt sub>`, and the
   `version_tag` cookie at both `v3` and `v4`. All still `-1800907`.
4. The web bundle (`app-initial-common`, build `prod-261102-162038`) shows the
   shell constant `lc = "v3"`, `version_tag` written as a cookie, and
   workspace-scoped requests built by `mi()` from
   `resolveWorkspaceToken(workspaceId)` returning `{token, domain, workspaceId}`.
   The account profile exposes no workspace, so there is no workspace token to
   resolve.
5. The `file-app` route strings do not appear in the v3 shell bundle at all. The
   v3 shell uses `/user-app/...` and the legacy `/file/...` routes. This is
   consistent with `file-app` belonging to the v4 shell that this account is not
   on.
6. The Playwright browser has no Plaud session: empty `localStorage`, no cookies,
   empty page body. Nothing to capture without an interactive sign-in.

**Gate:** David must sign in to `web.plaud.ai` in the Playwright browser (or
Chrome DevTools) so a real `file-app` request can be observed, if the v4 shell
serves one for this account. The specific question the capture must answer: does
the web UI for this v3-tagged account call any `file-app` route at all? If it does
not, the private v4 write route is unavailable to this account, and Phase 3 must
fall back to a supervised rename plus a Plaud support ticket rather than a
headless write path.

### 3c. Write verification sequence

Do these in order, stopping at the first surprise:

1. **Read only.** With the aligned token, `GET /file-app/v4/files/detail/{id}` on
   `3f30d76fc4f8757490008c4e4a3dbadb` and record the response shape to staging. No
   write.
2. **Same-value write.** Send the segment array exactly as read, with
   `origin_version` from that same read and `has_replaced_speaker` left at its
   existing value. Confirm `status: 0`, then read back and confirm the content is
   identical and the version advanced. This is the same-value discipline used in the
   2026-11-03 diagnostic.
3. **One rename.** Rename a single speaker on the same recording. Verify in three
   places: v4 detail, legacy `POST /file/list`, and the web UI.
4. **Durability window.** Wait 24 hours and re-read all three. Also force a Plaud app
   refresh and a web reload. The bug being fixed is a delayed revert, so a same-second
   read proves nothing.
5. **Multi-speaker rename.** Repeat with all six labels on the same recording. One
   PATCH, full array, then the same three-way verification.
6. **Pipeline integration.** Point `fetch_plaud.py` at the v4 write behind a flag and
   run one plaud-ingest end to end. The vault note must carry the new names and the
   run must report `RENAME_STATUS=verified` from a v4 read, not a legacy read.

### 3d. Implementation shape

- New module `skills/plaud-transcripts/scripts/plaud_v4.py`: auth refresh, detail
  read, content write, version handling, in-band status checking. All v4 knowledge in
  one file so the next Plaud change is a one-file change.
- `fetch_plaud.py` calls `plaud_v4.rename_speakers()` when a v4 token is available and
  falls back to the legacy `rename_speakers()` otherwise, logging which path ran.
- Before every v4 PATCH, write the pre-write state to
  `~/Downloads/transcript-staging/plaud_<name>_v4-backup-<timestamp>.json`:
  `object_id`, `content_id`, `origin_version`, and the full segment array. That file
  is the rollback.
- Verification moves to the v4 detail read, with the legacy `POST /file/list` check
  kept as a second opinion until two weeks of clean writes.
- Never send a partial segment array. The endpoint's contract is the whole content
  object.

---

## Sequencing and gates

| Phase | Work | Gate to exit |
|---|---|---|
| 1 | Short-term fixes in `fetch_plaud.py` | Landed. Output is honest, regeneration only on genuine DB failure. Update step-04 wording. |
| 2 | MCP or CLI read adapter | Discovery and transcript pull run through the adapter for 5 consecutive days of plaud-ingest with byte-identical staging output. Token refresh survives an unattended run. |
| 3a | Auth discovery | A v4 detail read returns `status: 0` with the script's aligned token, and the response shape is captured. |
| 3b | Same-value write | Content read back identical, version advanced, no revert after 1 hour. |
| 3c | Rename on test recording | Names in v4 detail, legacy `trans_result`, and the web UI, still correct after 24 hours. |
| 3d | Pipeline integration | One end-to-end plaud-ingest with names correct in the vault note and `RENAME_STATUS=verified`. |

Do not start 3a before 2 is stable. If Phase 3 stalls on auth, Phase 2 still leaves
the pipeline on a supported read path.

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| v4 endpoint shape is wrong or moves | Write fails or misfires | In-band status check fails closed; no partial arrays; legacy read stays as second opinion |
| Wrong `content_id` or stale `origin_version` | Overwrite the wrong revision, lose earlier manual edits | Read immediately before write, use the version from that read, keep the backup file |
| OAuth token for the workspace cannot be minted headlessly | Rename becomes supervised only | Discover in 3b before committing to the design; fall back to a supervised `--rename` run |
| Session or scope token leaks | Account access exposure | `~/.config/plaud` at 0600, never logged, never in the repo, redact in working memory |
| MCP hosted connector used by accident | Client recording data through a third-party server | Stdio only, documented in the skill; do not enable the connector for this account |
| MCP package or CLI changes shape | Read path breaks | Adapter isolates it; pin a tested version and upgrade deliberately |
| Renames revert after hours, not seconds | False success | 24 hour durability gate, plus the settle re-read already in Phase 1 |
| Plaud blocks private v4 routes entirely | Feature blocked | Support ticket in parallel; official developer API is the long-term answer |
| Legacy speaker embedding sync stays broken | No auto-labeling | Separate track, not a blocker for renames |

## Test recordings

- `3f30d76fc4f8757490008c4e4a3dbadb`, the 2026-11-02 Improving/ASEI planning meeting.
  167 segments, 6 generic speakers, already used for diagnostics, no data sensitivity
  beyond internal meeting content. Primary test target.
- One recording with a single speaker already renamed in the web UI, to prove the
  write does not clobber existing names. Pick at Phase 3 time.
- One low-value recording David is willing to leave with generic labels if a write
  fails. Pick at Phase 3 time.

## Rollback

- **Phase 2:** the adapter sits behind `--read-source`. Reverting is flipping the
  default back to `api`. No data migration, no schema change.
- **Phase 3:** every write is preceded by a full backup of the content object. A
  rollback is re-sending that array with a fresh `origin_version`, or falling back to
  the legacy path with `RENAME_STATUS=unverified` reported. Keep both write paths in
  the code for at least two weeks of clean v4 writes; do not delete the legacy path in
  the same change.
- **Everything:** changes are confined to `skills/plaud-transcripts/scripts/`. Staging
  files are regenerable from the API. No stored data migrates, so a git revert is a
  complete rollback.

## When Plaud changes it again

Assume every undocumented endpoint moves. Design for detection, not for stability.

- Run a read-only probe at the start of every plaud-ingest and at boot:
  `POST /file/list`, the v4 detail route, and the MCP `get_current_user`. Each probe
  checks the in-band status and prints the endpoint, status and msg. A failed probe
  degrades the run to read-only and alerts, rather than half-writing.
- Log the endpoint shape on every successful v4 write (field names, version field,
  segment count). A silent shape change then shows up as a diff in the run record
  instead of a corrupted transcript.
- Keep all v4 knowledge in `plaud_v4.py`. Keep all legacy web-route knowledge in
  `fetch_plaud.py`. Keep the MCP adapter separate. Three files, three blast radii.
- Watch the official changelog (https://docs.plaud.ai/plaud-mcp-cli/changelog.md and
  the developer platform docs) for a supported write or speaker endpoint. If one
  appears, prefer it over the private route and delete the private write.
- Open a Plaud support ticket in parallel: ask for the supported way to update
  speaker labels on a 4.0 account, and report that a token minted by
  `POST /auth/access-token` gets `-1800907` on `file-app/v4` routes. A supported
  answer beats reverse engineering.

## Stale documentation to correct

- `systems/plaud-speaker-sync-fix.md` (2026-06-10) documents the pre-4.0 three-store
  model ("Database, S3 transaction, S3 transaction_polish") and states that renames
  now sync to vault notes. Under 4.0 the legacy PATCH is not authoritative, so the
  document is stale. Mark it superseded and point it here.
- `skills/plaud-transcripts/SKILL.md` describes the same three-layer model in its API
  section. Audit and correct during Phase 1 documentation cleanup.
- `workflows/plaud-ingest/steps/step-04-fetch-staging.md` rules 2 and 4 promise
  automatic regeneration when names are missing from the transcript. That behavior
  was removed 2026-11-03. Update the rules and the failure-mode table.

## Decisions needed from David

1. Approve the local stdio install of `@plaud-ai/mcp` for the read path (adds a
   supported dependency, tokens at `~/.plaud/tokens-mcp.json`). Alternative: the
   `@plaud-ai/cli` command line, same data, no MCP client needed.
2. Approve the Chrome DevTools capture of the 4.0 web client's request headers for
   Phase 3a, including where the workspace-scoped token is stored.
3. Name the expendable test recording for Phase 3c.
4. Decide whether to open the Plaud support ticket now (faster if the v4 shape proves
   wrong) or after Phase 3b.

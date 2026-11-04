---
type: working
task_id: "session"
session_id: "rigby-2026-11-03-105111"
agent-source: rigby
created: 2026-11-03T10:51:11-05:00
expires: 2026-11-05T10:51:11-05:00
status: active
context: "Rigby implemented Plaud short-term fixes in fetch_plaud.py and authored the v4 rewrite plan — 2026-11-03"
---

# Rigby: Plaud short-term fixes + v4 rewrite plan

## What was requested and what was produced
David approved: (1) implement the short-term fixes to skills/plaud-transcripts/scripts/fetch_plaud.py, (2) author the v4 rewrite plan. Both done, working tree only, nothing committed.

## Task 1: fetch_plaud.py (+208/-123)
- `check_api_response()` added: HTTP != 200, non-JSON, or HTTP 200 with in-band `status != 0` all treated as failure with logged msg. Applied at rename PATCH, regeneration trigger, sync_speaker(), POST /file/list read, and list_speakers().
- Regeneration no longer a default consequence: `trigger_transcript_regeneration()` fires only on genuine DB verification failure.
- Verification rebuilt: free-text heuristic deleted; `verify_speaker_renames()` re-fetches via POST /file/list and asserts segment-level speaker mappings, with 2 bounded retries plus confirming re-read after 5s settle (guards against async 4.0 reverts producing false passes).
- One PATCH: `rename_speaker()` -> `rename_speakers()`, full mapping, single PATCH.
- Fake "retrying" block replaced with real bounded retry; final output line `RENAME_STATUS=verified|unverified|failed`; Knox's osascript call unaffected.
- Companion fix: staged markdown now rendered from DB `trans_result` (not `transaction_polish`) on successful PATCH, so notes show the names that were actually written.

## Test evidence
Live API: v4 -1800907 probe correctly detected; verify passed on correct expectation and failed with per-segment detail on wrong one; identity mapping test: one PATCH, status 0; full rename_and_refetch against scratch staging: RENAME_STATUS=verified, no regeneration fired; both failure branches forced with stubs; py_compile clean. Three identity PATCHes re-sent existing values only (no new names written); regeneration not fired live (destructive). Tests on recording 3f30d76fc4f8757490008c4e4a3dbadb.

## Flags / follow-ups
- `workflows/plaud-ingest/steps/step-04-fetch-staging.md` rules 2 and 4 still promise automatic regeneration when names are missing; now wrong. Needs a follow-up edit (workflows/ gated path, not yet approved).
- `contributions/plaud-connector-1.0.0/.../fetch_plaud.py` snapshot refreshes at next evolution package.
- Left alone deliberately: `trigger_transcription()` HTTP-only check; duration (ms) written into staged note Duration field (pre-existing); `get_speaker_embeddings()` returns nothing on this account, auto-labeling dead until the embedding track is revisited.
- Stale docs: `systems/plaud-speaker-sync-fix.md`, plaud-transcripts SKILL.md, and step-04 carry pre-4.0 claims.

## Task 2: reference/plaud-v4-rewrite-plan.md (368 lines)
Sequencing: Phase 1 short-term (landed) -> Phase 2 MCP/CLI read-path swap -> Phase 3a v4 auth discovery -> 3b same-value write -> 3c single rename with 24h durability gate -> 3d pipeline integration. Do not start 3a before Phase 2 stable.
- v4 PATCH shape marked third-party-sourced, with read-only detail-shape verification before any write.
- Auth discovery: DevTools capture of x-scope-id and friends, JWT claim diff, header-by-header replay.
- MCP option: stdio only; hosted connector routes recording data through Plaud's US server, ruled out for client work. Official MCP rides a supported partner API (platform.plaud.ai/developer/api/open/third-party/files/, visible in the 0.3.14 bundle); no write endpoint, so rename stays on private v4 route. @plaud-ai/cli noted as no-MCP-client alternative for scheduled runs.
- Risks, three named test recordings, rollback via per-write content backups, probe-and-degrade model for the next Plaud change.

## Decisions pending with David (listed at end of plan)
1. Approve stdio MCP install (Phase 2)
2. Approve DevTools header capture (Phase 3a)
3. Name an expendable test recording (Phase 3c)
4. When to open the Plaud support ticket

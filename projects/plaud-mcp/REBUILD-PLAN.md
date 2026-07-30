# Plaud Rebuild Plan — Decommission In-House Server, Adopt Official MCP

**Owner:** Rigby (System Operator — capability building, connector installation)
**Requested by:** David O'Hara
**Date:** 2026-07-30
**Status:** Not started

---

## Why

Plaud shipped an official MCP (`@plaud-ai/mcp`, docs at docs.plaud.ai/plaud-mcp-cli/mcp). The in-house server at `projects/plaud-mcp/plaud-mcp-ies/` was built in March as a stopgap, wrapping the community `plaud-toolkit` package because "official API is coming soon, switch when available" (see `PLAN.md` line 529). It's unfinished (657 lines, never confirmed working end-to-end per its own acceptance criteria), and everything it does on the read/auth side, the official package now does better: real OAuth instead of scraped bearer tokens, `list_files` with date/query filters instead of raw pagination, `get_note` for Plaud's own AI summary instead of us reconstructing one. Keeping it around is dead weight. Delete it.

The four working skills (`plaud-discover`, `plaud-trigger`, `plaud-speaker-id`, `plaud-transcripts`) and the `plaud-ingest` workflow are not obsolete. The official MCP is read-only and stateless: it has no transcription-trigger tool, no speaker/calendar cross-reference, and no vault write capability. Those skills carry the actual value and stay, but their internals need to be rebuilt to call the official tools instead of the reverse-engineered API and `fetch_plaud.py`.

---

## Part 1 — Decommission

1. **Snapshot before touching anything.** Standard protocol, no exceptions: back up `projects/plaud-mcp/` in full before deletion.
2. **Delete `projects/plaud-mcp/plaud-mcp-ies/`** (the TypeScript server: `src/`, `package.json`, `tsconfig.json`, `routing-rules.json`).
3. **Delete `projects/plaud-mcp/PLAN.md` and `SPEC.md`.** Superseded by this document. Keep `README.md` but rewrite its status line to point here instead of "Planned (2026-03-16)."
4. **Update `identity/INTEGRATIONS.md` line 17.** Currently reads:
   `MCP server (`plaud_*` tools) — `projects/plaud-mcp/plaud-mcp-ies/``
   Change the path reference to the official package (`@plaud-ai/mcp`, installed via `npx -y @plaud-ai/mcp@latest install`).
5. **Confirm no other file references `plaud-mcp-ies`** before deleting (grep the repo). If `contributions/plaud-connector-1.0.0` or any agent file points at it, update those references first.

---

## Part 2 — Install Official MCP

1. Run `npx -y @plaud-ai/mcp@latest install` on David's machine. This auto-detects Claude Desktop and Claude Code, writes the MCP config, and opens the browser for OAuth. Click Authorize.
2. Restart Claude Desktop (⌘Q + reopen) and start a fresh Claude Code session per the install output.
3. Smoke test in a live session: `get_current_user`, `list_files` (confirm it returns real recordings), `get_file` on one recording, `get_note`, `get_transcript`.
4. **Verify where the OAuth token lands.** The docs reference `~/.plaud/tokens-mcp.json`. The old reverse-engineered setup used `~/.config/plaud/token.json` and `~/.plaud/config.json` (different paths, different formats per `PLAN.md`). Check whether the new token is a plain bearer token that the raw API calls in `plaud-trigger` can reuse, or whether it's wrapped/scoped in a way that requires keeping a separate auth path for the two skills below that still need direct API access. Do not assume compatibility, confirm it.

---

## Part 3 — Rebuild Skills

### `skills/plaud-discover` — rebuild
Replace the manual `GET /file/simple/web` pagination loop with the official `list_files` tool. It already supports `query`, `date_from`, `date_to`, and pagination natively, so most of this skill's "enumerate everything, compare against vault" logic gets simpler, not harder. Keep the vault cross-reference logic (comparing against `zzPlaud/` filenames) exactly as-is; only the fetch mechanism changes.

### `skills/plaud-trigger` — keep, but confirm auth path
No official tool exists for triggering transcription on `missing`/`pending` recordings. This skill's two-step PATCH + POST against the raw Plaud API stays. The only open question is auth (see Part 2, step 4). If the official MCP's token can't be reused, this skill needs to keep its own login flow, isolated and documented as "the one place we still touch the raw API directly, because Plaud hasn't exposed this as an MCP tool." Flag that explicitly in the skill's Prerequisites section so it doesn't look like leftover cruft to whoever reads it next.

### `skills/plaud-speaker-id` — rebuild input handling
Logic stays (calendar cross-reference first, controller fallback only when unresolved, hard gate already in place). What changes is the input: instead of reading `_speakers.json` files written by `fetch_plaud.py` to a staging folder, pull speaker/segment data directly from the official `get_transcript` tool's response (it returns speaker labels with timestamps natively). Rebuild the "Load all `_speakers.json` files" step to instead call `get_transcript` per recording and extract the same `all_speakers` / `untagged_speakers` shape from that response.

### `skills/plaud-transcripts` — biggest rebuild
This is the one built entirely around `fetch_plaud.py` and a `~/Downloads/transcript-staging/` folder. Retire the staging-file pattern. Replace it with direct calls: `get_file` for metadata, `get_note` for Plaud's AI summary (stop hand-parsing summaries out of raw transcript text, `get_note` already returns summary, action items, and key topics), and `get_transcript` for the full text. The vault-formatting, tagging, and routing logic downstream of that stays. Delete `scripts/fetch_plaud.py` once nothing depends on it, and remove the "if fetch script returns nothing, check the scheduled task" troubleshooting language since there's no more fetch script to check.

### `workflows/plaud-ingest` — update step references
Steps 01, 02, 03, 04, 05, 05b all reference either a skill above or `fetch_plaud.py` directly (steps 04 and 05b call the script explicitly). Update the `workflow.md` step table and each `steps/step-0N-*.md` file to point at the rebuilt skills instead of the script. The 6-step shape and the interactive pause at step-03 (speaker ID) don't need to change, only what each step calls.

### `contributions/plaud-connector-1.0.0` — update manifest
This packages the skills for distribution (e.g., to Steve Hall's IES per the original plan). Update its component file list once the skills above are rebuilt, and confirm the `dependencies.mcp_servers` field now lists the official Plaud MCP instead of implying a custom server.

### `.claude/skills/` mirrors
`knox-transcripts-plaud`, `plaud-discover`, `plaud-speaker-id`, `plaud-transcripts`, `plaud-trigger` appear mirrored under `.claude/skills/` for registration. Confirm whether these are symlinks or duplicated copies, if duplicated, update both locations or fix the duplication so there's one source of truth going forward.

---

## Part 4 — Verify and Log

1. Run `plaud-ingest` end-to-end against real recordings, not a dry run, confirm vault notes land correctly, speaker resolution still works, and Monday/Alice routing steps still fire.
2. Run it twice back to back, confirm idempotency (no duplicate vault notes).
3. Update `skills/_manifest.jsonl` descriptions if any changed materially (e.g., `plaud-discover`'s description currently says "Query the Plaud API," fine as-is, but update if the mechanism description changes).
4. Log this as a platform change per standard protocol: snapshot reference, what was deleted, what was rebuilt, and any conflicts found, following the same format as prior entries in `evolutions/history.md`.

---

## Acceptance Criteria

- `projects/plaud-mcp/plaud-mcp-ies/` no longer exists.
- Official `@plaud-ai/mcp` installed and authorized, smoke-tested with all 7 tools.
- `identity/INTEGRATIONS.md` reflects the official package, not the deleted in-house path.
- `plaud-discover`, `plaud-speaker-id`, `plaud-transcripts` call official MCP tools, not raw API endpoints or `fetch_plaud.py`.
- `plaud-trigger` still works, with its auth path explicitly documented as the deliberate exception (not an oversight).
- `plaud-ingest` workflow runs end-to-end twice with no duplicates and correct routing.
- `scripts/fetch_plaud.py` deleted once nothing references it.

## Risks

| Risk | Mitigation |
|---|---|
| Official MCP's OAuth token isn't reusable for `plaud-trigger`'s raw calls | Confirmed in Part 2 step 4 before rebuilding anything else. If incompatible, keep a minimal isolated login flow for that one skill only. |
| Official MCP has no batch/webhook mechanism, still requires an agent to call it | No change from today, `plaud-daily-fetch` scheduled task still drives the pipeline, just calling different tools underneath. |
| Rebuilt skills break mid-flight on a recording already in `plaud-ingest`'s `state.yaml` as in-progress | Let any in-progress run finish or abort cleanly on the old path before cutting over; don't rebuild while a run is mid-pipeline. |

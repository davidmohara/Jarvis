---
type: working
task_id: "session"
session_id: "rigby-2026-11-03-123935"
agent-source: rigby
created: 2026-11-03T12:39:35-05:00
expires: 2026-11-07T12:39:35-05:00
status: active
context: "Rigby Phase 2 verification: MCP read path byte-identical to api path, day 1 of 5-day gate passed — 2026-11-03"
---

# Rigby: Plaud Phase 2 verification (commit 484dbe346)

## Result
- fetch_plaud.py staged via --read-source api and --read-source mcp into separate dirs for 2026-11-02 and 2026-11-03 recordings; byte comparison: 5/5 markdown notes identical, 5/5 speakers.json sidecars identical, both plaud_all_recordings.json carry 161 items (raw per-recording JSON differs by design; nothing downstream reads it).
- Day 1 of the 5-day byte-identical gate recorded as passed in the plan.

## Fixes required to reach equality (all in 484dbe346)
- Partner ids of_<legacy_id>: stripped on output, added on input (vault frontmatter and filenames keep legacy id).
- MCP transcript prefers transaction_polish with transaction fallback (matches api path).
- Uses start_at not created_at; parses partner API naive ISO timestamps as UTC.
- One shared MCP server process per run (a process per call raced on token refresh, spurious 401s).
- Auth heuristic no longer scans data payloads: a transcript mentioning 401(k) was misread as a 401 — actual cause of the intermittent auth failures.
- extract_summary handles raw markdown summaries (this was the deferred api-path bug; fixed here).
- Both paths strip UI-only PLAUD NOTE/summaryCard references and repair Latin-1 mojibake in legacy S3 text.

## Noted
- get_transcript(block="mark_memo") exposes device highlight moments with no api equivalent: logged as future capability in the plan.
- Hosted claude.ai Plaud connector deliberately not authenticated (routes recordings through Plaud US servers).

## Gate status / open items
- Days 2-5 of the gate: 2026-11-04 to 2026-11-07. Default read-source remains api, so the gate will NOT accrue unless a daily run uses mcp. Decision pending with David: flip the default for the gate window, or add a comparison-only daily run.
- Unverified: MCP token refresh across an unattended 6am run (token file has expires_at + refresh_token; headless refresh unproven). Main risk before flipping the default.
- Phase 3c durability gate due 2026-11-04 ~11:55 CT; "Speaker 1 TEST" still on 900d3853c0a06d570942db021be3853d; Knox must not ingest it until reverted (boot reminder rem-20261103T175720-FRL5LH holds the block).

## Commits this session (Plaud v4 plan)
e8137f95f (Phase 1), a3ae3082e (Phase 2 adapter), c492ee538 (3a discovery), a7cae2d82 (Phase 3 v3 write path), 484dbe346 (Phase 2 verification), 10b2fd72a (default read path flipped to mcp for the gate window; David accepted the 6am-refresh risk; fail-closed preflight on get_current_user with banner, marker file, exit 2, step-04 aborts without silent retry or api fallback).

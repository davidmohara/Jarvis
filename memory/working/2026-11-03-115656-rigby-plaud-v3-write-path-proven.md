---
type: working
task_id: "session"
session_id: "rigby-2026-11-03-115656"
agent-source: rigby
created: 2026-11-03T11:56:56-05:00
expires: 2026-11-06T11:56:56-05:00
status: active
context: "Rigby Phase 3 capture after David's web sign-in: v4 unavailable, v3 two-write path proven live — 2026-11-03"
---

# Rigby: Plaud Phase 3 — v3 write path proven

## Capture result (David signed in via Playwright)
- Zero file-app requests on dashboard or recording-detail load. The v3 client uses GET /file/simple/web and GET /file/detail/{id}.
- The real /file/detail request carries a workspace-scoped JWT (wid, mid, ver: 2, role, jti). The script-minted token from /user-app/auth/workspace/token/{wid} is ver: 1; file-app v3 and v4 both reject it with -1800907. Obtaining a ver 2 token requires replaying the web "frill" client exchange; the credential-minting classifier blocked that, correctly. No ver 2 token obtained.
- Verdict: private v4 file-app route unavailable for this account. Do not pursue.

## The real fix (v3 web client's transcript write helper, on the existing account token)
1. PATCH /file/{id} with {trans_result, support_mul_summ: true}
2. POST /ai/update_source_info with {file_id, source_id: <transaction_polish full data_id>, source_type: "transaction_polish", source_content: JSON.stringify(trans_result)}
The second call is what the script has been missing: PATCH alone leaves the 4.0 pipeline free to rebuild from its own polish source.

## Live verification
- Same-value test on 3f30d76f (167 segments): both calls status 0, identical content, no side effects.
- Single rename on approved test recording 900d3853c0a06d570942db021be3853d: "Speaker 1" -> "Speaker 1 TEST" on 22 segments. Verified three ways after reload: legacy trans_result 22/22, polish source 22/22, web UI renders "Speaker 1 TEST". file_version 1793725121 -> 1793728494. Backup: /Users/davidohara/Downloads/transcript-staging/plaud_3c-single-rename_v3-backup-20261103T115453.json

## Commits
Phase 1 e8137f95f, Phase 2 a3ae3082e, Phase 3a c492ee538, Phase 3 result a7cae2d82.

## Pending
1. 24h durability gate due 2026-11-04 ~11:55 CT: re-read all three stores plus forced app refresh and web reload.
2. After gate passes: implement the two-write sequence in fetch_plaud.py behind a flag (Phase 3d), then flip default.
3. Test label "Speaker 1 TEST" on 900d3853 must be reverted after the gate; Knox must NOT ingest that recording while the label is present (boot reminder added).
4. Phase 2 supervised MCP login (npx -y @plaud-ai/mcp@0.3.14 login) still needed.
5. extract_summary() raw-markdown bug: decide at Phase 2 switch.
6. Plaud support ticket now optional, not critical path.

## Browser
Left open on the recording page, storage intact. ~/.plaud/anonymous_id and device_id exist from CLI inspection; left for MCP login.

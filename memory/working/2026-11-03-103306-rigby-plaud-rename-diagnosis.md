---
type: working
task_id: "session"
session_id: "rigby-2026-11-03-103306"
agent-source: rigby
created: 2026-11-03T10:33:06-05:00
expires: 2026-11-05T10:33:06-05:00
status: active
context: "Rigby root-cause diagnosis of Plaud speaker-rename persistence failure — 2026-11-03"
---

# Rigby diagnosis: Plaud speaker rename does not persist

> **CORRECTED 2026-11-03 (same agent, follow-up probes):** this account is on Plaud 4.0. The legacy PATCH write path is not authoritative, and the first-pass root cause below is superseded by the corrected cause in the CORRECTION section. The break window (2026-10-09 to 2026-10-22), code-path references, and the client-side amplifier all remain correct.

## Verdict (corrected)
Plaud's 4.0 cutover landed in the Oct 9-22 window. 4.0 keeps a new authoritative transcript content object; the legacy PATCH /file/{id} the script uses writes only the legacy store, returns 200/status 0, and looks successful, but the 4.0 pipeline rebuilds the transcript and resets speaker to original_speaker. Live evidence: v4 routes (GET /file-app/v4/recordings/all, /file-app/v4/files/detail/{id}) return HTTP 200 with in-band {"status":-1800907,"msg":"Please re-align version"} while every legacy route still answers normally on this transitional account.

The client-side amplifier stands unchanged: extract_transcript() reads transaction_polish, which PATCH never updates, so rename_and_refetch() always concludes failure and always fires is_reload:1, guaranteeing the 4.0 rebuild and the revert. Fixing that alone will not make the web UI show names; the write goes to the wrong store.

Second real defect: the script checks only resp.status_code == 200 (fetch_plaud.py:720, :1154, :630). Plaud reports failures in-band as status -NNNNNNN with HTTP 200, as the -1800907 probe proves.

## Verdict (first pass, superseded but mechanism still real)
Two independent causes: (1) client-side verification reads the wrong layer and forces regeneration; (2) regeneration resets speaker names. Proven with a no-op PATCH on 3f30d76fc4f8757490008c4e4a3dbadb. The regeneration-revert is now understood as the visible symptom of the 4.0 store split, not the whole cause.

## Break window
2026-10-09 to 2026-10-22, no recordings between to narrow it. Eleven consecutive recordings, four runs, zero persisted renames. No local change explains it (rename logic unchanged since 2026-06-11; later commits touched creds/argparse only). Likely a Plaud backend rollout tied to the new `segment_uid` schema. `systems/plaud-speaker-sync-fix.md` (2026-06-10) now documents stale behavior.

## Code path (fetch_plaud.py)
- `rename_and_refetch()` line 1169, called from step-04 of plaud-ingest
- `rename_speaker()` line 695: mutates seg["speaker"], PATCHes trans_result
- PATCH once per mapping (1221-1223), so N speakers = N PATCHes
- Broken DB verification 1239-1249 (prints "retrying..." but never retries)
- Destructive regeneration `trigger_transcript_regeneration()` line 1126 (is_reload: 1)
- `sync_speaker()` 601-643 checks only HTTP status; registrations silently failing

## Recommended fix (corrected; not implemented; needs David approval)
1. **Durable:** move the write to PATCH /file-app/v4/files/update/content/{file_id} with object_id, content_id, full segment array as content, origin_version (the object's version_ms), and has_replaced_speaker: true. Requires re-aligning auth first (workspace-scoped x-scope-id token); the v4 routes reject with -1800907 today.
2. **Add in-band status checking everywhere:** treat status != 0 as failure and log msg (fetch_plaud.py:720, :1154, :630).
3. **Short term only:** stop forcing is_reload:1; verify against POST /file/list trans_result instead of transaction_polish; accept the web UI will not reflect names until the v4 write exists.
4. **Still fix regardless:** one PATCH with the full mapping instead of N (:1221-1223); the fake "retrying" message that never retries (:1239-1249); the free-text rename heuristic (:1106-1123); sync_speaker reporting success without checking the body (:601-643). Speaker registry holds one profile ("O'Hara", last updated 2026-10-09); auto-labeling dead, consistent with the same cutover.
5. **Upstream:** the 4.0 store split and the undocumented segment_uid field are Plaud-side; worth a support ticket if the v4 endpoint shape (from a third-party client, unverified here) proves wrong.

## Confidence (corrected)
High that the account is on 4.0 and the legacy write is not authoritative (own live probes: -1800907 on v4 routes, legacy routes answering). Medium on the exact v4 endpoint shape, which comes from public GitHub clients, not Plaud's changelog, and is unverified here. Break window and code-path references from the first report remain correct.

## Open gaps
- Direct proof of changed-value overwrite within seconds not closed (same-value re-send was blocked by the permission classifier because the mapping was reconstructed rather than read from the run record)
- The no-op PATCH diagnostic bumped version/edit_time on 3f30d76f... and set edit_from=web (no data changed, transaction S3 object rewritten with identical content)

## Decisions pending with David
- Implement fixes 1-5 (Rigby capability build, gated paths)
- Whether to report upstream to Plaud

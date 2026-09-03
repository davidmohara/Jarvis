---
status: completed
started-at: "2026-08-23T00:12:00Z"
completed-at: "2026-08-23T00:13:00Z"
model: haiku
outputs:
  already-ready: 1
  triggered: 0
  pending: 0
  skipped: 0
  gate_3_result: "pass"
  gate_3_retry_counts: {}
  gate_3_aborted_recordings: []
  note: "1 new recording (32c80d61ff44bb53825a93cfb0bbfa5a) already has transcript ready. No trigger needed. Proceeding to speaker identification."
---

<!-- system:start -->
# Step 02: Trigger Transcription

## MANDATORY EXECUTION RULES

1. You MUST process every recording in `accumulated-context.new-recordings`.
2. For `missing` recordings: trigger transcription immediately — do not skip.
3. For `pending` recordings: check current status. If still pending, add to pending queue.
4. For `ready` recordings: no action needed — pass through to step-03.
5. Do NOT wait here for pending transcriptions to complete — spawn the watcher and move on.
6. Do NOT proceed to step-03 until all `missing` recordings have been triggered and state is updated.

---

## EXECUTION PROTOCOL

**Agent:** Knox
**Skill:** `skills/plaud-trigger/SKILL.md` — read it in full before executing this step.
**Input:** `accumulated-context.new-recordings`
**Output:** `accumulated-context.transcription-triggered`, `accumulated-context.pending-recordings`, `accumulated-context.ready-for-fetch` (partial — will be finalized in step-03)

---

## YOUR TASK

### Sequence

1. **Partition new-recordings by status:**
   - `ready` → add to `ready-for-fetch` immediately
   - `pending` → re-check status via API; if still pending, add to `pending-recordings`
   - `missing` → trigger transcription per `skills/plaud-trigger/SKILL.md`

2. **For each `missing` recording:** execute the two-step trigger:
   - `PATCH /file/{file_id}` with `tranConfig` to save settings
   - `POST /ai/transsumm/{file_id}` with `is_reload: 0` to start the pipeline
   - Both steps required — PATCH alone does nothing
   - On success: add to `transcription-triggered` AND `pending-recordings`
   - On `status=-1` or `status=-12`: do NOT debug. Ask David: "Are you out of Plaud transcription minutes?" Log and skip.

3. **For each `pending` recording (including newly triggered):** spawn a watcher sub-agent per the protocol in `skills/plaud-transcripts/SKILL.md` under "Transcription watcher". The sub-agent polls every 2 minutes (max 30 retries) and, when ready, writes the transcript to staging and notifies Knox.

4. **Update state.yaml:**
   - `accumulated-context.transcription-triggered` = file_ids triggered this run
   - `accumulated-context.pending-recordings` = file_ids still awaiting transcript
   - `accumulated-context.ready-for-fetch` = file_ids already ready (does NOT include pending — those arrive via watcher)
   - `current-step: step-03`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

5. **Report:**
   ```
   [Knox/Trigger]: Transcription status:
     Already ready: N
     Triggered now: N (will arrive in staging when Plaud finishes)
     Still pending: N (watcher running)
     Skipped (minutes exhausted): N
   ```

---

## WATCHER HANDOFF

When a watcher sub-agent completes and drops a transcript in staging, it should:
1. Write the staged file path to `accumulated-context.staged-files` in state.yaml
2. If the workflow is still at step-03 or `awaiting-input`: the file will be picked up when the workflow resumes
3. If the workflow has already reached step-05: Knox should process the late-arriving file immediately inline

---

## QUALITY GATE 3 — Transcription Success (HARD, PER-RECORDING RETRY, ABORT AFTER 3 TRIES)

This gate applies to the two-step trigger protocol in `skills/plaud-trigger/SKILL.md` (PATCH
`/file/{file_id}` to save config, then POST `/ai/transsumm/{file_id}` to actually start the
job — PATCH alone does nothing, per that skill). It does **not** change the `status: -1`/
`status: -12` handling below — that remains a no-retry, ask-David-about-minutes case, exactly
as `plaud-trigger`'s own error table specifies. This gate governs everything else that can go
wrong in the two-step call: non-200 on the PATCH, a timeout on the POST, or a malformed/
unexpected response.

**Retry protocol per recording:**

1. Attempt the two-step trigger (PATCH then POST).
2. If it fails with anything other than `status: -1`/`status: -12`: wait 2 seconds, retry.
3. Track the attempt count for this `file_id` in this step's frontmatter `outputs.gate_3_retry_counts` (e.g. `{"<file_id>": 2}`).
4. After **3 failed attempts** for the same recording: **HARD STOP for that recording.**
   - Do not add it to `transcription-triggered` or `pending-recordings`.
   - Add its `file_id` to `outputs.gate_3_aborted_recordings`.
   - Log to the error tracking system per `Error Logging` conventions.
   - Continue processing the remaining recordings in `new-recordings` — one recording's
     repeated failure does not stop the others, consistent with this step's existing
     partition-and-continue design.
5. If **every** `missing` recording this run hits the 3-retry abort (i.e. `gate_3_aborted_recordings` covers the entire `missing` partition and nothing was triggered or already-ready), treat that as a workflow-level signal rather than a per-recording one: set `state.yaml status: blocked`, write a `blocker` describing the pattern (likely a systemic API issue, not per-recording bad luck), and report to the controller before proceeding to step-03.

**Distinguishing from the `-1`/`-12` minutes case:** if the POST ever returns `status: -1` or
`status: -12`, stop immediately (do not spend retries on it) — surface "Are you out of Plaud
transcription minutes?" per the existing rule in this step's YOUR TASK section 2, and do not
count it toward or against the Gate 3 retry budget. Gate 3 retries are for transient/
unexpected failures only.

Log the outcome per recording:
```
[Gate 3] <file_id>: attempt 1 — FAIL (non-200 on PATCH). Retrying.
[Gate 3] <file_id>: attempt 2 — PASS. Triggered.
```
or on exhaustion:
```
[Gate 3] <file_id>: attempt 3 — FAIL. Retry budget exhausted. Excluding from this run.
```

Write final tallies to this step's frontmatter:
```yaml
outputs:
  gate_3_result: "pass" | "pass-with-exclusions" | "blocked"
  gate_3_retry_counts: {"<file_id>": <int>, ...}
  gate_3_aborted_recordings: ["<file_id>", ...]
```

---

## SUCCESS METRICS

- All `missing` recordings have transcription triggered
- All `pending` recordings have watcher sub-agents running
- `ready-for-fetch` populated with immediately available recordings
- No recording left in an untracked state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Trigger API returns `status=-1` or `status=-12` | Ask David about transcription minutes. Log to error-log. Skip this recording. Not counted against Gate 3's retry budget — see Gate 3 above. |
| Trigger API timeout or other transient failure | Covered by Gate 3's 3-attempt retry budget above. After 3 failed attempts for the same recording, exclude it (`gate_3_aborted_recordings`) rather than adding it to `pending-recordings` on a guess. |
| All recordings are pending/triggered, none ready | Proceed to step-03 with empty ready list. Step-03 may still have speaker files to resolve from a prior partial run. |
| Every `missing` recording exhausts Gate 3's retry budget this run | Treat as systemic, not per-recording. Set `state.yaml status: blocked`, report to controller before proceeding to step-03. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py plaud-ingest step-02-trigger-transcription complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03-identify-speakers.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

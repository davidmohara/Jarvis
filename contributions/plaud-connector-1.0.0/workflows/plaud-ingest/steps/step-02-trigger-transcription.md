---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

**Agent:** Knowledge Manager (Knox)
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
   - On `status=-1` or `status=-12`: do NOT debug. Ask the controller: "Are you out of Plaud transcription minutes?" Log and skip.

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

## SUCCESS METRICS

- All `missing` recordings have transcription triggered
- All `pending` recordings have watcher sub-agents running
- `ready-for-fetch` populated with immediately available recordings
- No recording left in an untracked state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Trigger API returns `status=-1` or `status=-12` | Ask controller about transcription minutes. Log to error-log. Skip this recording. |
| Trigger API timeout | Retry once. If still fails, add to `pending-recordings` and spawn watcher anyway (watcher will detect when ready). |
| All recordings are pending/triggered, none ready | Proceed to step-03 with empty ready list. Step-03 may still have speaker files to resolve from a prior partial run. |

---

## NEXT STEP

Read fully and follow: `step-03-identify-speakers.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

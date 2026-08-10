---
status: waiting
started-at: "2026-08-10T00:22:00Z"
completed-at: null
model: haiku
outputs:
  fetch-status: "no-ready-recordings"
  staging-verified: false
  files-staged: 0
  speaker-renames-applied: 0
  notes: "No recordings are ready for fetch — all 88 new recordings still have transcription pending (trans_status=0). Step-04 will resume once transcriptions complete and transcripts arrive in staging. Workflow is now in a waiting state monitoring for transcript completion via polling or webhook."
---

<!-- system:start -->
# Step 04: Fetch Recordings to Staging

## MANDATORY EXECUTION RULES

1. You MUST run `fetch_plaud.py` for the target date — do not assume staging already has everything.
2. You MUST apply speaker renames before writing final staged files — the script automatically triggers regeneration if needed.
3. You MUST process all recordings in `ready-for-fetch`, not just the ones with speaker mappings.
4. The script will verify speaker names appear in the transcript and trigger regeneration if they don't — wait for this to complete.
5. Do NOT proceed to step-05 until all ready recordings are in staging with correct speaker names.

---

## EXECUTION PROTOCOL

**Agent:** Knox
**Tool:** `skills/plaud-transcripts/scripts/fetch_plaud.py` via osascript on host Mac
**Input:** `accumulated-context.target-date`, `accumulated-context.ready-for-fetch`, `accumulated-context.speaker-mappings`
**Output:** `accumulated-context.staged-files` — list of markdown files written to staging

---

## YOUR TASK

### Sequence

1. **Run the fetch script** for the target date:
   ```
   do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py <target-date> 2>&1"
   ```
   Where `<skill-scripts-dir>` is `skills/plaud-transcripts/scripts/` resolved to absolute path.
   This downloads transcripts for all ready recordings to `~/Downloads/transcript-staging/`.

2. **Apply speaker renames** for any recording in `accumulated-context.speaker-mappings`:
   - For each file_id with a mapping, run the rename command:
     ```
     do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py --rename <file_id> '<JSON-mapping>' 2>&1"
     ```
     Where `<JSON-mapping>` is a JSON object: `{"Speaker 1": "Real Name", "Speaker 2": "Other Name"}`
   - The `--rename` mode:
     1. Renames speaker labels in the Plaud file record (PATCH /file/{file_id})
     2. Registers voice embeddings with Plaud for future auto-labeling
     3. Verifies that renamed speakers appear in the downloaded transcript
     4. **If names are missing from the transcript**: automatically triggers transcript regeneration (POST /ai/transsumm with is_reload: 1)
     5. Re-fetches and overwrites the staged file with corrected speaker names
   - Run renames sequentially (one at a time) — they hit the Plaud API and must not race.
   - **Do not interrupt**: The script handles verification and regeneration automatically. Wait for each rename to complete (may take 5-10 seconds if regeneration is triggered).

3. **Verify staging files.** After all fetches and renames:
   - List `~/Downloads/transcript-staging/plaud_*.md` files
   - Cross-reference against `ready-for-fetch` — confirm every expected recording has a staged file
   - Note any gaps (recording in ready-for-fetch but no staged file found)

4. **Update state.yaml:**
   - `accumulated-context.staged-files` = list of staged markdown filenames
   - `current-step: step-05`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

5. **Report:**
   ```
   [Knox/Fetch]: Staging complete.
     Files ready: N
     Speaker renames applied: N
     Gaps (expected but missing): N
   ```

---

## TOKEN HANDLING

If `fetch_plaud.py` exits with `NO_TOKEN`:
1. Run the Chrome login flow per `skills/plaud-transcripts/SKILL.md`.
2. Retry the fetch command once.
3. If still failing, abort and report.

---

## SUCCESS METRICS

- fetch_plaud.py ran for the target date without errors
- All speaker renames applied with automatic verification and regeneration as needed
- New speaker names appear in the final staged markdown files (not generic labels)
- Every recording in `ready-for-fetch` has a corresponding staged markdown file
- `accumulated-context.staged-files` populated with files containing corrected speaker names

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Token expired / NO_TOKEN | Run Chrome login flow, retry once. |
| Rename API fails for one recording | Log the failure, continue with the generic speaker labels for that recording. Note in report. |
| Regeneration triggered but times out | Script will warn and proceed with current transcript. The names may not appear in vault notes — check if retry is needed. |
| Speaker names still missing after regeneration | This is rare. Check Plaud app directly to confirm names are saved. If saved in app, try one more rename pass. |
| Staging file missing after fetch | Log the gap. Proceed with what is available — do not block step-05 for one missing file. |
| Fetch script crashes entirely | Check osascript permissions. Report full error output. Abort and surface to controller. |
| `~/Downloads/transcript-staging/` appears empty or not visible | Before reporting it unreachable, run `ToolSearch` for `mcp__Desktop_Commander__list_directory` / `mcp__Control_your_Mac__osascript` if they aren't in the active tool list — an empty result via those tools is a valid "nothing staged" outcome, not an access failure. A sandboxed bash mount not covering `~/Downloads` is a different problem and is not evidence the path is unreachable. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py plaud-ingest step-04-fetch-staging complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-05-ingest-vault.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

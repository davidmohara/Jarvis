---
status: completed
started-at: "2026-11-03T16:02:00Z"
completed-at: "2026-11-03T16:14:00Z"
session-id: pi-20261103-001
model: haiku
outputs:
  files_ready: 3
  speaker_renames_applied: 3
  renames_persisted: 0
  gaps: 0
---

<!-- system:start -->
# Step 04: Fetch Recordings to Staging

## MANDATORY EXECUTION RULES

1. You MUST run `fetch_plaud.py` for the target date — do not assume staging already has everything.
2. You MUST apply speaker renames before writing final staged files. The script sends one PATCH per recording with the full segment array, then verifies the names against the database copy of `trans_result` (via `POST /file/list`). It does NOT regenerate by default.
3. You MUST process all recordings in `ready-for-fetch`, not just the ones with speaker mappings.
4. Regeneration (`POST /ai/transsumm` with `is_reload: 1`) fires ONLY on a genuine database verification failure, never because a rendered layer looks stale. When it does fire, the script polls and reports honestly. Read the final `RENAME_STATUS=` line (`verified`, `unverified`, or `failed`) to know what actually happened.
5. Do NOT proceed to step-05 until all ready recordings are in staging. Record the `RENAME_STATUS` for each renamed recording in your report; `unverified` or `failed` is a known Plaud 4.0 condition, not something a re-run fixes (see `reference/plaud-v4-rewrite-plan.md`).

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session.
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
     1. Renames speaker labels with a single PATCH to the legacy `/file/{file_id}` route, sending the full segment array for the recording
     2. Registers voice embeddings with Plaud for future auto-labeling (skipped when the account returns no embeddings)
     3. Verifies segment-level names in the database copy of `trans_result` via `POST /file/list`, using `original_speaker` as the stable key. Two bounded attempts plus a confirming re-read after a settle pause catch Plaud's async revert.
     4. **Only on genuine verification failure**: triggers regeneration (`POST /ai/transsumm` with `is_reload: 1`), polls, and re-verifies
     5. Renders the staged markdown from the database `trans_result` segments, so the vault gets the verified names even when the web UI lags
     6. Prints `RENAME_STATUS=verified|unverified|failed`
   - Run renames sequentially (one at a time) — they hit the Plaud API and must not race.
   - **Do not interrupt**: wait for each rename to finish and capture its `RENAME_STATUS` line. A rename can take up to ~2-3 minutes when regeneration fires. Under Plaud 4.0 the legacy PATCH may be accepted (`status: 0`) yet not persist; that reports as `unverified` and is not fixed by retrying.

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
- All speaker renames applied; each reports a `RENAME_STATUS` line that is captured in the report
- Renames that report `verified` have the new names in the staged markdown; `unverified` or `failed` are reported as such, not glossed over
- Every recording in `ready-for-fetch` has a corresponding staged markdown file
- `accumulated-context.staged-files` populated with the staged markdown files

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Token expired / NO_TOKEN | Run Chrome login flow, retry once. |
| Rename API fails for one recording | Log the failure (`RENAME_STATUS=failed`), continue with the current speaker labels for that recording. Note in report. |
| Rename PATCH accepted but `RENAME_STATUS=unverified` | Known Plaud 4.0 behavior: the legacy PATCH returns `status: 0` but the 4.0 pipeline does not treat that store as authoritative. Do NOT retry blindly. Report the status and point to `reference/plaud-v4-rewrite-plan.md`. |
| Regeneration triggered and times out | Script reports the failure honestly and leaves the staged transcript on the current labels. Report it; a retry is not guaranteed to help for the same 4.0 reason. |
| Staging file missing after fetch | Log the gap. Proceed with what is available — do not block step-05 for one missing file. |
| Fetch script crashes entirely | Check osascript permissions. Report full error output. Abort and surface to controller. |
| `~/Downloads/transcript-staging/` appears empty or not visible | Before reporting it unreachable, run `ToolSearch` for `mcp__Desktop_Commander__list_directory` / `mcp__Control_your_Mac__osascript` if they aren't in the active tool list — an empty result via those tools is a valid "nothing staged" outcome, not an access failure. A sandboxed bash mount not covering `~/Downloads` is a different problem and is not evidence the path is unreachable. |

---


## NEXT STEP

Read fully and follow: `step-05-ingest-vault.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
status: completed
started-at: "2026-04-15T00:00:00Z"
completed-at: "2026-04-15T12:00:00Z"
model: haiku
outputs:
  staged-files:
    - "plaud_04-14 Strategic Perspective on AI Growth and Business Adoption.md"
  speaker-renames-applied: 3
  gaps: 0
---

<!-- system:start -->
# Step 04: Fetch Recordings to Staging

## MANDATORY EXECUTION RULES

1. You MUST run `fetch_plaud.py` for the target date — do not assume staging already has everything.
2. You MUST apply speaker renames before writing final staged files — the rename must happen in Plaud, then re-fetch.
3. You MUST process all recordings in `ready-for-fetch`, not just the ones with speaker mappings.
4. Do NOT skip the re-fetch after rename — staging must reflect the corrected speaker names.
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
   - The `--rename` mode: renames speaker labels in Plaud, registers voice embeddings for future auto-labeling, then re-fetches and overwrites the staged file.
   - Run renames sequentially (one at a time) — they hit the Plaud API and must not race.

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
- All speaker renames applied and re-fetched
- Every recording in `ready-for-fetch` has a corresponding staged markdown file
- `accumulated-context.staged-files` populated

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Token expired / NO_TOKEN | Run Chrome login flow, retry once. |
| Rename API fails for one recording | Log the failure, continue with the generic speaker labels for that recording. Note in report. |
| Staging file missing after fetch | Log the gap. Proceed with what is available — do not block step-05 for one missing file. |
| Fetch script crashes entirely | Check osascript permissions. Report full error output. Abort and surface to controller. |

---

## NEXT STEP

Read fully and follow: `step-05-ingest-vault.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

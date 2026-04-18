---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 05: Ingest to KMS

## MANDATORY EXECUTION RULES

1. You MUST follow `skills/plaud-transcripts/SKILL.md` exactly for every staged file — no shortcuts.
2. You MUST use the KMS adapter configured by the `kms` key in `config/settings.json` — do not hardcode a specific KMS.
3. You MUST cross-reference each note against today's calendar for action items before routing to OmniFocus.
4. You MUST link every meeting note to the daily note in the KMS.
5. You MUST clean up staging after all notes are successfully written.
6. Do NOT mark this step complete until staging is clean and all notes are confirmed written to KMS.

---

## EXECUTION PROTOCOL

**Agent:** Knowledge Manager (Knox)
**Skill:** `skills/plaud-transcripts/SKILL.md` — read it in full before executing this step.
**Input:** `accumulated-context.staged-files`, KMS access via configured adapter
**Output:** `accumulated-context.ingested-notes` — KMS paths of all written notes

---

## YOUR TASK

### Sequence

1. **Determine KMS adapter.** Read `config/settings.json` → `kms` key. Load conventions from
   `skills/plaud-transcripts/references/vault-conventions.md`. All KMS writes in this step
   use the adapter operations defined there — not hardcoded tool calls.

2. **Process each staged file** per `skills/plaud-transcripts/SKILL.md` steps 2 onward (discovery already done):
   - Parse the staged markdown (title, date, duration, summary, transcript)
   - Match to calendar event (using dataverse-configured connector) for attendees and "real" meeting title
   - Transform into KMS note format with correct frontmatter tags
   - Rewrite AI summary in the KMS's analytical style
   - Route to correct subfolder (Client / Improving / YPO / Other)
   - Check for filename collisions

3. **Write notes to KMS** via the configured adapter.
   - Confirm each write succeeds before moving to the next file.
   - On collision with a Teams-sourced note: append ` (Plaud)` suffix.

4. **Link to daily note** per `skills/plaud-transcripts/SKILL.md` step 6.
   - Find or create the daily note at the path defined in `kms.daily_note_path_pattern`
   - Append link for each meeting note written today

5. **Route action items to OmniFocus** per the `omnifocus-tasks` skill.
   - Extract action items from each note's transcript and summary
   - Cross-reference with today's calendar — items that hit today go to the top
   - Create tasks with proper project and tag assignment

6. **Cross-reference recent transcripts with today's calendar** (this is the intelligence payoff):
   - Scan all notes ingested today AND the last 7 days of KMS meeting notes
   - Look for commitments keyed to today's date ("I'll follow up Friday", "send that by end of week")
   - Surface any matches in the final report — these are the lead items, not footnotes

7. **Clean up staging** per `skills/plaud-transcripts/SKILL.md` step 7:
   - Delete processed `plaud_*.md` files
   - Delete corresponding `plaud_*_raw.json` files
   - Leave scripts and config intact

8. **Update state.yaml:**
   - `accumulated-context.ingested-notes` = list of KMS paths written
   - `status: complete`
   - `current-step: step-05`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

9. **Final report:**
   ```
   [Knox/Ingest]: Plaud ingest complete.

   Processed X recording(s):
   ✓ Recording Title → <kms-root>/Improving/2026-04-15 Recording Title.md
   ✓ Another Recording → <kms-root>/Client/2026-04-15 Another Recording.md

   Action items routed to OmniFocus: N
   Staging cleanup: X transcript files removed

   Follow-up intelligence:
   - "Recording Title" (2026-04-08): committed to sending proposal by Friday (today)
   ```

---

## SUCCESS METRICS

- Every file in `accumulated-context.staged-files` has a corresponding KMS note
- Daily notes updated with links
- Action items in OmniFocus with project and tag assignment
- Staging folder clean
- Calendar cross-reference surfaced any date-relevant commitments

## FAILURE MODES

| Failure | Action |
|---------|--------|
| KMS write fails | Retry once. If still fails, report the file and skip — do NOT leave staging dirty. Move the staged file to `~/Downloads/transcript-staging/failed/` for manual recovery. |
| OmniFocus task creation fails | Log the action items in the report. User can manually create. Do not block KMS write. |
| Daily note path doesn't exist | Create the year/month folder structure and note from template. |
| Staging cleanup fails | Report the files that couldn't be deleted. Do not re-process them on next run (check KMS for duplicates first). |

---

## WORKFLOW COMPLETE

When this step finishes, the plaud-ingest workflow is done. Set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

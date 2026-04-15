---
status: completed
started-at: "2026-04-15T12:00:00Z"
completed-at: "2026-04-15T12:30:00Z"
model: sonnet
outputs:
  ingested-notes:
    - "zzPlaud/YPO/2026-04-14 Strategic Perspective on AI Growth and Business Adoption.md"
  daily-note-updated: "Calendar/2026/04-April/2026-04-14.md"
  omnifocus-tasks-created: 0
  staging-files-removed: 4
---

<!-- system:start -->
# Step 05: Ingest to Vault

## MANDATORY EXECUTION RULES

1. You MUST follow `skills/plaud-transcripts/SKILL.md` exactly for every staged file — no shortcuts.
2. You MUST cross-reference each note against today's calendar for action items before routing to OmniFocus.
3. You MUST link every meeting note to the daily calendar note in the vault.
4. You MUST clean up staging after all notes are successfully written.
5. Do NOT mark this step complete until staging is clean and all notes are confirmed written to vault.

---

## EXECUTION PROTOCOL

**Agent:** Knox
**Skill:** `skills/plaud-transcripts/SKILL.md` — read it in full before executing this step.
**Input:** `accumulated-context.staged-files`, vault access via Obsidian MCP
**Output:** `accumulated-context.ingested-notes` — vault paths of all written notes

---

## YOUR TASK

### Sequence

1. **Process each staged file** per `skills/plaud-transcripts/SKILL.md` steps 2 onward (discovery already done):
   - Parse the staged markdown (title, date, duration, summary, transcript)
   - Match to calendar event for attendees and "real" meeting title
   - Transform into vault note format with correct frontmatter tags
   - Rewrite AI summary in vault's analytical style
   - Route to correct `zzPlaud/` subfolder (Client / Improving / YPO / Other)
   - Check for filename collisions

2. **Write notes to vault** via Obsidian MCP.
   - Confirm each write succeeds before moving to the next file.
   - On collision with a Teams-sourced note: append ` (Plaud)` suffix.

3. **Link to daily calendar note** per `skills/plaud-transcripts/SKILL.md` step 6.
   - Find or create the daily note at `Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md`
   - Append wikilink for each meeting note written today

4. **Route action items to OmniFocus** per `skills/omnifocus-tasks/SKILL.md`.
   - Extract action items from each note's transcript and summary
   - Cross-reference with today's calendar — items that hit today go to the top
   - Create tasks with proper project and tag assignment

5. **Cross-reference recent transcripts with today's calendar** (this is the intelligence payoff):
   - Scan all notes ingested today AND the last 7 days of `zzPlaud/` notes
   - Look for commitments keyed to today's date ("I'll follow up Friday", "send that by end of week")
   - Surface any matches in the final report — these are the lead items, not footnotes

6. **Clean up staging** per `skills/plaud-transcripts/SKILL.md` step 7:
   - Delete processed `plaud_*.md` files
   - Delete corresponding `plaud_*_raw.json` files
   - Leave scripts and config intact

7. **Update state.yaml:**
   - `accumulated-context.ingested-notes` = list of vault paths written
   - `status: complete`
   - `current-step: step-05`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

8. **Final report:**
   ```
   [Knox/Ingest]: Plaud ingest complete.

   Processed X recording(s):
   ✓ Recording Title → zzPlaud/Improving/2026-04-15 Recording Title.md
   ✓ Another Recording → zzPlaud/Client/2026-04-15 Another Recording.md

   Action items routed to OmniFocus: N
   Staging cleanup: X transcript files removed

   Follow-up intelligence:
   - "Recording Title" (2026-04-08): David committed to sending proposal by Friday (today)
   ```

---

## SUCCESS METRICS

- Every file in `accumulated-context.staged-files` has a corresponding vault note
- Daily calendar notes updated with wikilinks
- Action items in OmniFocus with project and tag assignment
- Staging folder clean
- Calendar cross-reference surfaced any date-relevant commitments

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Obsidian MCP write fails | Retry once. If still fails, report the file and skip — do NOT leave staging dirty. Move the staged file to `~/Downloads/transcript-staging/failed/` for manual recovery. |
| OmniFocus task creation fails | Log the action items in the report. User can manually create. Do not block vault write. |
| Daily note path doesn't exist | Create the year/month folder structure and note from template. |
| Staging cleanup fails | Report the files that couldn't be deleted. Do not re-process them on next run (check vault for duplicates first). |

---

## WORKFLOW COMPLETE

When this step finishes, the plaud-ingest workflow is done. Set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

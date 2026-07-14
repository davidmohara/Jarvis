---
status: completed
started-at: "2026-07-13T15:10:00Z"
completed-at: "2026-07-13T15:30:00Z"
model: sonnet
outputs:
  ingested-notes:
    - "zzPlaud/Improving/2026-07-10 Aligning on a Centralized AI Agent Landing Zone.md"
  daily-note-updated: "Calendar/2026/07-July/2026-07-10.md"
  monday-tasks-created: 5
  staging-files-removed: 4
  notes: "Speaker 2 resolved as Michael Slater (michael.slater@improving.com) via M365 calendar lookup — calendar event 'Review Improving Landing Zone' Jul 10 20:00-20:30 UTC. Rename succeeded on first attempt (PATCH applied) but script exited code 1 due to transient /file/list API response; re-ran rename which skipped the already-applied PATCH and completed the re-fetch. Created daily note Calendar/2026/07-July/2026-07-10.md (did not exist). Cleanup scoped to 4 files (1 named .md + 1 ID-named .md + 1 _raw.json + 1 _speakers.json) for this session's recording; legacy backlog untouched per prior convention."
---

<!-- system:start -->
# Step 05: Ingest to Vault

## MANDATORY EXECUTION RULES

1. You MUST follow `skills/plaud-transcripts/SKILL.md` exactly for every staged file — no shortcuts.
2. You MUST cross-reference each note against today's calendar for action items before routing to Monday.
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

4. **Route action items to Monday** via `mcp__ae67c963-c9a1-4a47-9243-3f91556e1532__create_item`.
   - Extract action items from each note's transcript and summary
   - Cross-reference with today's calendar — items that hit today go to the top
   - For each action item, call `mcp__ae67c963-c9a1-4a47-9243-3f91556e1532__create_item` with:
     - `boardId`: `18420619069`
     - `groupId`: `new_group29179`
     - `name`: the action item text (concise, imperative phrasing)
     - `columnValues`: set `project_status` to "Not Started", `priority` to "Medium" by default (use "High" if the transcript flags the item as urgent), `date` to the due date if one was mentioned in the transcript (otherwise omit it), `text_mm50v09n` to the source recording title and date (e.g., "From: 2026-07-01 Nexben Discussion")
   - No project/tag gate required — Monday does not enforce that prerequisite
   - Log count of tasks created in the final report

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

   Action items routed to Monday: N
   Staging cleanup: X transcript files removed

   Follow-up intelligence:
   - "Recording Title" (2026-04-08): David committed to sending proposal by Friday (today)
   ```

---

## SUCCESS METRICS

- Every file in `accumulated-context.staged-files` has a corresponding vault note
- Daily calendar notes updated with wikilinks
- Action items created in Monday (board: Work, group: To-Do) with status, priority, and source traceability
- Staging folder clean
- Calendar cross-reference surfaced any date-relevant commitments

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Obsidian MCP write fails | Retry once. If still fails, report the file and skip — do NOT leave staging dirty. Move the staged file to `~/Downloads/transcript-staging/failed/` for manual recovery. |
| Monday task creation fails | Log the action item text in the report. User can manually create. Do not block vault write. |
| Daily note path doesn't exist | Create the year/month folder structure and note from template. |
| Staging cleanup fails | Report the files that couldn't be deleted. Do not re-process them on next run (check vault for duplicates first). |

---

## NEXT STEP

When this step finishes, do NOT mark the workflow complete yet. Update `state.yaml`:
- `current-step: step-05b`
- Leave `status: in-progress`

Then read and follow: `step-05b-share-with-alice.md`

Step-05b handles sharing each ingested recording with Alice Mburu and sends the share links via email. It sets `status: complete` when done.
<!-- system:end -->


## WRITE WORKING MEMORY

After the workflow output has been delivered, write a working memory file to the **IES local filesystem** — NOT the Obsidian vault. Use `mcp__Desktop_Commander__write_file` (Desktop Commander), never the Obsidian MCP server, for this write.

**Absolute path:**
```
/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/memory/working/plaud-ingest-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing. Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chief-{YYYY-MM-DD}-{HHmmss}"
agent-source: chief
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Plaud ingest summary — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

---
<!-- personal:start -->
<!-- personal:end -->

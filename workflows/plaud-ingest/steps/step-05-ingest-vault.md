---
status: completed
started-at: "2026-09-14T00:00:00Z"
completed-at: "2026-09-14T00:00:00Z"
model: sonnet
outputs:
  ingested-notes:
    - "zzPlaud/Improving/2026-09-14 Summer Craig Call - ACG Houston Speaking Engagement Planning.md"
    - "zzPlaud/Improving/2026-09-14 Sync AI Executive Workshop in California (Ashok Iyengar).md"
    - "zzPlaud/Improving/2026-09-14 Syncing Up Devlin and O'Hara - Production Hosting Handoff, Capacity Risk, and October Boot Camp Planning.md"
  daily-notes-updated:
    - "Calendar/2026/09-September/2026-09-14.md"
  monday-tasks-created: 0
  monday-tasks-logged-manual: 12
  staging-files-removed: 11
  gate_5_result: "pass"
  gate_5_verification_failures: []
  notes: >
    pi-20260914-001: 3 recordings ingested, all classified work, all filed
    to zzPlaud/Improving/ (internal Improving meetings/BD, no client or
    personal recordings in this batch). (1) 9bb5788628b16838019203e248399df3
    — ACG Houston speaking-engagement planning call with Summer Craig
    (ACG Houston board member); speakers left as "David O'Hara"/"Summer
    Craig" per plan (no mapping needed, "Speaker 2" identified from context
    and calendar match). (2) 66df23aef3712ab857d5a656c67ba763 — Executive AI
    Workshop planning sync with Ashok Iyengar; speaker labels normalized
    from staged "O'Hara"/"Ashok Iyengar" to full names per vault convention.
    (3) 97b419ebfe3fd7ed84ac820a3343fef7 — Production hosting handoff/
    capacity-risk/October boot camp planning with Devlin Liles; Robyn
    Fuentes also appears mid-call with brief interjections despite not
    being on the calendar invite (edge case #4 — caller set differs from
    invite). All 3 matched to real calendar events (Summer Craig call,
    "Sync: AI Executive Workshop in California", "Syncing Up: Devlin &
    O'Hara") for real titles/attendees/times. Duration fields in the staged
    .md files are mislabeled — the numeric value is milliseconds, not
    seconds as the "s" suffix implies; duration_minutes computed as
    raw_value / 1000 / 60 for all 3 notes (confirmed against transcript
    timestamp ranges). Gate 5 verified for all 3: read back via
    get_vault_file (markdown format — json format threw a pre-existing
    tool-side type-validation error on tags/duration_minutes, same as seen
    on the 2026-09-03 note; not a data issue), confirmed file_id/date/
    source/tags frontmatter and correct path for each. Daily note
    Calendar/2026/09-September/2026-09-14.md created fresh (didn't exist)
    with wikilinks to all 3 notes. Monday task creation was NOT possible
    this run — the create_item tool for board 18420619069 was not
    reachable in this session (only the unauthenticated claude_ai
    monday_com OAuth tools were available); per the standard Monday-
    failure-mode handling, all 12 action items across the 3 notes were
    logged in the final report for manual creation instead of blocking the
    vault write. Staging cleanup: removed 11 files — the 8 files (3×.md,
    3×_raw.json, 2×_speakers.json) explicitly listed in
    accumulated-context.staged-files, plus 3 more (plaud_2026-09-14
    14_03_46.md/_raw.json/_speakers.json) discovered to be an untracked
    duplicate of recording (1) under its pre-rename auto-generated
    timestamp filename (identical file_id, duration, and transcript
    content) — confirmed as part of this session's output, not the
    unrelated pre-existing backlog, before deleting. Follow-up
    intelligence: Sunday Texans-game commitment to Summer Craig + husband,
    and Wednesday Simpson Strong-Tie leadership-sync coverage commitment to
    Devlin, both surfaced in the final report as this-week action items.
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
   - **Route to correct `zzPlaud/` subfolder based on classification:**
     - **Personal recordings** → `zzPlaud/Personal/` (doctor appointments, personal lunch, wellness, etc.)
     - **Work recordings** → `zzPlaud/Client/`, `zzPlaud/Improving/`, `zzPlaud/YPO/`, or `zzPlaud/Other/` based on meeting context
   - Check for filename collisions

2. **Write notes to vault** via Obsidian MCP.
   - Confirm each write succeeds before moving to the next file.
   - On collision with a Teams-sourced note: append ` (Plaud)` suffix.

2a. **Run QUALITY GATE 5 (see below) for each note just written**, before proceeding to the
    daily-note linking step. Do not treat an Obsidian MCP write returning success as proof the
    note actually landed correctly — verify it.

3. **Link to daily calendar note** per `skills/plaud-transcripts/SKILL.md` step 6.
   - Find or create the daily note at `Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md`
   - Append wikilink for each meeting note written today

4. **Route action items to Monday** via `mcp__ae67c963-c9a1-4a47-9243-3f91556e1532__create_item`.
   - Extract action items from each note's transcript and summary
   - **Handle based on recording classification:**
     - **For WORK recordings:** Create Monday task, assign to Alice Mburu (`107886956`)
     - **For PERSONAL recordings:** Only create Monday task if the action item is actionable (not just notes). Assign to David O'Hara instead (`<user_id>` — do not assign to Alice)
   - Cross-reference with today's calendar — items that hit today go to the top
   - For each action item, call `mcp__ae67c963-c9a1-4a47-9243-3f91556e1532__create_item` with:
     - `boardId`: `18420619069`
     - `groupId`: `new_group29179`
     - `name`: the action item text (concise, imperative phrasing)
     - `columnValues`: 
       - `project_status`: "Not Started"
       - `priority`: "Medium" by default (use "High" if the transcript flags the item as urgent)
       - `date`: due date if mentioned in transcript (otherwise omit)
       - `text_mm50v09n`: source recording title and date (e.g., "From: 2026-07-01 Nexben Discussion — PERSONAL" for personal recordings)
       - `project_owner`: for WORK items, assign to Alice (`107886956`); for PERSONAL items, assign to David
   - No project/tag gate required — Monday does not enforce that prerequisite
   - Log count of WORK and PERSONAL tasks created separately in the final report

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
   ✓ (WORK) Recording Title → zzPlaud/Improving/2026-04-15 Recording Title.md
   ✓ (PERSONAL) Doctor Appointment → zzPlaud/Personal/2026-04-15 Doctor Appointment.md
   ✓ Another Recording → zzPlaud/Client/2026-04-15 Another Recording.md

   Action items routed to Monday:
     - Work items (assigned to Alice): N
     - Personal items (assigned to you): N

   Staging cleanup: X transcript files removed

   Follow-up intelligence:
   - "Recording Title" (2026-04-08): David committed to sending proposal by Friday (today)
   ```

---

## QUALITY GATE 5 — Vault Filing Verification (HARD, ESCALATE ON FAILURE)

This is the terminal "did the work actually land" check for the whole pipeline — everything
upstream (discovery, transcription, speaker ID, staging) exists to produce this one outcome.
An Obsidian MCP write call returning success is not sufficient proof by itself; this gate
independently re-reads what was written.

For every note the sequence just wrote in step 2, before moving on to daily-note linking:

| Check | How to verify | On failure |
|-------|---------------|------------|
| File exists at the expected vault path | Read it back via Obsidian MCP (`get_vault_file` or equivalent) using the exact path just written | **HARD FAIL for this note.** |
| Required frontmatter fields present | Confirm the note's frontmatter includes at minimum: title/date, source tag identifying it as Plaud-sourced, and the `file_id` (or equivalent traceability field back to the recording) | **HARD FAIL for this note.** A note with no way to trace back to its source recording is a dead end for any future audit or cleanup. |
| Expected wikilink connections were actually created, not just attempted | This note's link into the daily calendar note happens in step 3, which runs *after* this gate — so for this gate, check any links this step is itself responsible for (e.g. attendee references, related-project links the transform step adds). Confirm the link target exists and the link syntax is well-formed, not just that the writing step "ran". | **SOFT FAIL for this specific link** — log it, do not block the note's filing on a missing secondary link, but do not silently drop the flag either. |

**On HARD FAIL for a note (missing file or missing required frontmatter):**
1. Do not count that note as successfully ingested — remove it from the `ingested-notes` list you were about to build, or mark it separately as `verification-failed`.
2. Move the corresponding staged file to `~/Downloads/transcript-staging/failed/` for manual recovery (this reuses the existing failure-mode behavior for Obsidian MCP write failures — Gate 5 extends the same handling to writes that *appeared* to succeed but didn't actually land correctly).
3. Log to error tracking.
4. Escalate: surface in the final report as a flagged failure, e.g. `✗ <Recording Title> → vault filing verification FAILED — see gate_5_verification_failures`. Do not silently continue as if the recording were ingested — the controller needs to know this recording did not land.
5. Continue processing the remaining notes — one note's verification failure does not block the others (same continue-on-failure pattern as the rest of this step).

Log the result per note:
```
[Gate 5] <vault path>: file exists ✓, frontmatter complete ✓, links well-formed ✓ — PASS
```
or
```
[Gate 5] <vault path>: FILE NOT FOUND at expected path — HARD FAIL. Staged file moved to failed/. Escalating.
```

Write to this step's frontmatter `outputs`:
```yaml
outputs:
  gate_5_result: "pass" | "pass-with-soft-flags" | "fail"
  gate_5_verification_failures: [{expected_path, reason}, ...]
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
| Gate 5 hard fail (write reported success but file/frontmatter verification fails) | Same recovery as an outright write failure — move staged file to `failed/`, exclude from `ingested-notes`, escalate in final report. Continue with remaining notes. |
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

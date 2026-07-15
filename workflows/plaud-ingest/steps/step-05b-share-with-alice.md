---
status: completed
started-at: "2026-07-13T15:30:00Z"
completed-at: "2026-07-13T15:35:00Z"
model: sonnet
outputs:
  shares-attempted: 1
  shares-succeeded: 1
  shares-failed: 0
  tasks-created: 1
  share-urls:
    - file_id: e5a04131ee46970ac1c70a15cb4ae7ef
      url: "https://web.plaud.ai/s/pub_59ab2e0b-796e-46c8-a9d3-9ad151669774::KT0la9xJYK8lrXplPqAoEJpy4cGKDtRagpue8LvgJI6rrEvD5EDSrL9Q6VEv8DO6XnJ611OoEFg6II8C"
      monday-task-id: "12518555007"
---

<!-- system:start -->
# Step 05b: Share Recordings with Alice Mburu

## MANDATORY EXECUTION RULES

1. You MUST attempt a share for every file_id in `accumulated-context.staged-files` (or derived from `accumulated-context.ingested-notes` cross-referenced with `accumulated-context.speaker-mappings`).
2. A share failure for one recording MUST NOT block the others — log it and continue.
3. You MUST create one Monday task per recording — do not batch multiple recordings into one task.
4. You MUST set `state.yaml status: complete` when this step finishes — this is the final step.
5. Do NOT re-run the share script for a recording that already has a `SHARE_URL=` in its output this session.

---

## EXECUTION PROTOCOL

**Agent:** Knox
**Tool:** `skills/plaud-transcripts/scripts/fetch_plaud.py --share` via Desktop Commander bash, then Monday MCP
**Input:** `accumulated-context.staged-files`, `accumulated-context.ingested-notes`, `accumulated-context.speaker-mappings`, `accumulated-context.recording-classification`
**Output:** Share URLs and Monday task creation status logged in step outputs
**PERSONAL RECORDING HANDLING:** Skip sharing AND skip Monday task creation for any recording marked as `personal: true` in `recording-classification`

---

## YOUR TASK

### Sequence

1. **Filter for work recordings only.** Build the list of file_ids to process:
   - Start with keys from `accumulated-context.speaker-mappings` (keyed by file_id)
   - **SKIP any file_id marked as `personal: true` in `accumulated-context.recording-classification`** — do not share, do not create Monday task
   - Cross-reference remaining file_ids with `accumulated-context.staged-files` to confirm each file was fetched
   - If speaker-mappings is empty, derive file_ids from staged filenames if the raw JSON files contain them
   - Skip any file_id that cannot be resolved — log it
   - Log count of personal recordings skipped (not shared with Alice)

2. **For each file_id, run the share script:**
   ```bash
   cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES && \
   /usr/bin/python3 skills/plaud-transcripts/scripts/fetch_plaud.py --share <file_id> 2>&1
   ```
   - Parse the output for a line matching `SHARE_URL=<url>` — that is the share URL
   - If the output contains `SHARE_FAILED` or `NO_TOKEN`, log the failure and continue to next recording
   - If output contains `NO_TOKEN`: attempt the Chrome login flow per `skills/plaud-transcripts/SKILL.md`, then retry once
   - If share fails, use `"Share link unavailable — check Plaud web app"` as the notes value — still create the Monday task

3. **Resolve the recording title:**
   - Pull from the staged filename or from the vault note path in `accumulated-context.ingested-notes`
   - The title is the human-readable portion of the filename (e.g. `"Nexben Discussion — Platform Modernization and AI Integration"`)
   - If title cannot be resolved, use `file_id` as the fallback label

4. **Create a Monday task for each WORK recording** using `mcp__ae67c963-c9a1-4a47-9243-3f91556e1532__create_item`:
   - **Only process file_ids that passed the filter in step 1** (not marked as personal)
   - **Board ID:** `18420619069`
   - **Group:** `new_group29179` (To-Do)
   - **Item name:** `Review Plaud recording: <recording_title>`
   - **Column values JSON:**
     ```json
     {
       "project_owner": {
         "personsAndTeams": [{"id": 107886956, "kind": "person"}]
       },
       "project_status": {"label": "Not Started"},
       "text_mm50v09n": "<share_url_or_fallback_message>"
     }
     ```
   - Alice Mburu's user ID is `107886956` — hardcode it, do not look it up
   - Log success or failure for each task creation
   - **Note:** Personal recordings do NOT get Monday tasks in this step (they were handled in step-05 if they had actionable items)


5. **Update state.yaml:**
   - `status: complete`
   - `current-step: step-05b`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`
   - Write share results to `outputs`:
     ```yaml
     outputs:
       shares-attempted: N
       shares-succeeded: N
       shares-failed: N
       tasks-created: N
       share-urls:
         - file_id: <id>
           url: <url>
           monday-task-id: <task_id>
     ```

6. **Final report:**
   ```
   [Knox/Share]: Recording share complete.

   Work recordings shared with Alice: N
   Personal recordings (skipped sharing): N

   Shares: N succeeded, N failed
   Monday tasks created for alice.mburu: N

   ✓ <Recording Title> → <share_url> (task ID: <id>)
   ✗ <Recording Title> → SHARE_FAILED — task created with fallback note
   ⊘ <Personal Recording Title> — skipped (personal, not shared)
   ```

---

## SUCCESS METRICS

- Share script ran for every WORK file_id derived from this session's recordings
- Personal recordings correctly identified and skipped (no share, no Alice task)
- One Monday task created per WORK recording (regardless of share success/failure)
- Alice Mburu (`107886956`) assigned as `project_owner` only on WORK recordings
- Personal recordings were already handled in step-05 (vault ingestion + personal task routing if needed)
- state.yaml updated to `status: complete`
- All failures logged in step outputs
- Reports separately: work recordings shared vs. personal recordings skipped

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `NO_TOKEN` on share | Run Chrome login flow, retry once. If still failing, use fallback note in Monday task. |
| `SHARE_FAILED` (API error) | Log file_id and API response snippet. Create Monday task with fallback note. Continue. |
| Monday task creation fails | Log the error and the share URL. Controller can create the task manually. Continue. |
| No file_ids resolvable | Log the issue, mark step complete with 0 tasks — do not abort the workflow. |

---

## NEXT STEP

This is the final step. When complete, set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

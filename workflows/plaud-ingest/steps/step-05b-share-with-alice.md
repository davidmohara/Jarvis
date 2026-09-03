---
status: not-started
model: sonnet
outputs:
  gate_6_result: "pass"
  gate_6_delivery_confirmations: []
  notes: "RESET 2026-08-22: prior 'completed' frontmatter (claiming session pi-20260822-001, a share URL, and a Monday permission blocker) is not corroborated by state.yaml (share-urls/monday-tasks-created were empty) or today's real eval record (only step-01 ran, then the session aborted -- no session pi-20260822-001 exists in the eval log). Treating as stale/unverified and resetting to not-started. This step cannot run until step-04 (fetch to staging) actually completes, which is currently blocked -- see step-04-fetch-staging.md and state.yaml blocker field."
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

4. **Create a Monday task for each WORK recording via `skills/delivery-router/SKILL.md`:**
   - **Only process file_ids that passed the filter in step 1** (not marked as personal)
   - Call the skill once per recording:
     ```yaml
     content: "Review Plaud recording: <recording_title>"
     destinations:
       - backend: "monday"
         required: true
         config:
           board_id: "18420619069"
           group_id: "new_group29179"          # To-Do
           column_values:
             project_owner: { personsAndTeams: [{ id: 107886956, kind: "person" }] }
             project_status: { label: "Not Started" }
             text_mm50v09n: "<share_url_or_fallback_message>"
     ```
   - Alice Mburu's user ID (`107886956`) and the board/group IDs are this workflow's own facts
     — they live in this step's `config`, not inside `delivery-router` itself (the skill is
     shared across workflows and must not hardcode any one caller's board/person).
   - The skill's own retry budget (up to 3 attempts) applies before it reports a failure — do
     not add a second retry loop around it here.
   - Read `delivery_status[0].success`, `.id` (the created task ID), and `.error` from the
     skill's return to populate the per-recording log line and `outputs` below.
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

## QUALITY GATE 6 — Delivery Routing Confirmation (HARD, PER-RECORDING, RENAMED FROM "SLACK ROUTING")

**Naming note for future editors:** this gate was originally specified as a "Slack routing
decision" gate. That does not match this workflow — there is no Slack delivery anywhere in
plaud-ingest today (confirmed by grep across `workflow.md` and every step file; the only
Slack usage in this repo is `master-slack` and other workflows entirely). The actual terminal
delivery in this step is a Plaud public share link plus a Monday task assigning the recording
to Alice Mburu for review — not an email send either, despite the workflow's own goal
statement in `workflow.md` describing it as "share... via email." Rather than inventing new
Slack (or email) behavior that doesn't exist, this gate confirms the delivery path that
**actually runs**: the share-link generation and the Monday task assignment. If David wants a
real email notification or a Slack alert added on top of this, that is new functionality and
a product decision for him, not something to add silently under a gate.

Before marking a recording's delivery complete, confirm for each recording processed in step
4 above, reading from `delivery-router`'s returned `delivery_status` entry rather than
re-deriving these checks against a raw API response:

| Check | Expected | On failure |
|-------|----------|------------|
| Correct recipient | The `config.column_values.project_owner` passed to the skill was Alice Mburu's hardcoded ID `107886956` — not David, not blank, not a different person (verify the config you built in step 4, since the skill just passes it through) | **HARD FAIL.** Do not mark this recording's delivery complete. Log and escalate — a misrouted task defeats the point of this step. |
| Correct destination used | `delivery_status[0].backend == "monday"` and the `config` sent was board `18420619069` / group `new_group29179`, per the existing spec — not some other board or a skipped call | **HARD FAIL** if the skill was never actually called for this recording (e.g. skipped due to an earlier error but not logged as such). |
| Share URL or fallback note present in the task | `config.column_values.text_mm50v09n` contains either a real `SHARE_URL=` value or the documented fallback string `"Share link unavailable — check Plaud web app"` — never blank | **SOFT FAIL** — log it, but the task can still stand (a blank note is a lesser problem than a missing/misrouted task; still flag it since Alice needs *something* to act on). |
| Task creation actually succeeded | `delivery_status[0].success == true` and `.id` is a real task ID, not null | **HARD FAIL** if `success` is `false` or `.error` is set — this is the "did it actually send" check the gate exists for. `delivery-router` has already retried up to 3 times internally by the time it reports this, so a failure here means those retries were exhausted. |

**On HARD FAIL:** do not count that recording toward `tasks-created` in this step's final
tally. Log the failure to `gate_6_delivery_confirmations` with `delivery_status[0].error`, and
escalate in the final report exactly as the existing "Monday task creation fails" failure mode
below already specifies. Do not add a second manual retry loop here — `delivery-router` already
exhausted its own retry budget before returning `success: false`; retrying again at this layer
would just be re-running a call the skill already confirmed fails.

Log per recording:
```
[Gate 6] <file_id>: recipient=Alice Mburu (107886956) ✓, board/group correct ✓, share note present ✓, task ID <id> confirmed — PASS
```
or
```
[Gate 6] <file_id>: task creation returned no ID — HARD FAIL. Retrying once.
```

Write to this step's frontmatter `outputs`:
```yaml
outputs:
  gate_6_result: "pass" | "pass-with-soft-flags" | "fail"
  gate_6_delivery_confirmations: [{file_id, task_id, recipient_confirmed, share_url_present}, ...]
```

Do not set `state.yaml status: complete` (this step's terminal action) while any recording
has an unresolved Gate 6 HARD FAIL still pending retry.

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
| Gate 6 hard fail (wrong recipient, wrong board, or no task ID returned) | `delivery-router` already retried internally (up to 3 attempts) before reporting `success: false` — do not retry again at this layer. Log `delivery_status[0].error` to `gate_6_delivery_confirmations` and escalate in the final report — do not count as delivered. |
| No file_ids resolvable | Log the issue, mark step complete with 0 tasks — do not abort the workflow. |

---

## NEXT STEP

This is the final step. When complete, set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

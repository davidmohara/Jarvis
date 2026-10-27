---
status: complete
started-at: '2026-10-26T14:30:00Z'
completed-at: '2026-10-26T14:53:00Z'
---

<!-- system:start -->
# Step 04.5: Watchtower Daily Hand-off

## MANDATORY EXECUTION RULES

1. This step is a hand-off, not a gather. You run the Watchtower daily pipeline exactly as `workflows/watchtower/workflow.md` defines it (daily mode) and relay its result. You do not re-implement, shorten, or reorder any Watchtower step.
2. Run at most once per calendar day. The ran-today check in YOUR TASK step 1 is the first thing you do; a positive result means reuse, never re-run.
3. A Watchtower failure never blocks the briefing. Every failure path ends with this step's frontmatter `status: complete` and a `watchtower_output` whose `status` says what happened. Never leave the frontmatter `in-progress` or `not-started`.
4. Never write to `workflows/watchtower/seen.jsonl`, `sources.yaml`, `proposed-sources.md`, or any Watchtower file yourself outside what the daily steps instruct. The daily steps own the ledger.
5. Record boot results in `workflows/boot/state.yaml` `accumulated-context` and update this step's frontmatter with the Edit/Write tools, never Bash redirection or heredocs. The eval harness's per-step attribution keys on Edit/Write tool calls.
6. Do not read or execute any boot step file, any morning-briefing file, any Watchtower weekly step, or `SYSTEM.md` / `agents/master.md`. Your mandate is this file plus the Watchtower daily steps (`daily-step-01` through `daily-step-07`, then `daily-step-06`), then exit.

---

## EXECUTION PROTOCOL

**Agent:** dedicated Watchtower hand-off subagent (Knox executing the Watchtower daily steps), spawned by the coordinator (Master) with a tight single-purpose brief, model `sonnet` (steps 03, 04, 04b score and synthesize). It loads no persona file; the daily step files name the only identity files it needs (`identity/VOICE.md`, `identity/MEMORY.md`).
**Input:** `workflows/watchtower/` (workflow, config, state, sources, ledger), today's date
**Output:** `watchtower_output` in `workflows/boot/state.yaml` `accumulated-context`; Watchtower's own outputs (`seen.jsonl`, Obsidian `Watchtower/Daily/YYYY-MM-DD.md`, `source-activity.json`, dashboard) written by the daily steps

---

## CONTEXT BOUNDARIES

- Watchtower daily mode is invoked by this step in a full boot and by `workflows/morning-briefing/` in a standalone briefing run. This step is the boot-side invocation point.
- Watchtower and boot keep separate `state.yaml` files. The daily steps write to `workflows/watchtower/state.yaml`; only this step's final record goes to `workflows/boot/state.yaml`.
- Delta boot never runs this step.
- The weekly run is out of scope. Never start it from here.

---

## YOUR TASK

0. **Open the step.** Set this file's frontmatter `status: in-progress` and `started-at` (Edit tool) before anything else. Both timestamps come from the real clock: `date -u +%Y-%m-%dT%H:%M:%SZ`. Never estimate, round, or backfill. The 2026-10-26 run stamped this step completed 23 minutes after the file was actually written, which collapsed boot's per-step attribution onto this step and nulled steps 05-08.

1. **Ran-today check.** Let `TODAY` be the local date (YYYY-MM-DD). The daily run already completed today when either holds:
   - `workflows/watchtower/state.yaml` has `status: complete` and `session-id: wt-daily-TODAY`.
   - The note `Watchtower/Daily/TODAY.md` exists in the vault (`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian`, read it with the Read tool on the expanded absolute path).

   If it already completed: do not run the pipeline. Rebuild `watchtower_output` (step 4) from the daily note's items (`### [Title](url)` headings, the `*Score: XX | Source: name*` line, the summary paragraph) with `status: reused`, then go to step 5.

2. **Run the daily pipeline.** Read `workflows/watchtower/workflow.md`, run its STATE CHECK in daily mode (the Variant paragraph governs shared state and mode matching), set `session-id: wt-daily-TODAY`, and execute `daily-step-01` through `daily-step-05`, `daily-step-07`, then `daily-step-06` in that order, each per its own step file. Vault writes follow `obsidian_write_method` in the Watchtower `state.yaml`. The daily run opens and closes its own eval record per `workflows/watchtower/workflow.md` → "EVAL RECORD (daily run)"; do not open a second record here, and carry its `eval_id` into `watchtower_output` below.

3. **Verify the ledger.** The silent failure this step exists to prevent is a completed run that never wrote `seen.jsonl`. Using Grep (count mode) on `workflows/watchtower/seen.jsonl` for `"seen_date": "TODAY"`, compare the count with `kept_count` from the Watchtower `accumulated-context`. Record `ledger_check`: `ok` when the count is at least `kept_count`, `mismatch` when it is lower, `n/a` when the pipeline did not reach `daily-step-02`. A mismatch is reported, not repaired: do not edit the ledger.

4. **Record `watchtower_output`** in `workflows/boot/state.yaml` `accumulated-context` with the Edit tool. Quote every string value.
   ```yaml
   watchtower_output:
     status: "ok | no-items | reused | failed"
     date: "YYYY-MM-DD"
     items_surfaced: <int>
     content_candidates: <int>
     scored_items:            # top 5 by score, descending; empty list when none
       - title: "string"
         url: "string"
         source_name: "string"
         score: <int>
         takeaway: "first sentence of the item's summary"
         content_worthy: <bool>
     through_line: "string or empty"
     obsidian_note_path: "Watchtower/Daily/YYYY-MM-DD.md or empty"
     ledger_check: "ok | mismatch | n/a"
     eval_id: "eval-... or empty"
     retirements: []
     failure_reason: "string or empty"
   ```
   `status: no-items` means the run completed with nothing above the awareness floor. `status: failed` means the pipeline did not reach a completed `daily-step-06`; `failure_reason` names the step and the cause.

5. **Update this step's frontmatter** (Edit tool): `status: complete` and `completed-at` = the real UTC clock time from `date -u +%Y-%m-%dT%H:%M:%SZ` (paste the exact output; never estimate or round). Then set `current-step: step-05-synthesize-briefing.md` in `workflows/boot/state.yaml`.

---

## SUCCESS METRICS

- The ran-today check ran first and gated everything else
- On a first run of the day: `seen.jsonl` gained today's kept items, `Watchtower/Daily/TODAY.md` exists, `ledger_check` is recorded
- `watchtower_output` is present in boot's `accumulated-context` on every path, including failure
- No Watchtower weekly step, boot step, or morning-briefing step was read
- This step's frontmatter ends `complete`

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Watchtower `state.yaml` is `in-progress` for a different mode or older than 4 hours | Treat as stale per the Watchtower STATE CHECK Variant: start a fresh daily run. Do not resume a weekly run from here. |
| A daily step fails or its verifier asks for a retry | Retry once per the step's own failure table. If it still fails, close the watchtower eval record as `failure` with an abort reason (if one was opened), stop the pipeline, record `status: failed` with `failure_reason`, complete this step, exit. |
| Obsidian write fails | The daily step's own failure mode applies (fallback file under `workflows/watchtower/fallback/`). Continue; record the path actually written in `obsidian_note_path`. |
| Zero items above the awareness floor | Valid. `status: no-items`, empty `scored_items`. |
| `ledger_check: mismatch` | Record it, include it in the final status line, do not repair the ledger. |
| Spawn, config, or workflow file unavailable | Record `status: failed` with the reason, complete this step, exit. |

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read `step-05-synthesize-briefing.md` or any other boot step file: the coordinator spawns the briefing subagent for steps 05 through 08 after you return. Your final message is a short status report: `watchtower_output.status`, items surfaced, content candidates, `ledger_check`, the eval id, the note path, and any failure. Then stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

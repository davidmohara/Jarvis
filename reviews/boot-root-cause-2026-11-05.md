# Boot Workflow Root-Cause Analysis

Companion to `reviews/boot-cost-review-2026-11-05.md` (same window, 2026-10-15 to 2026-11-05). Diagnosis only: every fix below is a proposal, nothing here is implemented. All file references are absolute under the IES root; line numbers are as of 2026-11-05.

---

## 1. Attribution pipeline failures

The pipeline has three token-capture paths, and each failure mode in the review maps to a specific one:

- **Inline path**: `.claude/hooks/post-tool-use.py` `update_eval_record_step_frontmatter()` (line ~946) fires on every Write/Edit to `workflows/*/steps/*.md`, reads the step's frontmatter `started-at`/`completed-at`, and calls `usage_between(transcript_path, started, completed, lenient_fallback=False)` against the **main session transcript** (`systems/eval-harness/token_usage.py:167`).
- **Subagent stop path**: `.claude/hooks/step-complete.py` `extract_step_tokens()` (line 279), strict window against the subagent's own transcript.
- **Partition backfill**: `token_usage.py` `partition_usage_by_steps()` (line 267), called from `.claude/hooks/eval-agent-stop.py` (line 821), which is the **only** path with a stale-window guard (lines 305-330: a step whose `started-at` predates the run start is labeled `stale-window` and excluded).

All four observed failure modes trace to one shared root: **step frontmatter timestamps are agent-authored, and two of the three paths trust them without validation.**

### 1a. 11-04 back-half corruption (identical 1.87M inputs, ~53h durations)

Mechanism, verified against the live record and the on-disk step files:

- `workflows/boot/steps/step-05` through `step-08` currently carry `started-at: '2026-11-02T16:19-16:22Z'` (stale, from the 11-02 run) with `completed-at: '2026-11-04T21:34-21:35Z'` (fresh). Confirmed by reading the files today.
- On 11-04 the consolidated 05-08 briefing subagent (created by commit `c40e431de`, 11-02, "run steps 05-08 as one briefing subagent") wrote only the completion edit. The per-step instructions drive this: `step-05` line 69 says "One Edit to this step file's frontmatter: `status: complete`, `completed-at` = the clock value", and `step-04` line 84 is the same shape. **No step file 04-08 instructs the executor to write `started-at` at step start.** `workflows/boot/workflow.md` line 120 has the global timestamp rule, but the per-step checklists the executor actually follows omit it.
- When the subagent's Edit fired, the inline path in `post-tool-use.py` sliced the main session transcript over `[2026-11-02T16:19, 2026-11-04T21:34]`: a two-day window. All four steps claimed start times within ~2.5 minutes of each other, so all four windows matched the same turn set, hence the identical 1,875,532 in / 5,827 out. `duration_seconds` is computed from the same stamps (post-tool-use.py line 1015-1021), hence ~191,500s against a 22-minute run.
- The stale-window guard in `partition_usage_by_steps` does not exist in the inline path. Worse, the partition backfill in `eval-agent-stop.py` (line 814) only fills steps whose tokens are still null, so once the inline path wrote its corrupted values, the correct per-step data from the 05-08 subagent's own record (eval-20261104T212943-QGM9VB, 4 real step entries) could not overwrite them.
- **This exact failure was predicted and documented.** `systems/error-tracking/entries/err-20261021T201533-209PMT.json` (the 10-21 root-cause, status resolved) lists as known residual risk #1: "post-tool-use.py inline extraction still reads the main transcript for subagent-written steps (hook payload carries no agent identity), so a concurrent main-session turn can be labeled 'windowed' on a subagent step; partition backfill only fills null tokens and will not overwrite such values." The fix was scoped but never built. The 11-04 record is that residual risk firing.

### 1b. step-04 unattributed in 4 of 6 recent runs

- Commit `386edc4eb` (2026-10-29, "cut boot token regressions") rewrote `step-04-gather-meeting-context.md` and **dropped the `started-at` line from its frontmatter entirely** (verified via `git show`: `b9a04ca34` version has `started-at: '2026-10-27T18:15:00Z'`; `386edc4eb` version does not). Since 10-29 the file has no `started-at` field at all.
- The inline extraction gate (post-tool-use.py line 1032) requires both timestamps; with `started-at` absent, tokens stay null and the review shows "?". The 10-22 occurrence (5C4OEY) predates this and belongs to the 10-22 record-routing bug day instead (see 1e).

### 1c. Zeros from windowed-partition (10-21, 10-26, 10-23)

`partition_usage_by_steps` trusts only the **order** of claimed `started-at` values. When executors write projected or copied windows (documented: boot steps 06-08 on 10-21 carried 15:47-15:50 windows for a subagent that ended 15:41:15), the real transcript turns all sort before those boundaries and land on earlier steps; later steps get honest zeros. These are the "honest zero, not estimated" outcomes the 10-21 root-cause deliberately chose. The mechanism is the same agent-authored-timestamp root as 1a; the zeros are the benign symptom, 1a is the malignant one.

### 1d. 10-19 flat lenient_fallback values (418,613 x 8; 5,249,805 x 2)

Historical, already root-caused and fixed. `token_usage.py` `usage_between` used to return the whole transcript when a strict window matched nothing; each stale step window therefore received the same whole-transcript sum. Retired in commit `278676cbd` (2026-10-21) per err-209PMT's resolution. No new occurrence after 10-21. No action needed beyond not regressing it.

### 1e. Runs with cost but no step records (IP36P9, P6CA3U, L9PFZ9, VXWWK6, BK458M)

Two mechanisms. (1) The 10-22 workflow-recovery bug: a dispatched executor's record carried `name: "general-purpose"`, `workflow: None`, so the step fan-out resolved workflow "general-purpose" and skipped per-step attribution entirely (documented in eval-agent-stop.py lines 641-651; fixed by stop-time spawn-prompt mining plus commit `a6ec2bf73` on 10-22). (2) The stale-open absorber records (see section 2): they close as aborted before any step write lands.

### 1f. 10-30 identical 83.1s durations

By design, not a bug in measurement: `systems/eval-harness/close-eval-record.py` `build_steps()` (line 221) distributes the run's elapsed time evenly across the `--steps` list when the workflow's final step closes the record (831.3s / 10 steps = 83.1s). On 10-30 the real per-step windows had been lost (the session-exit sweep orphaned six executors that day, documented in eval-agent-stop.py lines 704-715), so the skeleton survived and the executors' real token values were later adopted onto it (token_source windowed / subagent-transcript with `executed_by_agent_id` set). Durations are synthetic; tokens are real.

### 1g. Related defect found while tracing: windowed steps can over-sum the run

On the 11-04 plaud-ingest record (eval-20261104T211632-963724), per-step `windowed` values sum to 15.94M against a whole-run total of 14.84M. Step windows overlap (step-04-fetch-staging claims start 21:19:30, before step-02's claimed 21:20:30), so strict per-step slicing double-counts the overlapping turns. The sum-integrity invariant exists only in the partition path; the step-complete strict path has no check.

---

## 2. Retry stacking (27 records, 13 boot days, 5 multi-session days)

Reading `abort_reason`, `monitoring.close_reason`, guardrail entries, and step/subagent counts across all 27 records, the causes cluster into essentially **one operational root cause with two record flavors**, plus one historical bug day:

### Cluster A: boot outlives its session (the dominant cluster, ~16 of 27 records)

- **Flavor 1, `incomplete` / `abort_reason: session-exit-normal`** (7OUMW0, TPZO43, B7W765, NMXCZV, Q0REQ2, 49MKPI, 26QC3W, VG43U3, ZUIMG1): `close-open-evals.py` sweeps still-open records at SessionEnd. Boot runs 12-60 minutes and waits on subagents; when the session ends first (real exit, lid close, or the documented spurious SessionEnd events, three of them mid-boot on 10-30), the record is closed incomplete. B7W765 (10-26) had all 11 steps terminal and `completed: true` but still closed `incomplete` because state.yaml never got its final write.
- **Flavor 2, `aborted` / `abort_reason: unspecified` with close_reason "state.yaml's completion predates this record's open"** (J42OVZ 2.0h, 5C4OEY 3.6h, VXWWK6 2.5h, BK458M 2.1h, Y5F720 49.4h, DTTVF0 0.8h, L9PFZ9 2.1h): the same underlying event seen by `eval-turn-stop.py`'s stale-evidence guard (`try_finalize`, lines 821-861). The record's monitored state.yaml still shows the **previous** boot's completion because this run never reached the final state write, so the hook refuses to finalize it as success, waits out the stale window (10 minutes if zero steps, 2 hours otherwise), then force-aborts it. Y5F720 lingered 49.4h because the sweep only runs when some later Stop event fires.
- The two flavors are the same story (boot started, session ended before completion) depending on which sweep caught the record. Operationally: David re-opens a session, CLAUDE.md mandates boot, boot re-runs from the top, and each attempt mints a new record. Hence 2-4 records per real boot.

### Cluster B: harness bug days (historical, fixed)

- **10-15** (7 punch-outs): the "completed" vs "complete" status-spelling bug falsely escalated every plaud-ingest step; fixed in step-complete.py (lines 437-443).
- **10-22**: the workflow-recovery bug (1e) plus live harness surgery that day (commit `a6ec2bf73`); the retries were development iterations, not boot failures.
- **10-23 L9PFZ9** (226M tokens): a stale-open phantom that absorbed 37 unrelated subagents over 2.1 hours; the phantom-grace fix (STALE_PHANTOM_GRACE_MINUTES, eval-turn-stop.py line 726) was written because of it.

### Cluster C: tail-pass records counted as separate runs

10-27 YB6YAM is a 22-second "success" covering only steps 07-08: a second session re-entered boot, ran the remaining tail, and closed a fresh record as success. Not a retry, but it inflates both the record count and the success count.

### Guardrail signals

`punch_out_signal` fires only twice in the window (both 10-15, the spelling bug). `retry_signal` appears on 4 records, all `step-06-scan-workflows` (10-19, 10-23 x2, 10-26): one recurring step-level retry loop, cause not determinable from records alone (the retry reason text was not persisted on those records beyond the step name).

**Also confirmed: the Knox "no in-progress eval record" gap (4th consecutive run on 11-04).** `workflows/plaud-ingest/state.yaml` line 112 records guardrail-checkpoint.py failing to find an in-progress plaud-ingest record after 6 retries on pi-20261027, pi-20261028, pi-20261103, and 11-04. Root cause: `record-step.py:95` and `guardrail-checkpoint.py`'s copy of `find_most_recent_eval_record` match on `data.get("name") == workflow_name` only. A subagent-run workflow's record carries `name: "general-purpose"` with the real workflow in the `workflow` field (verified: eval-20261103T154553-L7OFL5 and eval-20261104T211632-963724 both have `name: general-purpose, workflow: plaud-ingest`). The finder never looks at `workflow`, so no subagent-run workflow can ever receive a checkpoint or record-step write. Same root cause produced the three 11-04 plaud-ingest phantoms in `runs/_phantoms/`: GUARD 2 in post-tool-use.py (`open_turn_level_record_exists`) checks turn-level records, not in-progress agent-type records, so each state.yaml `status: complete` write during the run spawned a phantom while the real subagent record was still open.

---

## 3. Status accuracy: why complete boots close as `partial` or `failure`

The status is derived at finalize time in `.claude/hooks/eval-turn-stop.py` `finalize()` (lines 677-690) and, for subagent records, `eval-agent-stop.py` (lines 1028-1037). The rules:

```
error_ids non-empty        -> failure
not completed              -> aborted
tool_failures > 0          -> partial
else                       -> success
```

Three mechanisms make this disagree with reality:

- **`tool_failures > 0 -> partial` counts benign probe failures.** `eval-tool-failure.py` increments the counter on any failed tool call in the session while the record is open. The 11-04 boot (019TAZ) has one failure: a `Read` on a not-yet-existing file 15 seconds into the run (the normal check-then-create pattern). The 11-03 boot (HYT8JX) has two identical Read misses 6 seconds in. The 10-30 and 11-02 records are the same shape (an Outlook NOT_FOUND probe against a deliberately fake folder name on 11-02). All four genuinely complete boots closed `partial` because of failures the workflow itself treated as routine.
- **`failure` is stamped by temporal correlation, not causation.** `post-tool-use.py` `check_error_tracking_write()` (line 1091) sets `status: failure` on whatever same-session record with activity is in-progress at the moment **any** error-tracking entry is written. On 11-03, Knox's plaud-ingest tooling error (err-20261103T161857-G1KXKK, a `context_tools.py` path mistake) was written while absorber record 863SNK was open, so 11-03 shows a boot "failure" that has nothing to do with boot. The error entries carry `agent` and `session` fields that would allow scoping; the hook ignores them.
- **Multiple records per real boot each get their own verdict.** 11-03 produced three boot records for one real boot: HYT8JX `partial` (the real run, benign Read misses), 863SNK `failure` (absorber stamped by cross-workflow error), DTTVF0 `aborted` (stale-open sweep). The review's outcome mix reads this as 1 partial + 1 failure + 1 aborted for a day whose boot actually completed.

---

## 4. Cost creep: 2.5M (10-21) to 29.6M (11-04)

Four additive causes, in order of contribution:

1. **Structural change: per-step subagent fan-out.** Commit `a6ec2bf73` (2026-10-22, "scope boot executors to single-purpose subagents") replaced the single-executor design with one subagent per step. The 10-21 record (QNQLC5) had 3 subagents totaling ~2.5M; runs from 10-29 onward carry 7-9 subagents and steady-state boot-proper totals of 8-12M (11.6M on 10-29, 8.2M on 10-30, 8.8M on 11-02, 7.8M on 11-03). Each spawned executor re-reads its step file, state.yaml, and identity slices, and every subagent transcript's full volume rolls into the boot record's total. Commit `c40e431de` (11-02) consolidated steps 05-08 into one subagent precisely to cut this.
2. **Accounting changes: cache-inclusive totals plus the parent window.** Since the 10-21 rework (`278676cbd`), `tokens_input` = input + cache_read + cache_creation (token_usage.py line 231), and each record additionally carries the `parent_window` component (the orchestrating session's own turns, 0.6-2.7M per run). These are newly **counted** tokens, not newly spent ones, and they make cross-window comparisons against pre-10-21 numbers invalid.
3. **Volatility from plaud-ingest inside the boot window.** When boot's Knox check triggers a real ingestion, that subagent is enormous: 23.6M measured tokens on 11-03 (L7OFL5; 7.3M on speaker-ID alone, deepseek-flash cache-read-heavy) and 14.8M on 11-04 (963724). On no-op days it costs ~36k. Whether it lands **in** the boot record's total is timing-dependent: on 11-03 the rollup arrived after the parent's aggregation ran, so HYT8JX's total excludes it (7.8M); on 11-04 it arrived in time, so 019TAZ includes it (14.8M of the 29.6M). Same work, opposite totals.
4. **11-04-specific corruption.** The four stale-window steps from section 1a contributed 4 x 1.87M = 7.5M of phantom tokens to the 29.6M total. Removing them: 29.6M - 7.5M = 22.1M, of which 14.8M is plaud-ingest and ~7.3M is boot proper, in line with the 8-12M trend.

Context growth is a minor contributor: the unified data files now read each boot (ynab-unified 172KB, calendar-unified 173KB) and every run loads SYSTEM.md (33KB) + agents/master.md (26KB) + identity files, re-sent per turn and per subagent.

---

## Error log cross-check (systems/error-tracking/entries, in-window)

51 entries in the window. Recurring categories at or over the 3-occurrence pattern threshold: **hallucination 7, tool-misuse 6, instruction-following 6, wrong-assumption 4, process-skip 3, data-accuracy 3**. Two entries bear directly on this analysis:

- **err-20261021T201533-209PMT** (severity major, category recurring-failure, "repeated-instrumentation-fixes-that-dont-hold"): six prior per-step attribution fixes each failed because they patched plumbing without fixing the two real roots (agent-authored timestamps, recency-based record routing). Its resolution built the 10-21 rework but explicitly left residual risk #1 (inline extraction on subagent-written steps) unimplemented. That residual is exactly what corrupted 11-04. The pattern David is asking about, "why do these keep occurring", has its meta-answer in this entry: fixes are landing one layer above the root.
- **err-20261104T212704-8DIR4P** (knox, stale-cache, fix_status proposed): `fetch_plaud.py` aborts the whole fetch when a stale pending-queue entry 404s. This is what made the 11-04 plaud-ingest run a failure inside boot's window. The proposed fix (drop confirmed-404 pending entries, process target date first) is written up and unimplemented.

---

## Ranked fix list

| # | Fix | What it fixes | Why it prevents recurrence | Effort | Proposal path |
|---|---|---|---|---|---|
| 1 | Add the stale-window guard to the inline path in `post-tool-use.py`: if `started-at` < the target record's `started`, write null tokens with `token_source: stale-window` (same contract as `partition_usage_by_steps` lines 305-330) | 11-04-style corruption (7.5M phantom tokens, 53h durations) | Removes the trust gap between the two remaining window paths; corrupted windows become visible audit labels instead of silent fabrication | Small (mirror existing guard, ~20 lines + test) | Clear-cut: auto-propose |
| 2 | Restore `started-at` to `step-04` frontmatter and add an explicit start-of-step stamp (`status: in-progress` + `started-at`) to the execution checklists of steps 04-08; consider a step-complete.py validation that flags `status: complete` with missing/stale `started-at` | step-04 "?" gap, the 05-08 stale stamps at the source | The instructions are what the executors actually follow; the global workflow.md rule is demonstrably insufficient | Small | Clear-cut mechanics; David confirms the stamp-on-start convention since it adds one Edit per step |
| 3 | Extend `find_most_recent_eval_record` (record-step.py:72, guardrail-checkpoint.py) and `open_turn_level_record_exists` to match `workflow` field as well as `name` | 4-in-a-row guardrail recording gap; 11-04 plaud-ingest phantom triplets; record-step writes for all subagent-run workflows | Subagent-run workflows are a permanent architectural feature; the finders predate the `workflow` field and were never updated for it | Small | Clear-cut: auto-propose |
| 4 | Scope `check_error_tracking_write` (post-tool-use.py:1091) by the error entry's `agent`/`session` fields: only stamp `failure` when the error's agent matches the record's owning workflow family | False `failure` on 11-03 (863SNK) and the class of cross-workflow failure stamps | The data to discriminate exists on every error entry; the hook just does not read it | Small | Auto-propose, but flag: it changes status semantics, David should see the rule |
| 5 | Discriminate benign tool failures in `eval-tool-failure.py` (Read file-not-found, existence-probe NOT_FOUNDs) or change the finalize rule so `partial` requires a failure correlated with an incomplete step | Complete boots closing `partial` (11-03, 11-04, 10-30, 11-02, and most partials in the window) | The current rule treats a routine probe identically to a real breakage, so `partial` carries no signal today | Medium (policy + implementation) | Needs David's call: what should downgrade a run |
| 6 | Re-run `aggregate_record_totals` after the orphan re-attach in eval-agent-stop.py (line 716-751) | 11-03's total excluding its 23.6M plaud-ingest subagent; totals that depend on rollup arrival order | Makes run totals order-independent; same tokens land in the total regardless of stop-hook timing | Trivial (~5 lines) | Clear-cut: auto-propose |
| 7 | Add a sum-integrity check (or window clamping) to the step-complete strict-window path, matching the partition path's invariant | Over-summed step slices (11-04 plaud: 15.9M of steps over a 14.8M run) | Overlapping agent-authored windows are a certainty; the check converts silent over-counting into a logged anomaly | Small | Clear-cut: auto-propose |
| 8 | Standardize `abort_reason` codes for the two session-lifecycle flavors (e.g. `session-end-mid-run`, `stale-state-open`) instead of `unspecified` + free-text close_reason | Retry-stack measurability | Today's clustering analysis required reading free text off 27 records; codes make the next review a query | Trivial | Clear-cut: auto-propose |
| 9 | Decide the cross-session boot policy: either one durable record per boot day that later sessions continue, or accept N records but teach the review tooling to group by day | The record-multiplication half of retry stacking | This is a design choice about what "a run" is, not a bug | Medium-large | Needs David's call |
| 10 | Implement the already-proposed `fetch_plaud.py` fix from err-8DIR4P (drop confirmed-404 pending entries; process the target date before pending re-checks) | The recurring plaud-ingest failures that keep landing inside boot windows | Proposed and approved-shaped already; every day unimplemented it can fail another ingest | Small | Auto-propose (already documented as proposed) |

Note on #1 priority: fixes 1, 3, 6, 7, 8 are all small, independent, and directly evidenced. Doing just those five would have made every anomaly in the 11-04 record either impossible or honestly labeled.

---

## What we can't explain without more instrumentation

- **Why the sessions actually ended mid-boot on the retry days.** The records show the sweeps that closed them, not the cause of the session ending. SessionEnd's reason (real exit vs spurious fire, documented as occurring 10-30) is not captured on any record. A SessionEnd reason field on closed records would answer the top remaining question in section 2.
- **Why the 05-08 briefing subagent stamped `started-at` on 11-02 but not on 11-04.** The step-file instructions do not ask for it either way, so both runs deviated from the global rule in opposite directions. Explaining the difference requires the subagent transcripts, which were out of scope for this analysis (no raw .jsonl reads).
- **Whether the step-06 retry loop (4 records) shares one cause.** The retry_signal on those records names the step but not the underlying validation failure in a durable field.
- **Whether L9PFZ9's 226M was real spend.** It is the sum of 37 absorbed subagents' measured transcripts, so the tokens were spent somewhere, but how much belonged to actual boot work versus unrelated concurrent sessions is not recoverable from the records.

---
name: boot
description: Session boot. Context load, data gather, verification, briefing, workflow scan.
agent: master
model: sonnet
fairness:
  applicable: false
  reason: Single-user personal assistant boot. Pulls one executive's calendar, email, and tasks; no differential treatment across any population.
---

<!-- system:start -->
# Boot Workflow

7 sequential steps with per-step token extraction and guardrail checkpoints.

## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `boot`; agent: `master`.

**Variant:** if `status: in-progress` but `session-started` is more than 4 hours old, treat the run as stale and start fresh.

**Fresh-run reset (mandatory):** when the state check takes the fresh-run branch, reset `accumulated-context` to a single `prior-run:` summary line before writing this run's keys (see `reference/workflow-conventions.md` → "Fresh-run reset"). Do not carry a prior run's phase blocks forward, and never rename one to `*-superseded` inside this file — boot's `state.yaml` is state, not history, and a `*-superseded` block is deleted, not parked. The 2026-10-26 run left a 7 KB `phase2-2026-10-23-superseded` block plus duplicate `prior-run`/`phase1` keys after claiming a fresh run.

**Delta mode:** if `status: complete` and `completed-at` is today, boot already ran. Run delta boot instead of a full boot:
1. Execute step-01 (identity load) normally; skip its Knox spawn entirely.
2. Execute step-01.5 (calendar pull, via the dedicated calendar subagent brief in the EXECUTION section below) and step-01.2 (unified data pull, via its dedicated data-pull subagent brief in the EXECUTION section below) to refresh `data/`.
3. Skip steps 02, 03, 04, 06, 08.
4. Produce a short delta briefing: what changed since this morning's boot (new flagged email, new inbox items, calendar changes, newly due/overdue tasks). No re-synthesis of unchanged sections.
5. Run step-07 to close. Delta boot target cost is under 20% of a full boot.

## DATA SOURCES

| Source | Method |
|--------|--------|
| SYSTEM.md, identity/* | Read files |
| M365 Calendar (3 days) | outlook_calendar_search |
| M365 Email (flagged) | outlook_email_search |
| OmniFocus inbox | `omnifocus-data` skill (step-01.2 Pull B; not the MCP) |
| Clay (7 days) | MCP |
| workflows/*/state.yaml | Read all |

## EXECUTION

**Dispatch model:** every workflow step below runs as a spawned sub-agent, never inline in Master's own session — the same rule that applies everywhere else in IES (e.g. Knox running `plaud-ingest`) applies here too, with exactly one deliberate exception (step-01, below) and a set of tightly-scoped single-purpose spawns covering every data/gather/verify step (01.5, 01.2, 02, 03, 04).

**Exception — step-01 only.** Step-01 loads `agents/master.md`, `SYSTEM.md`, the identity files, and `agents/routing.md` into Master's own live context; a subagent's context evaporates when it stops and cannot be deposited into Master's session.
So Master executes step-01 directly, in the main session, exactly as written in `steps/step-01-load-context.md`.
This is a permanent structural exception, not a shortcut.
The same exception applies to the equivalent first step of `shutdown-cleanup` and `weekly-review` (the only other `agent: master` workflows).

**Step 01.5 — dedicated calendar subagent, spawned first.** Immediately after step-01 completes, Master spawns a single-purpose subagent and blocks on it (it is one API call). Spawn prompt (substitute today's date and Day+3):

> Single-purpose calendar pull for step-01.5 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md` — your mandate is one calendar API call, one file write, then exit.
>
> Read `workflows/boot/steps/step-01.5-unified-calendar-pull.md` and execute exactly its YOUR TASK section: freshness-check `data/calendar-unified.json` (reuse if `pulled_at` is within 12 hours), otherwise a single `mcp__claude_ai_Microsoft_365__outlook_calendar_search` call for [TODAY] 00:00 through [TODAY+3] 23:59, write `data/calendar-unified.json`, then update the step frontmatter and `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with a one-line status: reused-or-pulled, event_count, date_range, failures.

Two reasons this spawn prompt is shaped exactly this way. First, the literal `workflows/boot/workflow.md` reference: the eval harness's subagent attribution (`eval-agent-start.py` / `eval-agent-stop.py`) resolves which workflow a spawn ran from that string in the spawn prompt — without it the record is tagged `general-purpose` and per-step token attribution is silently dropped (eval-20261022T114429-OCSJIC). Second, the "do not read any other step file" line: step files used to chain into each other ("read fully and follow next step"), which is how a one-call calendar pull became a 57-turn walk of the whole boot workflow at 6.27M tokens.

**Steps 01.2, 02, 03, and 04 — dedicated single-purpose subagents, spawned in sequence.** Each runs as its own fresh, bounded subagent: no persona load, no step walking, compact results into `state.yaml`, then return. This extends the step-01.5 fix (work-20261022-143802) to the rest of the gather chain: one long-lived boot subagent walking steps 02-04 carried 500-720k input tokens per step for outputs of a few hundred tokens (eval-20261021T151330-QNQLC5: steps 02/03/04 at 545k/495k/531k in for 628/1,014/1,354 out; eval-20261013T114019-Q5UJLE: 719k in / 4,291 out attributed across the same steps). Every brief below must keep its literal `workflows/boot/workflow.md` reference (eval subagent attribution) and its "do not read any other step file" line. Spawn them one at a time, blocking on each, in this order:

**Step 01.2 — unified data pull** (spawn after the calendar subagent returns):

> Single-purpose unified data pull for step-01.2 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md` — your mandate is the five data pulls (A-E), then exit.
>
> Read `workflows/boot/steps/step-01.2-unified-data-pull.md` and execute exactly its YOUR TASK section. Read `workflows/boot/references/pull-file-formats.md` and `workflows/boot/references/execution-guidelines.md` first. Fire pulls A-E per the step file (the calendar already ran as step-01.5 — never re-pull it), write the `data/*-unified.json` files, then update the step frontmatter and `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with a one-line status per pull (A-E), the files written, and any failure.

**Step 02 — gather data** (spawn after step-01.2 returns):

> Single-purpose data-gather pass for step-02 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md` — your mandate is six bounded tasks over the unified data files already on disk, then exit.
>
> Read `workflows/boot/steps/step-02-gather-data.md` and execute exactly its YOUR TASK section: task A (morning-briefing steps 01-02 applied directly to `data/calendar-unified.json` and `data/omnifocus-unified.json` — the two gather step files under `workflows/morning-briefing/steps/` are borrowed as mechanical file reads, not a morning-briefing workflow run), task G (72-hour look-ahead filter), task H (email triage filter), task I (Jarvis inbox from `data/jarvis-inbox-unified.json` — spawn the jarvis-inbox processing subagent only if it shows unread items), task J (boot reminders from `data/reminders.json`). Zero M365/OmniFocus/Clay API calls. Record compact results in `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file (including anything in `workflows/morning-briefing/` beyond its step-01 and step-02 gather files). Return to the coordinator with a one-line status per task (A, G, H, I, J) and any failure.

**Step 03 — verify phase 2** (spawn after step-02 returns):

> Single-purpose verification pass for step-03 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md` — your mandate is one verifier script run, then exit.
>
> Read `workflows/boot/steps/step-03-verify-phase2.md` and execute exactly its YOUR TASK section: run `python3 workflows/boot/verify/boot-verify.py phase2` from the IES root; on exit 0 record the pass in `state.yaml` `accumulated-context` via Edit; on exit 1 spawn Ralph with the tight flagged-items-only brief the step file specifies. Update the step frontmatter and `current-step` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with the verification verdict and the one-line instrumentation measurement.

**Step 04 — gather meeting context** (spawn after step-03 returns):

> Single-purpose meeting-context pass for step-04 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md` — your mandate is bounded context gathering, then exit.
>
> Read `workflows/boot/steps/step-04-gather-meeting-context.md` and execute exactly its YOUR TASK section: read step-02's `calendar_data` from `state.yaml`, apply morning-briefing step-03's gather rules to the `needs_prep` meetings (identity files, knowledge-base searches, delegation tracker, yesterday's review), read Clay data from `data/clay-reminders-unified.json` (no Clay MCP call), record compact results in `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> **Obey the step file's CONTEXT BUDGET section as a hard rule.** `vault_read` only with `target`/`targetType: heading` or `limit` ≤ 60 — never a full note body; `search_simple` `contextLength` ≤ 40; at most 2 notes per meeting; no duplicate reads of the same path; never read `systems/eval-harness/**`, `~/.claude/projects/**`, or any `.jsonl`. A 4x token spike in this step on 2026-10-29 traced entirely to full-body vault reads.
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with meetings-with-context, the Clay outcome, yesterday's review status, and any failure.

**Steps 05 through 08 — exactly one briefing subagent.** Spawn it only after the step-04 subagent has returned and completed, not fire-and-forget. Its mandate is steps 05, 06, 07, and 08 and nothing else.

> Single-purpose briefing pass for steps 05 through 08 of `workflows/boot/workflow.md`. You are Master, running mid-boot: `state.yaml` is `in-progress`.
>
> Your mandate is exactly four steps, in order: `step-05-synthesize-briefing.md`, `step-06-scan-workflows.md`, `step-07-verify-completion.md`, `step-08-knox-completion-check.md`. Execute each per its own YOUR TASK section, including the guardrail-checkpoint/retry/punch-out behavior described in the workflow file.
>
> **Do NOT re-run or re-pull steps 01.5, 01.2, 02, 03, or 04.** They already ran as dedicated single-purpose subagents before you were spawned. Watchtower no longer runs as part of boot (removed 2026-10-27, err-20261027T184315-93PIYQ) — do not run the Watchtower daily pipeline. If `current-step` in `state.yaml` still points at step-04 or earlier, do not execute that step: return to the coordinator with a one-line mismatch report instead.
>
> Timestamps: read the real clock with `date -u +%Y-%m-%dT%H:%M:%SZ` at each write. Never estimate, round, or backfill.
>
> Your final message must contain the complete morning briefing produced in step-05, verbatim and unabridged, plus the workflow-scan summary and the final verification result.

Additional rules:

1. Wait for the subagent (block on the result) — Master needs the synthesized briefing this turn, so this is not a background spawn.
2. Its final message must contain the complete morning briefing, verbatim and unabridged, plus the workflow-scan summary from step-06 and the verification result from step-07/08. Master relays that content to the controller as its own next message — do not summarize, truncate, or re-synthesize it.
3. If the subagent's run hits a guardrail `escalate` it cannot resolve on its own (see step-complete.py's punch-out signal), it should pause and report the blocker in its response rather than guessing; Master surfaces that to the controller and, once a decision is given, resumes the same subagent via SendMessage rather than starting a fresh one — this preserves `state.yaml`'s `current-step` and `accumulated-context`.

**File-tool rule for every spawned executor:** state.yaml and step-frontmatter updates go through the Edit/Write tools, never Bash redirection or heredocs. The eval harness's per-step attribution keys on Edit/Write tool calls; the 2026-10-22 boot executor did everything through 42 Bash calls and left zero per-step records.

**Timestamp rule for every spawned executor:** `started-at` and `completed-at` are the real clock reading from `date -u +%Y-%m-%dT%H:%M:%SZ`, pasted exactly. Never estimate, round to a convenient minute, backfill after the fact, or use a midnight placeholder. Attribution windows are derived from these stamps: the 2026-10-26 run stamped its later steps 23-27 minutes after the files were actually written, which collapsed per-step attribution and nulled steps 05-08. `boot-verify.py completion` now treats a stamp ahead of the file's write time as a hard error.

### Steps

| # | File | Guardrail | Executed by |
|---|------|-----------|-------------|
| 1 | `step-01-load-context.md` | step-01-checkpoint | Master, inline (see exception above) |
| 2 | `step-01.5-unified-calendar-pull.md` | step-01.5-checkpoint | dedicated calendar subagent (tight brief above) |
| 3 | `step-01.2-unified-data-pull.md` | — | dedicated data-pull subagent (tight brief above) |
| 4 | `step-02-gather-data.md` | step-02-checkpoint | dedicated gather subagent (tight brief above) |
| 5 | `step-03-verify-phase2.md` (measure + verify, script-first via `verify/boot-verify.py phase2`; Ralph only on anomaly) | step-03-checkpoint | dedicated verify subagent (tight brief above) |
| 6 | `step-04-gather-meeting-context.md` | step-04-checkpoint | dedicated meeting-context subagent (tight brief above) |
| 7 | `step-05-synthesize-briefing.md` | step-05-checkpoint | briefing subagent (steps 05-08) |
| 8 | `step-06-scan-workflows.md` | step-06-checkpoint | briefing subagent (steps 05-08) |
| 9 | `step-07-verify-completion.md` (guardrail review + completion gate, script-first via `verify/boot-verify.py completion`) | step-07-checkpoint | briefing subagent (steps 05-08) |
| 10 | `step-08-knox-completion-check.md` | — | briefing subagent (steps 05-08) |

Former step-02.5 (measure) and step-06.5 (guardrail checkpoint) were merged into step-03 and step-07 on 2026-10-20; their mechanics now run as `verify/boot-verify.py` subprocesses instead of LLM subagent work.

After each step: (1) step-complete.py hook extracts per-step tokens, (2) guardrail checkpoint validates output, (3) if escalate: punch out to controller per the resume protocol above, (4) if retry: re-execute step (max 2 attempts per step-complete.py's retry_signal), (5) else: continue to next step.

Begin: `steps/step-01-load-context.md`

<!-- system:end -->

<!-- personal:start -->
## Session Index

After step-01 reads identity files:
- Create `memory/sessions/index.json` if missing: `[]`
- Append session record: `{started, closed: null, current_topic: null, topics: []}`

<!-- personal:end -->

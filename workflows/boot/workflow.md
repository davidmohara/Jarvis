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
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with meetings-with-context, the Clay outcome, yesterday's review status, and any failure.

**Steps 05 through 08 — one briefing subagent.** Spawn it after the step-04 subagent returns, not fire-and-forget:

1. Spawn a subagent (general-purpose, persona `agents/master.md`) with instructions to: run STATE CHECK (the workflow is mid-run — `state.yaml` status is `in-progress` and resumes from `current-step`), then execute steps 05 through 08 of `workflows/boot/workflow.md` in order (every gather/pull/verify step before them — 01.5, 01.2, 02, 03, 04 — already ran as dedicated single-purpose subagents; never re-run or re-pull any of them), following each step's own frontmatter/state.yaml update protocol exactly as written, including the guardrail-checkpoint/retry/punch-out behavior described below.
2. Wait for it (block on the result) — Master needs the synthesized briefing this turn, so this is not a background spawn.
3. The subagent's final message must contain the complete morning briefing produced in step-05, verbatim and unabridged, plus the workflow-scan summary from step-06/06.5/08. Master relays that content to the controller as its own next message — do not summarize, truncate, or re-synthesize it.
4. If the subagent's run hits a guardrail `escalate` it cannot resolve on its own (see step-complete.py's punch-out signal), it should pause and report the blocker in its response rather than guessing; Master surfaces that to the controller and, once a decision is given, resumes the same subagent via SendMessage rather than starting a fresh one — this preserves `state.yaml`'s `current-step` and `accumulated-context`.

**File-tool rule for every spawned executor:** state.yaml and step-frontmatter updates go through the Edit/Write tools, never Bash redirection or heredocs. The eval harness's per-step attribution keys on Edit/Write tool calls; the 2026-10-22 boot executor did everything through 42 Bash calls and left zero per-step records.

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

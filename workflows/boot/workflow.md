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

10 sequential steps with per-step token extraction and guardrail checkpoints.

## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `boot`; agent: `master`.

**Variant:** if `status: in-progress` but `session-started` is more than 4 hours old, treat the run as stale and start fresh. **Fresh-run reset (mandatory):** when the state check takes the fresh-run branch, reset `accumulated-context` to a single `prior-run:` summary line before writing this run's keys (see `reference/workflow-conventions.md` → "Fresh-run reset"). Do not carry a prior run's phase blocks forward, and never rename one to `*-superseded` inside this file. Boot's `state.yaml` is state, not history, and a `*-superseded` block is deleted, not parked.

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

**Dispatch model:** every workflow step below runs as a spawned sub-agent, never inline in Master's own session. The same rule applies everywhere else in IES (e.g. Knox running `plaud-ingest`), with exactly one deliberate exception (step-01, below) and a set of tightly-scoped single-purpose spawns covering every data/gather/verify step (01.5, 01.2, 02, 03, 04).

**Exception, step-01 only.** Step-01 loads `agents/master.md`, `SYSTEM.md`, the identity files, and `agents/routing.md` into Master's own live context; a subagent's context evaporates when it stops and cannot be deposited into Master's session. So Master executes step-01 directly, in the main session, exactly as written in `steps/step-01-load-context.md`. This is a permanent structural exception, not a shortcut. The same exception applies to the equivalent first step of `shutdown-cleanup` and `weekly-review` (the only other `agent: master` workflows).

**Step 01.5, dedicated calendar subagent, spawned first.** Immediately after step-01 completes, Master spawns a single-purpose subagent and blocks on it (it is one API call). Spawn prompt (substitute today's date and Day+3):

> Single-purpose calendar pull for step-01.5 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md`; your mandate is one calendar API call, one file write, then exit.
>
> Read `workflows/boot/steps/step-01.5-unified-calendar-pull.md` and execute exactly its YOUR TASK section: freshness-check `data/calendar-unified.json` (reuse if `pulled_at` is within 12 hours), otherwise a single `mcp__claude_ai_Microsoft_365__outlook_calendar_search` call for [TODAY] 00:00 through [TODAY+3] 23:59, write `data/calendar-unified.json`, then update the step frontmatter and `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with a one-line status: reused-or-pulled, event_count, date_range, failures.

**Steps 01.2, 02, 03, and 04, dedicated single-purpose subagents, spawned in sequence.** Each runs as its own fresh, bounded subagent: no persona load, no step walking, compact results into `state.yaml`, then return. Every brief below must keep its literal `workflows/boot/workflow.md` reference (eval subagent attribution) and its "do not read any other step file" line. Spawn them one at a time, blocking on each, in this order:

**Step 01.2, unified data pull** (spawn after the calendar subagent returns):

> Single-purpose unified data pull for step-01.2 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md`; your mandate is the five data pulls (A-E), then exit.
>
> Read `workflows/boot/steps/step-01.2-unified-data-pull.md` and execute exactly its YOUR TASK section. Read `workflows/boot/references/pull-file-formats.md` and `workflows/boot/references/execution-guidelines.md` first. Fire pulls A-E per the step file (the calendar already ran as step-01.5, never re-pull it), write the `data/*-unified.json` files, then update the step frontmatter and `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with a one-line status per pull (A-E), the files written, and any failure.

**Step 02, gather data** (spawn after step-01.2 returns):

> Single-purpose data-gather pass for step-02 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md`; your mandate is six bounded tasks over the unified data files already on disk, then exit.
>
> Read `workflows/boot/steps/step-02-gather-data.md` and execute exactly its YOUR TASK section: task A (morning-briefing steps 01-02 applied directly to `data/calendar-unified.json` and `data/omnifocus-unified.json`, with the two gather step files under `workflows/morning-briefing/steps/` borrowed as mechanical file reads, not a morning-briefing workflow run), task G (72-hour look-ahead filter), task H (email triage filter), task I (Jarvis inbox from `data/jarvis-inbox-unified.json`, spawning the jarvis-inbox processing subagent only if it shows unread items), task J (boot reminders from `data/reminders.json`). Zero M365/OmniFocus/Clay API calls. Record compact results in `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file (including anything in `workflows/morning-briefing/` beyond its step-01 and step-02 gather files). Return to the coordinator with a one-line status per task (A, G, H, I, J) and any failure.

**Step 03, verify phase 2** (spawn after step-02 returns):

> Single-purpose verification pass for step-03 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md`; your mandate is one verifier script run, then exit.
>
> Read `workflows/boot/steps/step-03-verify-phase2.md` and execute exactly its YOUR TASK section: run `python3 workflows/boot/verify/boot-verify.py phase2` from the IES root; on exit 0 record the pass in `state.yaml` `accumulated-context` via Edit; on exit 1 spawn Ralph with the tight flagged-items-only brief the step file specifies. Update the step frontmatter and `current-step` with the Edit tool (never Bash).
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with the verification verdict and the one-line instrumentation measurement.

**Step 04, gather meeting context** (spawn after step-03 returns):

> Single-purpose meeting-context pass for step-04 of `workflows/boot/workflow.md`. You are NOT loading any persona file or `SYSTEM.md`; your mandate is bounded context gathering, then exit.
>
> Read `workflows/boot/steps/step-04-gather-meeting-context.md` and execute exactly its YOUR TASK section: read step-02's `calendar_data` from `state.yaml`, apply morning-briefing step-03's gather rules to the `needs_prep` meetings (identity files, knowledge-base searches, delegation tracker, yesterday's review), read Clay data from `data/clay-reminders-unified.json` (no Clay MCP call), record compact results in `state.yaml` `accumulated-context` with the Edit tool (never Bash).
>
> **Obey the step file's CONTEXT BUDGET section as a hard rule.** `vault_read` only with `target`/`targetType: heading` or `limit` ≤ 60, never a full note body; `search_simple` `contextLength` ≤ 40; at most 2 notes per meeting; no duplicate reads of the same path; never read `systems/eval-harness/**`, `~/.claude/projects/**`, or any `.jsonl`.
>
> That step file is your entire mandate. Do not read or execute any other step file. Return to the coordinator with meetings-with-context, the Clay outcome, yesterday's review status, and any failure.

**Steps 05 through 08, exactly one briefing subagent.** Spawn it only after the step-04 subagent has returned and completed, not fire-and-forget. Its mandate is steps 05, 06, 07, and 08 and nothing else.

> Single-purpose briefing pass for steps 05 through 08 of `workflows/boot/workflow.md`. You are Master, running mid-boot: `state.yaml` is `in-progress`.
>
> Your mandate is exactly four steps, in order: `step-05-synthesize-briefing.md`, `step-06-scan-workflows.md`, `step-07-verify-completion.md`, `step-08-knox-completion-check.md`. Execute each per its own YOUR TASK section, including the guardrail-checkpoint/retry/punch-out behavior described in the workflow file.
>
> **Do NOT re-run or re-pull steps 01.5, 01.2, 02, 03, or 04.** They already ran as dedicated single-purpose subagents before you were spawned. Do not run the Watchtower daily pipeline; Watchtower is not part of boot. If `current-step` in `state.yaml` still points at step-04 or earlier, do not execute that step: return to the coordinator with a one-line mismatch report instead.
>
> Timestamps: read the real clock with `date -u +%Y-%m-%dT%H:%M:%SZ` once per step, in that step's write turn, and reuse that one reading for the step's `state.yaml` write and its frontmatter stamp. Never estimate, round, or backfill.
>
> TURN BUDGET: target 22 assistant turns or fewer for all four steps. Turns are the cost: every turn re-sends the whole conversation, so one extra turn at this point in boot costs about 80,000 tokens. Batch independent tool calls into one turn. Do not spend a turn on anything you can fold into another turn. The budget governs reads and bookkeeping only: it never licenses skipping a gate, the guardrail punch-out, the step-07 content judgment, or shortening the briefing.
>
> READ RESTRICTIONS:
> - Read the four step files in ONE turn, not four.
> - Read `workflows/boot/state.yaml` ONCE, targeted at the `accumulated-context:` block. Never `cat` the whole file. Do not grep before an edit; the step file names the anchor.
> - Do NOT read `workflows/boot/verify/boot-verify.py` source. Invoke it. It is the authority.
> - Do NOT read `systems/eval-harness/**` or any `.jsonl`.
> - Do NOT re-run a gate that already exited 0.
>
> WRITE ORDER: do the step's work, write the state key, then stamp the step frontmatter LAST as the final action of the step. `completed-at` is the clock reading taken immediately before the writes.
>
> Your final message must contain the complete morning briefing produced in step-05, verbatim and unabridged, plus the workflow-scan summary and the final verification result.

Additional rules:

1. Wait for the subagent (block on the result); Master needs the synthesized briefing this turn, so this is not a background spawn. Its final message must contain the complete morning briefing, verbatim and unabridged, plus the workflow-scan summary from step-06 and the verification result from step-07/08. Master relays that content to the controller as its own next message: do not summarize, truncate, or re-synthesize it.
2. If the subagent's run hits a guardrail `escalate` it cannot resolve on its own (see step-complete.py's punch-out signal), it should pause and report the blocker in its response rather than guessing; Master surfaces that to the controller and, once a decision is given, resumes the same subagent via SendMessage rather than starting a fresh one, which preserves `state.yaml`'s `current-step` and `accumulated-context`.

**File-tool rule for every spawned executor:** state.yaml and step-frontmatter updates go through the Edit/Write tools, never Bash redirection or heredocs. The eval harness's per-step attribution keys on Edit/Write tool calls.

**Timestamp rule for every spawned executor:** `started-at` and `completed-at` are the real clock reading from `date -u +%Y-%m-%dT%H:%M:%SZ`, pasted exactly. Never estimate, round to a convenient minute, backfill after the fact, or use a midnight placeholder. Attribution windows are derived from these stamps.

### Steps

| # | File | Guardrail | Executed by |
|---|------|-----------|-------------|
| 1 | `step-01-load-context.md` | step-01-checkpoint | Master, inline (see exception above) |
| 2 | `step-01.5-unified-calendar-pull.md` | step-01.5-checkpoint | dedicated calendar subagent (tight brief above) |
| 3 | `step-01.2-unified-data-pull.md` | none | dedicated data-pull subagent (tight brief above) |
| 4 | `step-02-gather-data.md` | step-02-checkpoint | dedicated gather subagent (tight brief above) |
| 5 | `step-03-verify-phase2.md` (measure + verify, script-first via `verify/boot-verify.py phase2`; Ralph only on anomaly) | step-03-checkpoint | dedicated verify subagent (tight brief above) |
| 6 | `step-04-gather-meeting-context.md` | step-04-checkpoint | dedicated meeting-context subagent (tight brief above) |
| 7 | `step-05-synthesize-briefing.md` | step-05-checkpoint | briefing subagent (steps 05-08) |
| 8 | `step-06-scan-workflows.md` | step-06-checkpoint | briefing subagent (steps 05-08) |
| 9 | `step-07-verify-completion.md` (guardrail review + completion gate, script-first via `verify/boot-verify.py completion`) | step-07-checkpoint | briefing subagent (steps 05-08) |
| 10 | `step-08-knox-completion-check.md` | none | briefing subagent (steps 05-08) |

After each step: (1) step-complete.py hook extracts per-step tokens, (2) guardrail checkpoint validates output, (3) if escalate: punch out to controller per the resume protocol above, (4) if retry: re-execute step (max 2 attempts per step-complete.py's retry_signal), (5) else: continue to next step. Begin: `steps/step-01-load-context.md`

<!-- system:end -->

<!-- personal:start -->
## Session Index

After step-01 reads identity files:
- Create `memory/sessions/index.json` if missing: `[]`
- Append session record: `{started, closed: null, current_topic: null, topics: []}`

<!-- personal:end -->

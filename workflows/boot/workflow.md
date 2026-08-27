---
name: boot
description: Session boot. Context load, data gather, verification, briefing, workflow scan.
agent: master
model: sonnet
---

<!-- system:start -->
# Boot Workflow

9 sequential steps with per-step token extraction and guardrail checkpoints.

## STATE CHECK

1. Read `state.yaml`
2. If `status: in-progress`:
   - If `session-started` > 4 hours old: treat as stale, fresh run
   - Else: resume from `current-step`
3. If `status: complete` or `not-started`: fresh run
4. If `status: aborted`: ask controller

## DATA SOURCES

| Source | Method |
|--------|--------|
| SYSTEM.md, identity/* | Read files |
| M365 Calendar (3 days) | outlook_calendar_search |
| M365 Email (flagged) | outlook_email_search |
| OmniFocus inbox | MCP |
| Clay (7 days) | MCP |
| workflows/*/state.yaml | Read all |

## EXECUTION

**Dispatch model:** every workflow step below runs as a spawned sub-agent, never inline in Master's own session — the same rule that applies everywhere else in IES (e.g. Knox running `plaud-ingest`) applies here too, with exactly one deliberate exception.

**Exception — step-01 only.** Step-01's entire job is loading `agents/master.md`, `SYSTEM.md`, the identity files, and `agents/routing.md` *into Master's own live context* so Master can operate as itself for the rest of the session. A subagent reading those files reads them into its own context, which evaporates the moment it stops — it cannot deposit that context into Master's session. There is no way to delegate this step without defeating its purpose, so Master executes step-01 directly, in the main session, exactly as written in `steps/step-01-load-context.md`. This is a permanent, structural exception, not a shortcut — the same exception applies to the equivalent first step of `shutdown-cleanup` and `weekly-review` (the only other `agent: master` workflows), which have the identical constraint and need the same treatment.

**Everything else — steps 2 through 12 — runs as one spawned sub-agent**, not fire-and-forget. Immediately after step-01 completes:

1. Spawn a subagent (general-purpose, persona `agents/master.md`) with instructions to: run STATE CHECK, then execute steps 01.2 through 08 below in order, following each step's own frontmatter/state.yaml update protocol exactly as written, including the guardrail-checkpoint/retry/punch-out behavior described below.
2. Wait for it (block on the result) — Master needs the synthesized briefing this turn, so this is not a background spawn.
3. The subagent's final message must contain the complete morning briefing produced in step-05, verbatim and unabridged, plus the workflow-scan summary from step-06/06.5/08. Master relays that content to the controller as its own next message — do not summarize, truncate, or re-synthesize it.
4. If the subagent's run hits a guardrail `escalate` it cannot resolve on its own (see step-complete.py's punch-out signal), it should pause and report the blocker in its response rather than guessing; Master surfaces that to the controller and, once a decision is given, resumes the same subagent via SendMessage rather than starting a fresh one — this preserves `state.yaml`'s `current-step` and `accumulated-context`.

This dispatch pattern is what gives boot a real `SubagentStart`/`SubagentStop` pair to hang an eval record on. It is not, on its own, what makes the eval record exist — that is `.claude/hooks/eval-turn-start.py` (opens the record on `UserPromptSubmit`, independent of whether steps run inline or spawned) and `.claude/hooks/eval-turn-stop.py` (closes it out on `Stop` once `state.yaml` reaches `status: complete`). Both mechanisms are complementary: the turn-level hooks guarantee an eval record exists at all; running steps 2-12 as a real subagent additionally gives per-subagent model/token/cost data in the record's `subagents[]` array. See `systems/eval-harness/schema.md` for the full field reference.

### Steps

| # | File | Guardrail | Executed by |
|---|------|-----------|-------------|
| 1 | `step-01-load-context.md` | step-01-checkpoint | Master, inline (see exception above) |
| 2 | `step-01.2-unified-data-pull.md` | — | spawned subagent |
| 3 | `step-01.5-unified-calendar-pull.md` | step-01.5-checkpoint | spawned subagent |
| 4 | `step-02-gather-data.md` | step-02-checkpoint | spawned subagent |
| 5 | `step-02.5-measure-phase2.md` | — | spawned subagent |
| 6 | `step-03-verify-phase2.md` | step-03-checkpoint | spawned subagent |
| 7 | `step-04-gather-meeting-context.md` | step-04-checkpoint | spawned subagent |
| 8 | `step-05-synthesize-briefing.md` | step-05-checkpoint | spawned subagent |
| 9 | `step-06-scan-workflows.md` | step-06-checkpoint | spawned subagent |
| 10 | `step-06.5-guardrail-checkpoint.md` | step-06.5-checkpoint | spawned subagent |
| 11 | `step-07-verify-completion.md` | step-07-checkpoint | spawned subagent |
| 12 | `step-08-knox-completion-check.md` | — | spawned subagent |

After each step: (1) step-complete.py hook extracts per-step tokens, (2) guardrail checkpoint validates output, (3) if escalate: punch out to controller per the resume protocol above, (4) if retry: re-execute step (max 2 attempts per step-complete.py's retry_signal), (5) else: continue to next step.

Begin: `steps/step-01-load-context.md`

<!-- system:end -->

<!-- personal:start -->
## Session Index

After step-01 reads identity files:
- Create `memory/sessions/index.json` if missing: `[]`
- Append session record: `{started, closed: null, current_topic: null, topics: []}`

<!-- personal:end -->

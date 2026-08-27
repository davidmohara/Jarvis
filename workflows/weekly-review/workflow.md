---
name: weekly-review
description: Weekly review - rocks, delegations, inbox health, calendar audit, people check, next week priorities
agent: master
orchestrates: [chief, chase, quinn, shep]
model: sonnet
---

<!-- system:start -->
# Weekly Review Workflow

**Goal:** The most important cadence. Review everything that matters, surface what's drifting, and set next week up for execution. This is where the execution gap gets closed.

**Agent:** Master agent (orchestrates sub-agents as needed)

**Architecture:** Sequential 8-step workflow. Each step reviews a different domain. The master agent drives, pulling in sub-agents when their domain expertise is needed. Interactive throughout - the controller walks through each section.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Quarterly objectives | Rock status and progress | Read memory/personal/quarterly-objectives.md |
| Delegation tracker | All active delegations, overdue items | Read delegations/tracker.md |
| Task management | Inbox count, flagged items, items > 7 days old | Task management API |
| Calendar | This week's meetings (what happened), next week's meetings (what's coming) | M365 MCP |
| Daily reviews | This week's daily review files | Read reviews/daily/ |
| Knowledge layer | Recent meeting notes, decisions made this week | Knowledge base API |

### Output

- Weekly review file: `reviews/weekly/YYYY-Wxx.md`

### Agent Routing

| Step | Domain | Sub-Agent |
|------|--------|-----------|
| Wins and misses | Operations | Master (interactive) |
| Rocks review | Strategy | Quinn |
| Delegation review | People | Shep |
| Inbox and calendar | Operations | Chief |
| People check | People | Shep |
| Set priorities | Strategy | Quinn |
| Social calendar lookahead | Personal | Sterling |
| Eval summary + close | System Health | Master (invokes rigby-eval-analyze skill, then closes workflow) |
| Error improvement | System Health | Rigby — runs `workflows/error-improvement/` Phase A only (Steps 1-3: intake, analyze, triage). Surfaces Apply Now list and Needs Your Call items to controller. Controller approves or defers. Weekly review then closes. Rigby runs Phase B (Steps 4-7: apply, verify, compact, summary) as a follow-on task after the review session ends — the summary report is delivered separately. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

**Dispatch model — differs from boot's, and deliberately so.** Checked step-01 (`step-01-wins-and-misses.md`) and step-08 (`step-08-eval-summary.md`), the two steps labeled `**Agent:** Master`, against boot's constraint (does either load `agents/master.md`/`SYSTEM.md`/identity files into Master's own live session?): no — step-01 is a reflective wins/misses conversation with the controller, step-08 invokes the `rigby-eval-analyze` skill. Neither has boot's structural requirement, and Master's own identity was already loaded once this session, at boot. So there is no inline-execution exception anywhere in this workflow either.

But unlike boot and shutdown-cleanup, weekly-review is **not** a single-persona workflow that happens to run inline — its own frontmatter (`orchestrates: [chief, chase, quinn, shep]`) and its Agent Routing table already name a *different* owning agent per step: Quinn (rocks, priorities), Shep (delegations, people), Chief (inbox/calendar), Sterling (social calendar), Master (wins/misses, eval summary). Collapsing all 8 steps into one generic `agents/master.md` subagent — the pattern used for boot and shutdown-cleanup — would mean that subagent narrating Quinn's/Shep's/Chief's/Sterling's personas from inside a Master-flavored context instead of actually being them, which is worse than what boot had, not equivalent to it. The correct fix here is the same one already used everywhere else in IES for a workflow with a named owning persona (e.g. Knox for `plaud-ingest`): each step gets spawned as its own designated agent.

Every step is also interactive — each one asks the controller questions and waits for real answers, not just at an escalation point the way boot's guardrail-punch-out is. So the resume mechanism boot uses for its one guardrail case is used *continuously* here, once per step:

1. For each step in order, spawn that step's designated agent as a subagent (Quinn for steps 02/06, Shep for steps 03/05, Chief for step 04, Sterling for step 07, a general-purpose subagent with persona `agents/master.md` for steps 01/08), with instructions to run that one step per its own frontmatter/state.yaml update protocol.
2. Wait for it. Its final message will typically be a question or a finding awaiting controller validation (per each step's `MANDATORY EXECUTION RULES` — e.g. step-01 must not proceed until wins/misses are captured, step-02 must not proceed until the controller confirms each rock's status).
3. Master relays that message to the controller verbatim, gets the controller's answer, and resumes the *same* subagent via SendMessage with that answer — repeating until the step's own completion criteria are met and it writes `status: complete` to its step frontmatter.
4. Move to the next step's designated agent. State (`current-step`, `accumulated-context`) carries forward in `state.yaml` exactly as before; each step's spawn is a fresh subagent even when consecutive steps share the same owning agent (e.g. Quinn's step-02 and step-06 are separate spawns, not one long-lived session), since state.yaml is the source of truth carried between them, not subagent memory.

Net effect: this workflow now produces up to 6 distinct `SubagentStart`/`SubagentStop` pairs (one per step-agent spawn) instead of boot's one, all linked into the same turn-level eval record by session_id — `.claude/hooks/eval-agent-start.py`/`eval-agent-stop.py`'s existing "link into open turn record" logic handles this automatically regardless of how many distinct agent_types get spawned. `.claude/hooks/eval-turn-start.py` opens that record on `UserPromptSubmit` (matched by name/slug + run-verb, e.g. "run weekly review" — no natural-language alias needed here, unlike shutdown-cleanup); `.claude/hooks/eval-turn-stop.py` closes it once `state.yaml` reaches `status: complete`.

### Steps

| # | File | Dispatched to |
|---|------|----------------|
| 1 | `step-01-wins-and-misses.md` | spawned subagent, persona `agents/master.md` |
| 2 | `step-02-rocks-review.md` | spawned subagent, persona Quinn |
| 3 | `step-03-delegation-review.md` | spawned subagent, persona Shep |
| 4 | `step-04-inbox-and-calendar.md` | spawned subagent, persona Chief |
| 5 | `step-05-people-check.md` | spawned subagent, persona Shep |
| 6 | `step-06-set-priorities.md` | spawned subagent, persona Quinn |
| 7 | `step-07-social-tracker.md` | spawned subagent, persona Sterling |
| 8 | `step-08-eval-summary.md` | spawned subagent, persona `agents/master.md` |

Begin: `steps/step-01-wins-and-misses.md`

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

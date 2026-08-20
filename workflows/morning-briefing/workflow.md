---
name: morning-briefing
description: Start-of-day briefing - calendar, priorities, delegations, meeting context, and what needs attention today
agent: chief
model: sonnet
---

<!-- system:start -->
# Morning Briefing Workflow

**Goal:** Give the controller complete situational awareness for the day ahead in under 2 minutes of reading.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Sequential 4-step workflow. Each step gathers data from a different source, then the final step synthesizes into a single briefing. No user interaction required until the briefing is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity files | Current rocks, responsibilities, key people | Read identity layer files |
| Calendar | Today's meetings with attendees, times, locations | M365 MCP |
| Task management | Inbox count, due today, flagged items | Task management API |
| Delegation tracker | Overdue items, items due today | Read delegations/tracker.md |
| Knowledge layer | Recent meeting notes, previous daily review | Knowledge base API |

### Paths

- `identity_path` = `{project-root}/identity/`
- `delegation_tracker` = `{project-root}/delegations/tracker.md`
- `quarterly_objectives` = `{project-root}/memory/personal/quarterly-objectives.md`
<!-- system:end -->

<!-- personal:start -->
### Additional Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Clay | Upcoming reminders (next 7 days), upcoming birthdays, attendee relationship context | Clay MCP (mcp__clay__*) |
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

## WATCHTOWER INVOCATION

Before step-01, delegate the Watchtower daily awareness pipeline to Knox so its output is fresh for the briefing. Chief does NOT execute the gather steps directly — this is a hand-off.

1. Spawn Knox with the following payload: "Run the Watchtower daily workflow: `workflows/watchtower/workflow.md` — read this file first, run the STATE CHECK, and execute the full daily run (daily-step-01 through daily-step-07-prune through daily-step-06) as written. Return `watchtower_output`."
2. Knox executes the gather→dedupe→score→summarize→synthesize→capture→prune chain, writes the Obsidian daily note and dashboard (with through-line banner and consulting-read callout), and returns the result of `daily-step-06-report.md` as `watchtower_output`.
3. Store `watchtower_output` in this workflow's `accumulated-context`. The top 5 items by score (from `watchtower_output.scored_items`) are surfaced in the morning briefing Watchtower section (step-04).

If Knox fails to spawn or the Watchtower run produces no items above the awareness floor, note it and proceed. Do NOT let a Watchtower failure block the morning briefing.

## DATA SOURCE UNREACHABLE — MANDATORY CHECK

This workflow and any sub-workflow/agent it invokes (Chase's lead-review, Knox's Watchtower/plaud-ingest, etc.) touch data sources that live on the host Mac outside this session's bash mount — e.g. `My Leads.xlsx` and the Plaud transcript staging folder. Before any step reports one of these as "not accessible," "unreachable," or "no Mac filesystem access":

1. Run `ToolSearch` for `mcp__Desktop_Commander__*` and `mcp__Control_your_Mac__osascript` — these are frequently deferred and absent from the initial tool list, which is not evidence they're unavailable.
2. Only after confirming those tools are genuinely unavailable (or the path doesn't exist even via them) is it valid to report the source as unreachable.
3. See `err-20260715T134820-X2GOL2` for the specific failure this guards against — Master previously declared these sources unreachable without checking for Desktop Commander first.

## EXECUTION

Read fully and follow: `steps/step-01-gather-calendar.md` to begin the workflow.

**Guardrail checkpoint:** After step-03 (gather context) and before step-04 (synthesize), `steps/step-03b-guardrail-checkpoint.md` runs an automated review of the gathered data. `pass`/`flag` continue normally; `escalate` requires step-04 to open the delivered briefing with an explicit data-quality warning rather than silently presenting bad data as clean.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

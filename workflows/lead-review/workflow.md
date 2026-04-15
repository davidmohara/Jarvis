---
name: lead-review
description: Review David's lead tracker for unassigned leads (blank "Passed To" field) and surface them for Account Manager assignment. Runs during daily briefings and pipeline reviews.
agent: chase
model: sonnet
---

<!-- system:start -->
# Lead Review Workflow

**Goal:** No lead sits unassigned for more than a few days. If David generated it, someone should be running with it. This workflow catches the ones that slipped through.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 2-step workflow. Read the leads file, identify unassigned entries, surface them with context and urgency based on age.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| My Leads.xlsx | Full lead log — scan for blank "Passed To" entries | M365 MCP: `read_resource` with file URI |
| Calendar | Any upcoming meetings with unassigned lead companies | M365 MCP: `outlook_calendar_search` |
| Email | Recent threads with unassigned lead companies | M365 MCP: `outlook_email_search` |

### File Reference

- **File:** `My Leads.xlsx`
- **Location:** OneDrive → `Sales/My Leads.xlsx`
- **M365 File URI:** `file:///b!ilmQNHdRSEuxhG1Y66o6s2pUiIQPYJdBpYjAjbtZ8aRPj2M3V6pnT7CvN3AYbbdR/01ZA7BKHDIRSDTOJSU5JF2L2KUC4DMNJMF`

### Known Account Managers

Alexander Powell, Craig Fisher, Rod Patane, Mark Miesner, Diana Stevens, Vicki Kelly, Stephen Johnson, Derek Nwamadi.

### Triggers

This workflow fires:
- During the **daily briefing** (morning-briefing workflow) — Chase checks for unassigned leads as part of the revenue section
- During a **pipeline review** — after reviewing CRM, Chase checks the lead tracker
- On explicit request: "review my leads" or "lead review"
- The nag clock only starts AFTER a call/meeting has occurred with the lead — not from the log date

### Urgency Logic

**CRITICAL RULE:** The nag timer does NOT start when a lead is logged. It starts when David has had a call or meeting with the prospect. Before that call, the lead is simply "pending first contact" — no urgency, no nagging.

**Why:** Leads often sit in email ping-pong scheduling a first call. That's normal. The handoff decision happens after David qualifies the lead on a call, not before.

**How to detect post-call status:**
1. Check calendar for a past meeting with the lead company (`outlook_calendar_search` with `beforeDateTime: today`)
2. If no past meeting found, check email threads for signs a call happened (e.g., "great speaking with you", "following up on our call", meeting recap)
3. If neither found → lead is **Pre-Call** — do not nag

### Urgency Tiers (Post-Call Only)

| State | Label | Behavior |
|-------|-------|----------|
| No call yet | Pre-Call | No nag. Optionally mention: "[Client] — still scheduling first call." |
| 0–3 days post-call | Fresh | Mention in briefing: "You spoke with [Client] on [date]. Who gets it?" |
| 4–7 days post-call | Stale | Flag prominently: "[Client] call was [X] days ago. Still unassigned." |
| 8+ days post-call | Overdue | Push hard: "Sir, you talked to [Client] [X] days ago and nobody's running with it. Pick an AM or kill it." |
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

Read fully and follow: `steps/step-01-scan-leads.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
name: client-meeting-prep
description: Client/prospect meeting prep - email-first reason-for-call verification, attendee and company research, calibrated talking points, landmines
agent: chase
model: sonnet
---

<!-- system:start -->
# Client Meeting Prep Workflow

**Goal:** Walk into every external call knowing *why the meeting actually exists* — not why it looks like it exists. Web research and calendar metadata are supplements, never substitutes, for what the connected email account already knows about the relationship. No surprises. No invented sales narrative. No wrong titles.

**Agent:** Chase — Revenue, Pipeline & Client Strategy

**Architecture:** Sequential 5-step workflow.

1. **Identify the meeting** — logistics, attendees, verified local time.
2. **Establish ground truth from email** — query the connected email/calendar tool for the actual introduction or most recent thread with the attendee(s) BEFORE any web research. Classify the meeting type from that evidence.
3. **Research the company and attendee** — disambiguate company identity first, then build out company and bio context, calibrated to the classification from step 2.
4. **Build the prep sheet** — assemble the final deliverable in the canonical format. Pre-call only — no post-call action items.
5. **Generate PDF and deliver to reMarkable** — render the prep sheet to PDF and push it to David's tablet via Knox, using the hardened reMarkable delivery protocol.

No user interaction required until the prep sheet is delivered, except where a step's Failure Modes require surfacing an unresolved gap.

**Why this order matters:** This workflow was rebuilt on 2026-07-20 after a moderate-severity error (`err-20260720T144623-LSBA9A`) in which a prep sheet was built from web research and calendar data alone. The agent invented a sales-prospect narrative, misidentified the company (an acronym collision), and stated the wrong title for the attendee — all because the actual introduction email thread was never checked. The systemic fix: **email/calendar evidence is the source of truth for why a meeting exists; web research fills in identity and company context around that truth, never in place of it.**
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Required Input

- **Who**: Name of the external attendee(s) and/or their company
- **When**: Date and time of the meeting (if known, otherwise find it on calendar)

### Data Sources Required

| Source | What to Pull | Access Method | Priority |
|--------|-------------|----------------|----------|
| Email/Calendar connector | Meeting logistics, attendees, AND the introduction/most-recent thread with the attendee(s) | Connected email/calendar MCP tool per SYSTEM.md connector resolution (e.g., `mcp__1f6e0bda-36e0-456c-956f-abc8f14b8b8c__query_email_and_calendar` / `get_thread`, or M365 MCP `outlook_calendar_search` when authorized) | **First — mandatory, run before web research** |
| Local system clock | Ground truth for the Mac's actual local time and timezone | `osascript` `date` command via Desktop Commander or Control_your_Mac | First — before stating any meeting time |
| CRM | Prior opportunity/account history if the company already exists as a client | CRM via Chrome/M365 auth, if a connector is active | Second |
| Web | Company profile, attendee bio, LinkedIn, recent news | Web search | Second — supplements, never substitutes for email evidence |
| Knowledge layer | Past meeting notes, relationship history, prior prep docs for this person/company | Knowledge base API / Obsidian | Second |

### Output

- Prep sheet saved to knowledge layer / working directory: `{Person Name} — {Company} — {YYYY-MM-DD}.md`
- Clean markdown starting directly with the H1 title — **no YAML frontmatter block** in the deliverable itself (the workflow's own step files carry frontmatter; the output document does not).
- **No "Next Steps" or post-call action item section.** This is a pre-call prep sheet. It does not presume outcomes.
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
   - Notify the controller: "[Chase]: Resuming client-meeting-prep from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Chase]: client-meeting-prep was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow, in order:

1. `steps/step-01-identify-meeting.md`
2. `steps/step-02-source-of-truth-email.md`
3. `steps/step-03-research-company-and-attendee.md`
4. `steps/step-04-build-prep-sheet.md`
5. `steps/step-05-remarkable-delivery.md`

Each step file names the next step at its end. Do not skip ahead — step 2's classification output gates the tone and content of steps 3 and 4.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

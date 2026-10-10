---
name: email-drafting
description: Draft professional emails calibrated for recipient, relationship, context, and the controller's voice
agent: harper
model: sonnet
---

<!-- system:start -->
# Email Drafting Workflow

**Goal:** Produce a draft email the controller can send with zero or minimal edits. Every draft must match the controller's natural writing style and specific formatting conventions.

**Agent:** Harper -- Storyteller, Communication, Content & Thought Leadership

**Architecture:** Interactive 3-step workflow. Clarify context (ask only for what was not provided), draft the email (enforcing the controller's voice profile), then iterate until approved and route to delivery. User interaction required at each step.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity layer | Voice profile, email conventions, formatting rules | Read identity/VOICE.md |
| CRM | Recipient context, relationship history, account status | CRM |
| Calendar | Related meetings, upcoming events with recipient | M365 MCP |
| Knowledge layer | Relationship history, previous communications, context notes | Knowledge base API |
| M365 Email | Recent email threads with recipient (for tone matching and thread context) | M365 MCP |

### Controller's Email Style Conventions

Loaded from `identity/VOICE.md` at the start of every drafting session. Always re-read the voice file for the current conventions; do not rely on a cached copy here.

### Output

- Draft email presented to the controller for review
- Upon approval: routed to email client for delivery, or presented for manual send
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

Read fully and follow: `steps/step-01-clarify-context.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

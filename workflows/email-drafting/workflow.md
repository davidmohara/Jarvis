---
name: email-drafting
description: Draft professional emails calibrated for recipient, relationship, context, and the controller's voice
agent: harper
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

### Why This Exists

Email is the most frequent external communication the controller produces. Getting the voice wrong -- even slightly -- breaks trust, creates rework, and wastes time. This workflow exists to guarantee that every draft:

1. Matches the controller's natural writing style (loaded from identity layer)
2. Is calibrated for the specific recipient and relationship
3. Follows the controller's exact formatting conventions
4. Has a clear purpose and call to action
5. Can be sent with zero or minimal edits

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity layer | Voice profile, email conventions, formatting rules | Read identity/VOICE.md |
| CRM | Recipient context, relationship history, account status | CRM |
| Calendar | Related meetings, upcoming events with recipient | M365 MCP |
| Knowledge layer | Relationship history, previous communications, context notes | Knowledge base API |
| M365 Email | Recent email threads with recipient (for tone matching and thread context) | M365 MCP |

### Controller's Email Style Conventions

These are loaded from `identity/VOICE.md` at the start of every drafting session. The conventions below are the current known rules -- **always re-read the voice file in case they have been updated:**

| Convention | Rule |
|------------|------|
| Em-dashes | Never. Use hyphens instead. |
| Blank lines above greeting | None. Greeting starts immediately. |
| Greeting to body | One blank line between greeting and body. |
| Between body paragraphs | One blank line. |
| Body to closing | Two blank lines between last body paragraph and closing. |
| Closing style | "Thanks," / "Take care," / "Have a great weekend," -- always with a comma. |
| Sign-off name | No name when email signature is pre-populated. |
| Length | Clean and tight. No padding. No filler. |
| Formality | Calibrate per recipient and context. Default to professional-warm. |

### Output

- Draft email presented to the controller for review
- Upon approval: routed to email client for delivery, or presented for manual send
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-clarify-context.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

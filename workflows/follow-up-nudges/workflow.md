---
name: follow-up-nudges
description: Surface overdue delegations and draft calibrated follow-up messages from gentle reminder to escalation
agent: shep
model: sonnet
---

<!-- system:start -->
# Follow-Up Nudges Workflow

**Goal:** Surface every overdue delegation and stale commitment, then draft a follow-up message at the right tone. No dropped balls. No heavy-handed accountability.

**Agent:** Shep — People, Delegation & Development

**Architecture:** Sequential 3-step workflow. Identify overdue and stale items, draft tone-calibrated messages, present for executive review and send (or hand off to Harper for polish).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management / Delegation tracker | All overdue delegations, stale commitments | Task management API |
| Knowledge layer | Relationship context, past patterns, prior follow-up history | Knowledge base API |

### Tone Calibration Levels

Defined in shared-definitions.md. Tone escalates based on how many days overdue:

| Level | Trigger | Style |
|-------|---------|-------|
| Level 1 — Gentle reminder | 1-3 days overdue | Friendly check-in, assumes good intent |
| Level 2 — Firm follow-up | 4-7 days overdue | Direct request for update with deadline restatement |
| Level 3 — Escalation | 8+ days overdue OR 2+ prior nudges ignored | Formal tone, states impact, requests immediate response |

**Seniority adjustment:** Nudges to superiors cap at Level 2 unless the executive explicitly escalates. Nudges to direct reports use all 3 levels.

**Relationship adjustment:** Pull relationship context from the knowledge layer. A person with a history of late deliverables warrants firmer tone sooner than someone who is reliably on time.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-identify-overdue.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

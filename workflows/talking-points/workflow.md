---
name: talking-points
description: Talking points generator — produce crisp, voice-calibrated talking points tailored by event type with anticipated Q&A and knowledge layer sourcing
agent: harper
model: sonnet
---

<!-- system:start -->
# Talking Points Workflow

**Goal:** Generate crisp, ready-to-use talking points the executive can deliver with confidence. Every point is voice-calibrated, evidence-backed, and formatted for the specific event context.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 3-step workflow. Analyze context and event type → generate points with evidence, phrasing, and anticipated questions → format output for specific context (meeting, panel, media, internal).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Event Types and Output Formats

| Event Type | Format | Output Rules |
|------------|--------|-------------|
| `meeting` | 3-5 bullet points | Concise, action-oriented, direct |
| `panel` | 1-minute structured points with bridge phrases | Memorable, quotable, time-bounded |
| `media` / `podcast` | Key messages with anticipated Q&A and pivot techniques | On-message, defensible, prepared |
| `internal-comms` | Narrative with key themes | Transparent, motivating, values-aligned |

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity layer | Voice profile, communication style, executive position on key topics | Read `identity/VOICE.md` |
| Knowledge layer | Relevant context, past statements, key themes, expertise areas | Knowledge base API |
| Agent domains | Domain-specific data: Chase (revenue), Quinn (strategy), Shep (people), Chief (operations) | On-demand per event context |
| Calendar | Event details, audience, context | M365 / Google Calendar |

### Paths

- `voice_file` = `{project-root}/identity/VOICE.md`
- `knowledge_layer` = `{project-root}/context/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-context-analysis.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

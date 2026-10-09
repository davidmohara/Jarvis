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
- `knowledge_layer` = `{project-root}/memory/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-context-analysis.md` to begin the workflow.

After step-03 formats and delivers the points, run `steps/step-04-adversarial-verify.md`, the terminal adversarial verification step. It spawns **Ralph** with `workflows/talking-points-verification/workflow.md` (the points-traced-to-source-strategy-and-notes lens). Ralph traces each delivered point back to a real source and returns a verdict table; the result is recorded as an `adversarial-verification` guardrail checkpoint. The workflow is marked complete only at the end of step-04.

**Deterministic step guardrails:** Every step transition is machine-checked. The verifiers in `workflows/talking-points/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

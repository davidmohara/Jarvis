---
name: presentation-builder
description: Presentation builder — convert any source material (talking points, outlines, strategy docs, raw ideas) into a polished slide-by-slide text structure calibrated to the executive's voice
agent: harper
model: sonnet
---

<!-- system:start -->
# Presentation Builder Workflow

**Goal:** Transform source material of any quality into a slide-by-slide presentation structure the executive can use immediately. No blank slides, no generic AI voice. Output is structured text — not PowerPoint files or actual slide formats.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 4-step workflow. Load and parse source material → calibrate executive voice → structure slide-by-slide output → handle incoming handoffs from Chase or Quinn with domain context.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Accepted Input Formats

Harper accepts source material in any of these formats:

| Format | Description |
|--------|-------------|
| Talking points | Bullet list of key messages, any level of polish |
| Outline | Structured outline with sections and sub-points |
| Strategy document | Formal or informal strategy doc with objectives and context |
| Raw ideas | Unstructured thoughts, brain dump, or rough notes |
| Cross-agent handoff | Structured context package from Chase (client meeting) or Quinn (leadership) |

### Output Contract

- Output is **slide-by-slide text structure** — title, key point, supporting content, speaker notes, and visual suggestion per slide
- No actual slide files (.pptx, .key, .gslides) are produced
- Voice must match the executive's profile from `identity/VOICE.md`
- Narrative arc: hook → context → evidence → call to action

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Identity layer | Executive voice profile, communication style, tone preferences | Read `identity/VOICE.md` |
| Knowledge layer | Relevant context, past talks, key themes, expertise areas | Knowledge base API |
| Handoff context | Domain-specific data from Chase or Quinn if applicable | Handoff payload |

### Paths

- `voice_file` = `{project-root}/identity/VOICE.md`
- `knowledge_layer` = `{project-root}/context/`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-load-source-material.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---
source: whiteboard-extraction (photo only, no transcript)
date: 2026-08-03
meeting: Systemic Compliance — IMS Architecture Whiteboard Session
location: Improving Involvement office (photographed on branded glass whiteboard)
attendees:
  - David O'Hara (Improving)
  - Ben Kennedy (Improving)
tags: [systemic-compliance, ims, sc-orb, architecture, whiteboard]
extracted: 2026-08-03
status: draft — several handwritten labels only partially legible, confirm with Ben
---

# Systemic Compliance — Aug 3 IMS Architecture Whiteboard

**Session:** David + Ben, technical working session on SC.IMS architecture
**Goal (per David):** design the structure SC.IMS will live in so it can become a full-blown product and be surfaced well in SC.ORB for all customer segments
**Source:** Single whiteboard photo (no Plaud transcript this time) — this note and the accompanying diagram are a best-effort read of the handwriting, not a verbatim transcript. Treat anything flagged below as unconfirmed until Ben validates it.

---

## How this connects to prior sessions

This is a technical deep-dive on exactly the question the Jul 8 whiteboard and the SC.IMS/SC.ORB briefing left open in the "IMS + SC.ORB relationship" bucket: **does the requirements graph feed ORB, or are they two products?** This session starts answering that at the infrastructure level — ingestion, model/agent routing, data stores, and how it all surfaces through ORB's front-ends.

It also lines up directly with briefing §5 ("How SC.IMS and SC.ORB fit together"), which named the exact engines that need productizing: the linkage graph as ORB's requirements backbone, the MOC ripple engine as the MOC module, Competence Architect as the training/LMS engine, and peer-benchmarking as a data product. Nothing on this whiteboard contradicts that — it's the "how" underneath it.

---

## What's on the whiteboard

**Two decision points (top left):**
1. **Versioned, Gated Ingest** — described as "ongoing," so this one is already decided/underway, not the live discussion
2. **Move Playground** — this is the actual live decision point being worked through in this session: the sandbox-to-promotion flow (exact promotion criteria not yet defined — confirm with Ben)

**Ingest layer:** Claude-driven ingest of PDF / XLS / MD / JSON documents, including operator CWFs/SOWs, using MCP/skills tooling.

**IMS — this whole block is the SC.IMS eval harness (confirmed by David).** The still-missing eval harness (the 4-hour committed bucket from the Jul 8 allocation) now has a concrete design. IMS is a component that combines a routing/agent layer with the data layer underneath it:

*Routing layer* — a gateway (**OpenRouter / Concentrate.ai** — not Claude.ai as first read; Concentrate.ai is the AI-governance/spend-control vendor David met with separately, per `meetings/2026-06-30-concentrate-ai.md`) routes into three lanes:
- **Eval & Golden** — the eval-harness pass/fail happens here; only what clears it is called client-facing/production ("Golden")
- **Sentinels & Governance / Security** — monitoring/guardrail agents enforcing access and security policy across the pipeline
- **Agents & Behaviors** — the working agent layer: task-specific agents and their defined behaviors

*Data layer sits underneath the three routing lanes* (not beside them, as first drawn) — 4 data stores:
- Vector (embeddings/similarity)
- Relational (entities/typed links — matches the ~750-entity, ~1,066-link regulatory graph from the briefing)
- Semantic
- RAG / Document Store

A "Discovery" question sits with this layer: *"How does data relate?"* — this is the regulatory-linkage/crosswalk engine from the briefing, described here at the data-architecture level rather than the business level.

**SC.ORB surface layer:** A central ORB hub with multiple front-end ("FE") spokes — directly answering David's "surfaced well in ORB for all customer segments" goal. Two named segments: **Customers** and **Consultants**, both described as being built via **Loveable** (the AI app-builder). Hosting: Cloudflare + AWS, split not yet finalized.

---

## Architecture diagram

A cleaned-up interpretation of the whiteboard is saved alongside this note:
- `2026-08-03-ims-architecture-diagram.svg`
- `2026-08-03-ims-architecture-diagram.png`

Flow: **Sources → Ingest (① Versioned/Gated — decided; ② Move Playground — the live decision point) → IMS (= the SC.IMS eval harness: gateway OpenRouter/Concentrate.ai → Eval & Golden / Sentinels & Governance-Security / Agents & Behaviors, sitting on top of the 4-store data layer) → SC.ORB (multiple front-ends for Customers and Consultants, built via Loveable, hosted on Cloudflare + AWS)**.

---

*Extracted by Jarvis · 2026-08-03 · Source: single whiteboard photo, no transcript. Cross-referenced against `2026-07-08-whiteboard-notes.md`, `2026-07-10-synthesis-committed-outcomes.md`, and `client docs/SC_Improving-Briefing_SC.IMS-and-SC.ORB_Summary_2026-07-08.docx`.*

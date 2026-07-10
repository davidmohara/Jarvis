---
source: whiteboard-extraction + plaud-transcript
date: 2026-07-08
meeting: Systemic Compliance — Whiteboard Session
location: Improving Plano — Dallas Classroom
attendees:
  - David O'Hara (Improving, Regional Director / Fractional AI Officer)
  - Ben Kennedy (Improving)
  - Kevin Graham (Systemic Compliance, kgraham@systemic-compliance.com)
  - Robin Graham (Systemic Compliance, rgraham@systemic-compliance.com)
  - Mehmet Yasar (Systemic Compliance, myasar@systemic-compliance.com)
duration: ~119 min (approx. 10:05–11:58 CDT)
tags: [systemic-compliance, ims, sc-orb, advisory, whiteboard, transcript]
extracted: 2026-07-10
---

# Systemic Compliance — July 8 Whiteboard Session

**Session:** Wednesday, July 8, 2026 · ~10:05–11:58 CDT (~119 min)
**Location:** Improving Plano — Dallas Classroom
**Source:** Whiteboard images (IMG_6315, IMG_6316) + Plaud transcript

---

## Summary

Full whiteboard session to map Systemic Compliance's AI-native platform architecture, define GTM options, and align Improving's advisory role. Kevin Graham has spent months building a deep compliance AI toolkit using Claude. This is the first formal session to structure that work into a coherent product with governance and commercial strategy.

The session opened with Robin and Kevin surfacing frustrations about their developer Mehmet (Matt) — technically capable but operating independently and resisting direction. The team decided: Improving works directly with Kevin and Robin on architecture; Mehmet will be part of some conversations but won't set direction. Kevin is the product visionary; Robin is the organizational conscience.

Kevin then walked through three pillars of his AI-native compliance platform, all built on Claude: Compliance Architecture, Competence System, and Gap Analysis. David's key flags: (1) data governance — operators' procedures are being used to build training content without explicit agreements; (2) GTM risk — SC is at risk of becoming a "Cheesecake Factory menu" with too many undifferentiated capabilities.

---

## Situation: Developer / Governance

Mehmet has been building sc.ims independently. His work is technically solid but not integrated with Kevin's vision, and he resists direction.

**Decision made:** Kevin and Robin will be in every significant conversation with Improving. David to set up a separate technical deep-dive with Mehmet to assess architecture and gaps. Mehmet reports in, not out.

> *"We wanted to have this conversation because we're a little uncomfortable with you guys talking to Matt directly and Matt running off in some direction." — Kevin Graham*

> *"Want him to be involved in every conversation, but we want to be part of every conversation." — Robin Graham*

---

## Platform Architecture — Three Pillars

### 1. Compliance Architecture (Regulatory Linkage)

Kevin's core data layer: sourcing, parsing, and crosswalking regulatory requirements.

**Sources of truth:**
- eCFR (federal regulations)
- State agency websites (state-level regs)
- Consensus standards authors (published update cycles)

**How it works:**
- Hallucination risk is low — system references documents rather than generating requirements
- NPRM pickup flow: delta changes enter eCFR on finalization → tracked automatically
- Update cycle: NPRM → 90-day comment period → 6-month implementation window

**IMS capabilities in this layer (from whiteboard):**
- Collect all requirements — Federal, State, Stringency levels
- Consensus Standards
- Findings & Interpretations
- Audit Protocols / Answers (generated)
- Equipment Requirements
- OSHA Requirements
- Task Required
- Excel Spreadsheet / DB (ORB)
- Skills — Crosswalk / Changelog, Calendaring
- Sources → Inputs

---

### 2. Competence System (Competence Architect)

Takes an operator's O&M procedures + anonymized training corpus + regulatory requirements and generates training materials in four formats.

**Four output formats:**
1. Instructor-led course — lesson plan + student handouts
2. OJT (on-the-job training record document)
3. Self-study guide
4. CBT / SCORM-ready package — production-ready in ~10 minutes

**Packaging formats supported:** xAPI, CMI, SCORM (covers different operator LMS standards)

**Competence and Progression Framework (CPF):**
Tells any operator exactly what training courses should be in their library and available to contractors — regulatory-driven and PSMS-driven.

**SC.org LMS integration:** SCORM output supports SC-hosted delivery (to contractors via SC.org) and client-hosted (behind own firewall). LMS integration makes training delivery a compliance record.

**Whiteboard items in this layer:**
- Design Training Requirements
- Build Training (Higgsfield) → LMS (ORB)
- CPF — Competence Progression Framework
- Skill — Content Creation, Requirements Design
- Existing Corpus of Training = Data Source

> *"I can in minutes, tell a client, you better have all of these courses in your training library." — Kevin Graham*

---

### 3. Gap Analysis

Reads operator documents (O&M procedures, integrity management programs) against regulatory requirements and outputs gaps with severity context and peer benchmarking.

**Whiteboard items:**
- Map Client Doc against Regs
- Identify Gaps
- Benchmark across peers for recommendations
- Due Diligence for M&A
- Sources: National Safety Council
- Skills: Gaps Analysis — Doc / Audit Log, Audit Prep (RL) & Training

**Peer benchmarking note:** Corpus is all pipeline operators, no differentiation by size/type, anonymized. Scope of "peers" should be defined more precisely before scaling.

---

### 4. MOC Ripple (Management of Change)

Predicts downstream consequences of regulatory or operational changes.

**Capabilities:**
- Predict up/downstream impacts
- Ripple Map & Audit Trail Dossier
- Legal Compliance tracking
- Folder per engagement: Client Docs (Templates), Changelog
- Skills — Doc Updates, Gap Analysis
- Partners: Emergency Services, Staffing / Resourcing

---

### 5. Panama Canal Placer

Market intelligence / lead generation tool — identifying and qualifying compliance-adjacent opportunities.

- Job Listings — Compliance Positions → Sales Funnel
- Posting Findings — LinkedIn, A.Reg, Conferences

---

## Regulatory Framework Reference

Structural underpinnings of the requirement database:

- **PSMS** — Process Safety Management System
- **OSHA-PSM** — OSHA Process Safety Management standard
- **ISO 14001 / 9001** — Environmental and Quality Management Systems

---

## Key Issues Surfaced

### Data Governance Risk (David's flag — HIGH)

Kevin has built a corpus from operators' training programs and procedures — anonymized but **not yet covered by explicit data use agreements**. Operators' procedures are being used to generate training content for other operators.

> *"Do you have agreements with them that say you're allowed to do that? No, okay, not yet. That's the okay. I don't want to get us in trouble here where it was like 'Oh, we took your stuff. And we trained our stuff on your stuff.' OpenAI does that, they all do that. I get it. But yeah, that's one that I would flag." — David O'Hara*

This needs to be formalized with legal review before SC scales.

---

### GTM Complexity — "Cheesecake Factory" Problem (David's flag — HIGH)

SC now has at least five distinct product capabilities:
1. Contractor management (SC.org)
2. Compliance architecture
3. Competence / training system
4. Gap analysis
5. Due diligence for acquisitions / M&A

> *"That's what's getting crazy about this — even trying to go and market this. You don't want it to be the Cheesecake Factory menu." — Robin Graham*

> *"If you are all things to all people, you are nothing." — David O'Hara*

**Three entry points identified:**
1. **Project-based consulting** — one-and-done gap analysis, due diligence
2. **Co-source consulting** — ongoing compliance team augmentation, recurring revenue
3. **SC.org SaaS** — contractor management as the landing page, upsell into consulting

Decision not finalized in session — needs further work.

---

## 16-Hour Advisory Plan — Agreed Allocation

Agreed on the whiteboard (total = 16 hours, Q3 2026):

| Hours | Work Area |
|-------|-----------|
| 4 | IMS Review + Eval Harness Design |
| 5 | IP Portability & Governance Baseline |
| 2 | SC.ORB Deep Dive |
| 2 | Path A/B Strategy / Decision |
| 2 | Data Room Work & Narrative |
| 1 | Q3 Gate & Misc |
| **16** | **Total** |

---

## Action Items

- [ ] **David** — Set up technical deep-dive with Mehmet on sc.ims architecture; identify gaps and integration needs
- [ ] **Kevin** — Formalize data use agreements with operators before scaling training corpus; flag for legal review
- [ ] **David + Kevin** — Define 1–2 primary GTM entry points (due diligence vs. gap analysis vs. co-source); create focused pitch
- [ ] **Robin** — Scope co-source consulting model as recurring revenue offer — what does the annual engagement look like?
- [ ] **Mehmet** — Confirm xAPI/CMI/SCORM packaging output formats are production-ready for SC.org LMS integration
- [ ] **David** — Develop fractional AI officer engagement playbook section for compliance-vertical clients

---

## Open Strategic Questions

- **Path A vs. Path B** — build a 10-year annuity or sell in ~4 years. M&A attorney and IP attorney are both active. Still open.
- **IMS + SC.ORB relationship** — two products, one platform, or does IMS's requirement graph feed ORB? The hinge architectural question. Needs the Matt deep-dive session.
- **Commercial status** — paying clients on IMS? Pilot agreements live? Not confirmed in session.
- **Regulatory timing forcing event** — API RP 1173 management-system framework expected mandatory in 3–4 years. Is this the primary forcing event, or is there something shorter-term?

---

*Extracted by Jarvis · 2026-07-10 · Sources: IMG_6315.JPG, IMG_6316.JPG, Plaud transcript (zzPlaud/Client/2026-07-08)*

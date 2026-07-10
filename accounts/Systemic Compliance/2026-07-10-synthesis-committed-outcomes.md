---
type: synthesis
account: Systemic Compliance
date: 2026-07-10
sources:
  - accounts/Systemic Compliance/2026-07-08-whiteboard-notes.md (Jul 8 whiteboard, full transcript extraction)
  - Jul 9 Orb Platform Demo (Mehmet Yasar walkthrough) — working-memory summary only; full transcript unavailable this session (Obsidian vault and Chrome unreachable)
  - accounts/Systemic Compliance/2026-06-30-call-prep.md
  - accounts/Systemic Compliance/Systemic Compliance.pdf (kickoff meeting-at-a-glance)
  - accounts/Systemic Compliance/client docs/SC_Improving-Briefing_SC.IMS-and-SC.ORB_Summary_2026-07-08.docx
  - reference/CAIO-Execution-Playbook.md (committed 90-day exit criteria, §5)
status: draft — Orb demo section based on summary, not full transcript
---

# Systemic Compliance — Synthesis: What We've Heard (through July 9)

## Why this note exists

Two sessions in six weeks — the July 8 whiteboard and the July 9 Orb platform demo — gave us the first real look at what Systemic Compliance (SC) has actually built, versus what the kickoff call and SC's own briefing said they'd built. This note lines up what we heard against what we committed to, so nothing said in the room gets lost before it becomes roadmap or a board/gate narrative.

**One caveat up front:** the Orb demo section below is built from a working-memory summary, not the full transcript — the vault and browser tools I'd normally pull the transcript from weren't reachable this session. Treat those details as directionally right, not quote-level accurate, until confirmed against the actual recording.

---

## What we committed to (the baseline we're measuring against)

No standalone signed proposal document exists for this account — the commitment is defined by three things:

1. **The SOW terms** (call-prep, kickoff): 16 advisory hours over Q3 2026, quarterly retainer, fractional CAIO role. Sourced Devlin Liles → Robyn Fuentes → Stephen Johnson → David.
2. **The 16-hour allocation agreed on the whiteboard** (supersedes the pre-kickoff draft split in call-prep):

   | Hours | Work Area |
   |---|---|
   | 4 | IMS Review + Eval Harness Design |
   | 5 | IP Portability & Governance Baseline |
   | 2 | SC.ORB Deep Dive |
   | 2 | Path A/B Strategy / Decision |
   | 2 | Data Room Work & Narrative |
   | 1 | Q3 Gate & Misc |

3. **The playbook's standard 90-day exit criteria** (`reference/CAIO-Execution-Playbook.md` §5): strategy + roadmap approved, governance baseline signed off, ≥2 pilots live and instrumented, board narrative v1 delivered, monthly + quarterly gates each run once. SC is a compressed case — the "16 hours" bucket described above stands in for the usual weekly cadence.

SC's own framing (from their internal briefing to us) adds a fourth lens: they explicitly asked for our guidance on (1) integration architecture — folding SC.IMS's engines into SC.ORB, (2) go-to-market positioning, (3) maximizing enterprise value / exit optionality, and (4) AI architecture, including a path to a closed or hybrid private AI environment. Anything we deliver should trace back to one of these four asks.

---

## What we heard — mapped to committed outcomes

### 1. IMS Review + Eval Harness Design (4 hrs committed)

**Heard:** Kevin walked the whiteboard through three core IMS pillars — Compliance Architecture (regulatory linkage/crosswalk), Competence System (four training output formats, CPF), and Gap Analysis (doc-vs-reg mapping, peer benchmarking) — plus two adjacent capabilities, MOC Ripple and a market-intel tool ("Panama Canal Placer"). Hallucination risk in the linkage engine is described as low because the system references source documents rather than generating requirements from memory — but there is still no independent evaluation harness, which is exactly what Devlin's roadmap (step 4) flagged as missing.

**Status against commitment:** On track to be scoped, not yet started. No eval harness work has begun; this is still the largest open gap and the one with the most sales/defensibility value (per Devlin's original diagnosis — the harness is "the sales weapon").

**Not yet confirmed:** whether any of this has been tested against real edge cases, or whether SME reviewers are tracking kickback rates (the "cognitive surrender" risk from the original roadmap).

### 2. IP Portability & Governance Baseline (5 hrs committed)

**Heard (whiteboard):** Two governance risks surfaced directly from Kevin and Robin, not from us:
- **Data governance (David flagged HIGH):** Kevin's training corpus is built from operators' own procedures — anonymized, but with no explicit data-use agreements in place. This is a live legal exposure, not a hypothetical one; action item assigned to Kevin to formalize before scaling further.
- **Developer governance:** Mehmet (Matt) Yasar has been building SC.IMS/SC.ORB somewhat independently of Kevin's architecture vision and resists direction. Kevin and Robin want to be in every Improving conversation going forward; Mehmet reports in, doesn't set direction. This is a governance-of-the-build problem sitting on top of the governance-of-the-data problem.

**Heard (Orb demo, per summary):** Mehmet walked through the live platform (~72 min) — multi-tenant architecture, OQ module, SCIMS integration, MVP compliance features. Two technical flags surfaced: the current email domain hosting setup creates an audit-trail liability, and the Orb Assistant is currently running on the Gemini API, which should be assessed for a swap to Claude (consistent with SC's own stated preference to build on Claude/Cowork and with Improving's standard stack guidance).

**Status against commitment:** This bucket is now the most active. The whiteboard produced concrete next steps (deep-dive with Mehmet, legal review of data-use agreements) but no governance baseline document exists yet. The Gemini-vs-Claude question is a new, specific decision point that should get its own line item rather than being folded silently into "governance."

### 3. SC.ORB Deep Dive (2 hrs committed)

**Heard:** The July 9 demo is effectively the start of this bucket, ahead of schedule relative to the whiteboard's plan to hold it as a separate session with Mehmet. Deliverables coming out of it: Mehmet to share technical documentation and GitHub access; David to follow up with Kevin on Thursday or Monday.

**Status against commitment:** In progress, running slightly ahead of the allocation sequence (whiteboard treated this as a later, separate session; it happened the next day instead).

### 4. Path A/B Strategy Decision (2 hrs committed)

**Heard:** Still explicitly open on both sides. The whiteboard reconfirmed the fork from the original roadmap — Keep & Scale (10-year annuity, moat depends on peer benchmarking + equivalency engine getting stronger with more operators) vs. Harvest IP (sell into 15-20 midstream operators inside ~4 years before knockoffs appear). M&A and IP attorneys are both already active on SC's side, which is new information since the kickoff — this decision has commercial urgency behind it now, not just strategic interest.

**New wrinkle surfaced on the whiteboard, not previously flagged:** a go-to-market complexity problem layered on top of the strategic fork. SC now spans five distinct product/service lines (contractor management, compliance architecture, competence/training, gap analysis, M&A due diligence). Robin named the risk directly — "you don't want it to be the Cheesecake Factory menu" — and three narrower entry points were proposed (project-based consulting, co-sourced consulting, SC.ORB SaaS) but not decided. This needs to be resolved before or alongside Path A/B, not after — a diffuse GTM story undermines either exit path.

### 5. Data Room Work & Narrative (2 hrs committed)

**Heard:** Nothing specific yet from either session; SC's own briefing document (prepared for the July 8 meeting) is effectively an early data-room artifact — it lays out SC.IMS as a stack of separable IP assets (linkage engine, MOC ripple, Competence Architect, CPF, peer-benchmarking corpus) and SC.ORB as 65 features across 18 business areas (35 built, 8 in progress, 22 planned), plus commercial terms ($98/records-bearing worker/year plus a banded platform license, ~$70K/year representative operator baseline).

**Status against commitment:** Not started as a working session, but the raw material for it already exists in SC's own briefing — this bucket may take less incremental time than budgeted if we build directly on what they handed us rather than starting from scratch.

### 6. Q3 Gate & Misc (1 hr committed)

**Not yet run.** No gate has happened since kickoff. Given the pace of what's surfaced in two sessions (governance risk, developer friction, GTM complexity, a live model-vendor decision), there's a case for pulling the first informal gate forward rather than waiting for a natural end-of-quarter checkpoint — several of these items (data-use agreements, Mehmet's role, Gemini/Claude) have their own urgency independent of the calendar.

---

## Decisions made (not just discussed)

- Kevin and Robin will be in every significant Improving conversation; a separate technical deep-dive with Mehmet is being set up, but Mehmet does not set direction unilaterally.
- The 16-hour allocation above is the agreed version of record — treat call-prep's draft split as superseded.

## Open items carried forward (owner noted where known)

- [ ] **Kevin** — formalize data-use agreements with operators before scaling the training corpus; flagged for legal review.
- [ ] **David** — set up the Mehmet technical deep-dive on SC.IMS/SC.ORB architecture.
- [ ] **David + Kevin** — pick 1-2 primary GTM entry points and build a focused pitch (the "Cheesecake Factory" problem).
- [ ] **Robin** — scope the co-source consulting model as a recurring-revenue offer.
- [ ] **Mehmet** — confirm xAPI/CMI/SCORM packaging is production-ready for SC.org LMS integration; share tech docs and GitHub access.
- [ ] **David** — follow up with Kevin (Thursday or Monday, per Orb demo).
- [ ] **Unconfirmed/needs decision** — assess swapping the Orb Assistant off Gemini onto Claude; resolve the email-domain-hosting audit liability.
- [ ] Path A vs. Path B — still open; M&A/IP counsel active on SC's side.
- [ ] IMS + SC.ORB architectural relationship (does the requirements graph feed ORB, or are they two products) — needs the Mehmet deep-dive to resolve.
- [ ] Commercial status of IMS (paying clients, live pilots) — not confirmed in either session.

## Risks to carry into the next gate

1. **Data governance / IP provenance** — training corpus built on operator procedures without signed use agreements. High severity, David already flagged it directly in-session.
2. **Developer/founder misalignment** — technically strong build work (Mehmet) running ahead of or apart from the vision it's supposed to serve. Left unmanaged, this becomes an execution-track governance failure, not just an interpersonal one.
3. **GTM over-diversification** — five product lines with no chosen entry point risks diluting the pitch to any single buyer type, whether the exit is Keep & Scale or Harvest IP.
4. **Model/vendor lock-in** — Orb Assistant on Gemini cuts against SC's own stated preference for Claude/Cowork and against a clean, single-vendor governance story; worth resolving early rather than letting it become sunk-cost infrastructure.
5. **Trapped IP** (carried forward from the original roadmap, still unresolved) — SC.IMS still lives inside a Cowork seat; every strategic path requires extracting it first, and no extraction work has visibly started yet.

---

*Prepared by Jarvis, 2026-07-10, for David O'Hara. Sources listed above. Orb demo detail should be confirmed against the full transcript when vault/browser access is available.*
